"""
models/financial.py
Financial model: IRR / NPV / Payback + policy-adjusted financials + Monte Carlo.
"""
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# ── Base assumptions ─────────────────────────────────────────────────────
INSTALL_MW      = 10
CAPEX_PER_MW    = 4_50_00_000   # ₹4.5 Cr/MW
OPEX_PER_MW_YR  = 15_00_000     # ₹15L/MW/yr
DISCOUNT_RATE   = 0.10
PROJECT_YEARS   = 20
DEGRADATION     = 0.005
PERF_RATIO      = 0.76          # industry standard PR
MC_ITERATIONS   = 1_000


def _solar_yield_mwh_per_mw(ghi: float) -> float:
    """Annual MWh yield per MW installed."""
    return round(ghi * 365 * PERF_RATIO * 1000 / 1000, 1)  # = GHI×365×PR kWh/kWp → MWh/MW


def _irr_bisection(cash_flows: list) -> float:
    """Robust IRR via bisection search."""
    def npv_at(r):
        return sum(cf / (1 + r) ** t for t, cf in enumerate(cash_flows))
    if npv_at(0.001) <= 0:
        return 0.0
    lo, hi = 0.001, 5.0
    for _ in range(80):
        mid = (lo + hi) / 2
        (lo if npv_at(mid) > 0 else hi).__class__  # dummy; real update below
        if npv_at(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _build_cash_flows(capex, annual_mwh, tariff, opex_annual):
    cfs = [-capex]
    for yr in range(1, PROJECT_YEARS + 1):
        energy = annual_mwh * (1 - DEGRADATION) ** (yr - 1)
        revenue = energy * 1000 * tariff
        cfs.append(revenue - opex_annual)
    return cfs


def _npv(cash_flows):
    return sum(cf / (1 + DISCOUNT_RATE) ** t for t, cf in enumerate(cash_flows))


def _payback(cash_flows):
    cum = 0
    for t, cf in enumerate(cash_flows):
        cum += cf
        if t > 0 and cum >= 0:
            return t
    return None


def compute_base_financials(state_df: pd.DataFrame) -> pd.DataFrame:
    """Compute IRR, NPV, Payback for each state at base assumptions."""
    records = []
    for _, row in state_df.iterrows():
        annual_mwh = _solar_yield_mwh_per_mw(row["solar_ghi_kwh_m2_day"]) * INSTALL_MW
        capex      = INSTALL_MW * CAPEX_PER_MW
        opex       = INSTALL_MW * OPEX_PER_MW_YR
        cfs        = _build_cash_flows(capex, annual_mwh, row["grid_tariff_inr_kwh"], opex)
        irr        = _irr_bisection(cfs) * 100
        npv_cr     = _npv(cfs) / 1e7
        pb         = _payback(cfs)
        records.append({
            "state":       row["state"],
            "solar_yield_mwh_per_mw": _solar_yield_mwh_per_mw(row["solar_ghi_kwh_m2_day"]),
            "capex_cr":    round(capex / 1e7, 1),
            "irr_pct":     round(irr, 1),
            "npv_cr":      round(npv_cr, 1),
            "payback_yrs": pb if pb else ">20",
        })
    return pd.DataFrame(records)


def compute_policy_adjusted_financials(state_df: pd.DataFrame,
                                        policy_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply policy incentives to compute adjusted CAPEX/IRR:
      - fame2 + state subsidy → reduce effective capex per INSTALL_MW EVs supported
      - accelerated depreciation → tax shield reduces effective capex by ~10-15%
    """
    merged = state_df.merge(policy_df, on="state")
    records = []
    for _, row in merged.iterrows():
        # Assume 1 MW handles ~50 EVs simultaneously; subsidy per vehicle
        evs_per_mw         = 50
        subsidy_per_mw     = evs_per_mw * (row["fame2_subsidy_per_ev_inr"] + row["state_subsidy_per_ev_inr"])
        acc_dep_benefit    = INSTALL_MW * CAPEX_PER_MW * (row["accelerated_depreciation_pct"] / 100) * 0.30  # 30% tax rate
        adj_capex          = max(INSTALL_MW * CAPEX_PER_MW - INSTALL_MW * subsidy_per_mw - acc_dep_benefit, 1e6)

        annual_mwh = _solar_yield_mwh_per_mw(row["solar_ghi_kwh_m2_day"]) * INSTALL_MW
        # Green cert revenue bonus
        green_cert_bonus   = annual_mwh * 1000 * row["green_energy_certificate_inr_mwh"] / 1e6  # ₹/yr in ₹Cr
        opex               = INSTALL_MW * OPEX_PER_MW_YR - green_cert_bonus * 1e7 / PROJECT_YEARS  # spread over project

        cfs       = _build_cash_flows(adj_capex, annual_mwh, row["grid_tariff_inr_kwh"], INSTALL_MW * OPEX_PER_MW_YR)
        irr_adj   = _irr_bisection(cfs) * 100
        npv_adj   = _npv(cfs) / 1e7

        records.append({
            "state":          row["state"],
            "adj_capex_cr":   round(adj_capex / 1e7, 1),
            "irr_pct_base":   compute_base_financials(state_df.loc[[state_df[state_df["state"] == row["state"]].index[0]]]).iloc[0]["irr_pct"],
            "irr_pct_policy": round(irr_adj, 1),
            "npv_cr_policy":  round(npv_adj, 1),
        })
    return pd.DataFrame(records)


def run_monte_carlo(state_df: pd.DataFrame,
                    n: int = MC_ITERATIONS) -> pd.DataFrame:
    """
    Monte Carlo: for each state, sample:
      tariff     ~ N(mu, 0.15*mu)
      ghi        ~ N(mu, 0.08*mu)
      capex/mw   ~ N(4.5Cr, 0.10*4.5Cr)
    Returns P10, P50, P90 of IRR distribution per state.
    """
    rng = np.random.default_rng(42)
    records = []
    for _, row in state_df.iterrows():
        mu_tariff = row["grid_tariff_inr_kwh"]
        mu_ghi    = row["solar_ghi_kwh_m2_day"]
        mu_capex  = CAPEX_PER_MW

        tariffs = rng.normal(mu_tariff, 0.15 * mu_tariff, n)
        ghis    = rng.normal(mu_ghi,    0.08 * mu_ghi,    n)
        capexes = rng.normal(mu_capex,  0.10 * mu_capex,  n)

        irrs = []
        for i in range(n):
            annual_mwh = _solar_yield_mwh_per_mw(max(ghis[i], 3.0)) * INSTALL_MW
            capex_i    = max(capexes[i], 2e7) * INSTALL_MW
            cfs        = _build_cash_flows(capex_i, annual_mwh, max(tariffs[i], 3.0), INSTALL_MW * OPEX_PER_MW_YR)
            irrs.append(_irr_bisection(cfs) * 100)

        irrs = np.array(irrs)
        records.append({
            "state":     row["state"],
            "irr_p10":   round(float(np.percentile(irrs, 10)), 1),
            "irr_p50":   round(float(np.percentile(irrs, 50)), 1),
            "irr_p90":   round(float(np.percentile(irrs, 90)), 1),
            "irr_std":   round(float(np.std(irrs)), 1),
            "irr_all":   irrs.tolist(),
        })
    return pd.DataFrame(records)


if __name__ == "__main__":
    sd = pd.read_csv(DATA_DIR / "state_data.csv")
    base = compute_base_financials(sd)
    print("\n── Base Financials ─────────────────────────────")
    print(base.sort_values("irr_pct", ascending=False).to_string(index=False))

    mc = run_monte_carlo(sd.head(5))
    print("\n── Monte Carlo (top 5 states) ──────────────────")
    print(mc[["state", "irr_p10", "irr_p50", "irr_p90", "irr_std"]].to_string(index=False))
