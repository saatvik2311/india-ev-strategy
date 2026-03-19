"""
models/demand.py
Trend-fitted EV demand forecasting using historical registration data.
Fits an exponential growth curve per state and forecasts 2025-2030.
"""
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
AVG_KWH_PER_EV_YEAR = 1800  # ~5 kWh/day × 360 days


def _fit_growth_rate(years: list, registrations: list) -> float:
    """Fit ln(EV) = a + b*year via OLS; return annual growth rate b."""
    y = np.array(years, dtype=float)
    r = np.array(registrations, dtype=float)
    valid = r > 0
    if valid.sum() < 2:
        return 0.35  # fallback CAGR
    log_r = np.log(r[valid])
    y_v = y[valid]
    b = np.polyfit(y_v - y_v.mean(), log_r - log_r.mean(), 1)[0]
    return float(np.clip(b, 0.05, 1.20))  # cap between 5% and 120%


def build_demand_forecast(forecast_years: int = 6) -> pd.DataFrame:
    """
    Returns a DataFrame with:
      state, fitted_cagr, ev_2024, ev_2029, ev_2030,
      demand_mwh_2029, demand_mwh_2030, demand_mwh_list (2025-2030)
    """
    ts = pd.read_csv(DATA_DIR / "year_timeseries.csv")
    state_data = pd.read_csv(DATA_DIR / "state_data.csv")

    year_cols = [c for c in ts.columns if c.startswith("ev_")]
    years = [int(c.replace("ev_", "")) for c in year_cols]

    rows = []
    for _, row in ts.iterrows():
        regs = [row[c] for c in year_cols]
        cagr = _fit_growth_rate(years, regs)
        base = row["ev_2024"]

        ev_by_year = {}
        for offset in range(1, forecast_years + 1):
            yr = 2024 + offset
            ev_by_year[yr] = int(base * (1 + cagr) ** offset)

        demand_by_year = {yr: ev * AVG_KWH_PER_EV_YEAR / 1000
                          for yr, ev in ev_by_year.items()}

        rows.append({
            "state":           row["state"],
            "fitted_cagr":     round(cagr * 100, 1),
            "ev_2024":         int(base),
            "ev_2029":         ev_by_year.get(2029, 0),
            "ev_2030":         ev_by_year.get(2030, 0),
            "demand_mwh_2029": round(demand_by_year.get(2029, 0), 0),
            "demand_mwh_2030": round(demand_by_year.get(2030, 0), 0),
            "ev_by_year":      ev_by_year,
            "demand_by_year":  demand_by_year,
        })

    return pd.DataFrame(rows)


def apply_scenario(demand_df: pd.DataFrame, scenario: str = "Base") -> pd.DataFrame:
    """Scale demand forecast by scenario multipliers."""
    multipliers = {"Low": 0.65, "Base": 1.0, "High": 1.45}
    m = multipliers.get(scenario, 1.0)
    out = demand_df.copy()
    out["ev_2029"]         = (out["ev_2029"] * m).astype(int)
    out["demand_mwh_2029"] = (out["demand_mwh_2029"] * m).round(0)
    return out


if __name__ == "__main__":
    df = build_demand_forecast()
    print(df[["state", "fitted_cagr", "ev_2024", "ev_2029",
              "demand_mwh_2029"]].sort_values("demand_mwh_2029", ascending=False).to_string(index=False))
