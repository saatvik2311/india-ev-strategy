"""
visualisations/charts.py
Generates all 8 consulting-grade charts and saves to outputs/charts/.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter
from pathlib import Path

CHART_DIR = Path(os.environ.get("EV_CHART_DIR", Path(__file__).parent.parent / "outputs" / "charts"))
CHART_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = {
    "primary":   "#1B4F8A",
    "accent":    "#E8932A",
    "positive":  "#2E8B57",
    "neutral":   "#607D8B",
    "negative":  "#C0392B",
    "light":     "#ECF0F1",
    "tiers":     ["#C0392B", "#E67E22", "#27AE60", "#1B4F8A"],
}

plt.rcParams.update({
    "font.family":   "DejaVu Sans",
    "font.size":     10,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
    "axes.grid":          True,
    "grid.alpha":         0.25,
    "grid.linestyle":     "--",
})


def _save(fig, name):
    path = CHART_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓  {name}.png")
    return path


# ── Chart 1: Composite Score Horizontal Bar ───────────────────────────────────
def chart_composite_scores(scores_df: pd.DataFrame):
    df = scores_df.sort_values("composite_score").tail(15)
    tier_colors = {
        "Tier 1 (Premium)":  PALETTE["primary"],
        "Tier 2 (High)":     PALETTE["positive"],
        "Tier 3 (Moderate)": PALETTE["accent"],
        "Tier 4 (Low)":      PALETTE["negative"],
    }
    colors = [tier_colors.get(str(t), PALETTE["neutral"]) for t in df["tier"]]

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(df["state"], df["composite_score"], color=colors, height=0.65)
    ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=9)
    ax.set_xlabel("Composite Investment Attractiveness Score (0–100)")
    ax.set_title("India EV + Renewable: State Investment Attractiveness Ranking",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlim(0, 110)
    handles = [mpatches.Patch(color=v, label=k) for k, v in tier_colors.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=9)
    ax.axvline(60, color=PALETTE["neutral"], linestyle=":", alpha=0.5, label="Moderate threshold")
    fig.tight_layout()
    return _save(fig, "1_composite_scores")


# ── Chart 2: IRR Bubble Scatter (x=tariff, y=IRR, size=demand) ───────────────
def chart_irr_bubble(scores_df: pd.DataFrame, state_df: pd.DataFrame,
                      base_fin: pd.DataFrame):
    # scores_df already contains irr_pct from compute_scores; just add tariff
    merged = scores_df.merge(state_df[["state", "grid_tariff_inr_kwh"]], on="state")
    sizes  = (merged["demand_mwh_2029"] / merged["demand_mwh_2029"].max() * 800 + 60).values

    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(merged["grid_tariff_inr_kwh"], merged["irr_pct"],
                    s=sizes, c=merged["composite_score"],
                    cmap="RdYlGn", alpha=0.85, edgecolors="white", linewidths=0.8)
    for _, row in merged.iterrows():
        ax.annotate(row["state"], (row["grid_tariff_inr_kwh"], row["irr_pct"]),
                    textcoords="offset points", xytext=(5, 4), fontsize=7.5)
    cbar = plt.colorbar(sc, ax=ax, shrink=0.8)
    cbar.set_label("Composite Score", fontsize=9)
    ax.set_xlabel("Grid Tariff (₹/kWh)")
    ax.set_ylabel("Base IRR (%)")
    ax.set_title("IRR vs. Tariff — Bubble Size ∝ EV Demand (2029)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.axhline(15, color=PALETTE["negative"], linestyle="--", alpha=0.5, label="Min attractive IRR (15%)")
    ax.legend(fontsize=9)
    return _save(fig, "2_irr_bubble_scatter")


# ── Chart 3: Scenario Fan Chart (P10/P50/P90) ────────────────────────────────
def chart_scenario_fan(mc_df: pd.DataFrame, top_n: int = 8):
    df = mc_df.head(top_n).sort_values("irr_p50", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(df))
    ax.barh(y, df["irr_p90"] - df["irr_p10"],
            left=df["irr_p10"], color=PALETTE["primary"], alpha=0.20, height=0.5, label="P10–P90 range")
    ax.scatter(df["irr_p50"], y, color=PALETTE["primary"], zorder=5, s=60, label="P50 (median)")
    ax.scatter(df["irr_p10"], y, color=PALETTE["negative"], zorder=5, s=40, marker="|", linewidths=2)
    ax.scatter(df["irr_p90"], y, color=PALETTE["positive"], zorder=5, s=40, marker="|", linewidths=2)
    ax.set_yticks(y)
    ax.set_yticklabels(df["state"])
    ax.set_xlabel("IRR (%)")
    ax.set_title("Monte Carlo IRR Distribution — Top States\n(P10 | Median | P90 from 1,000 simulations)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.axvline(15, color=PALETTE["negative"], linestyle="--", alpha=0.5)
    ax.legend(fontsize=9)
    return _save(fig, "3_scenario_fan_mcarlo")


# ── Chart 4: GHI Heatmap ─────────────────────────────────────────────────────
def chart_ghi_heatmap(state_df: pd.DataFrame):
    df = state_df.sort_values("solar_ghi_kwh_m2_day", ascending=False)
    matrix = df["solar_ghi_kwh_m2_day"].values.reshape(-1, 1)
    fig, ax = plt.subplots(figsize=(4, 10))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")
    ax.set_xticks([])
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["state"], fontsize=9)
    for i, v in enumerate(df["solar_ghi_kwh_m2_day"]):
        ax.text(0, i, f"{v:.1f}", ha="center", va="center", fontsize=8.5,
                color="black" if v < 5.8 else "white", fontweight="bold")
    plt.colorbar(im, ax=ax, label="GHI (kWh/m²/day)", shrink=0.6)
    ax.set_title("Solar Resource Quality\nGHI by State", fontsize=12, fontweight="bold", pad=10)
    return _save(fig, "4_ghi_heatmap")


# ── Chart 5: Demand Forecast Lines (top 5 states) ────────────────────────────
def chart_demand_forecast(demand_df: pd.DataFrame, top_n: int = 6):
    top_states = demand_df.nlargest(top_n, "demand_mwh_2029")["state"].tolist()
    colors = plt.cm.tab10(np.linspace(0, 0.9, top_n))

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, state in enumerate(top_states):
        row = demand_df[demand_df["state"] == state].iloc[0]
        yrs = sorted(row["demand_by_year"].keys())
        vals = [row["demand_by_year"][y] / 1000 for y in yrs]  # → GWh
        ax.plot(yrs, vals, marker="o", lw=2.0, color=colors[i], label=state)

    ax.set_xlabel("Year")
    ax.set_ylabel("EV Charging Demand (GWh/year)")
    ax.set_title("EV Charging Demand Forecast 2025–2030 — Top States",
                 fontsize=13, fontweight="bold", pad=12)
    ax.legend(fontsize=9)
    ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    return _save(fig, "5_demand_forecast_lines")


# ── Chart 6: NPV Waterfall (top state) ───────────────────────────────────────
def chart_npv_waterfall(base_fin: pd.DataFrame, policy_fin: pd.DataFrame):
    top = base_fin.sort_values("irr_pct", ascending=False).iloc[0]
    state = top["state"]
    pol_row = policy_fin[policy_fin["state"] == state].iloc[0]

    capex_cr      = -top["capex_cr"]
    base_npv      = top["npv_cr"]
    policy_npv    = pol_row["npv_cr_policy"]
    policy_uplift = policy_npv - base_npv

    labels  = ["CAPEX\n(outflow)", "Base\nNPV", "Policy\nIncentives", "Policy-\nAdjusted NPV"]
    values  = [capex_cr, base_npv, policy_uplift, policy_npv]
    colors  = [PALETTE["negative"], PALETTE["primary"], PALETTE["positive"], PALETTE["accent"]]
    bottoms = [0, 0, base_npv, 0]

    fig, ax = plt.subplots(figsize=(9, 6))
    for i, (lbl, val, col, bot) in enumerate(zip(labels, values, colors, bottoms)):
        ax.bar(i, abs(val) if i != 0 else val, bottom=bot if i != 0 else 0,
               color=col, width=0.5, alpha=0.9)
        ax.text(i, (bot + val / 2) if i not in [0] else val / 2,
                f"₹{abs(val):.1f} Cr", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")

    ax.set_xticks(range(4))
    ax.set_xticklabels(labels)
    ax.set_ylabel("₹ Crore")
    ax.set_title(f"NPV Waterfall — {state} (10 MW installation)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.axhline(0, color="black", linewidth=0.8)
    return _save(fig, "6_npv_waterfall")


# ── Chart 7: Monte Carlo Histogram (top 3 states) ────────────────────────────
def chart_monte_carlo_hist(mc_df: pd.DataFrame, top_n: int = 3):
    top3 = mc_df.head(top_n)
    colors = [PALETTE["primary"], PALETTE["accent"], PALETTE["positive"]]
    fig, axes = plt.subplots(1, top_n, figsize=(13, 5), sharey=False)

    for ax, (_, row), col in zip(axes, top3.iterrows(), colors):
        irrs = np.array(row["irr_all"])
        ax.hist(irrs, bins=40, color=col, alpha=0.80, edgecolor="white", linewidth=0.4)
        ax.axvline(row["irr_p50"], color="black",  lw=1.5, linestyle="--", label=f"P50 {row['irr_p50']:.1f}%")
        ax.axvline(row["irr_p10"], color=PALETTE["negative"], lw=1.2, linestyle=":", label=f"P10 {row['irr_p10']:.1f}%")
        ax.axvline(row["irr_p90"], color=PALETTE["positive"], lw=1.2, linestyle=":", label=f"P90 {row['irr_p90']:.1f}%")
        ax.set_title(row["state"], fontsize=11, fontweight="bold")
        ax.set_xlabel("IRR (%)")
        ax.set_ylabel("Frequency" if ax == axes[0] else "")
        ax.legend(fontsize=8)

    fig.suptitle("Monte Carlo IRR Distribution — Top 3 States (n=1,000)", 
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save(fig, "7_monte_carlo_histogram")


# ── Chart 8: Weight Sensitivity Tornado ──────────────────────────────────────
def chart_weight_tornado(sensitivity_df: pd.DataFrame, target_state: str = None):
    if target_state is None:
        target_state = sensitivity_df["state"].value_counts().idxmax()
    df = sensitivity_df[sensitivity_df["state"] == target_state].copy()
    df["label"] = df["weight"] + " (" + df["direction"] + ")"
    up   = df[df["direction"] == "up"].set_index("weight")["rank_delta"]
    down = df[df["direction"] == "down"].set_index("weight")["rank_delta"]
    keys = list(DEFAULT_WEIGHTS_REF.keys())

    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(keys))
    ax.barh(y - 0.2, [up.get(k, 0) for k in keys], height=0.35,
            color=PALETTE["positive"], alpha=0.85, label="+20% weight")
    ax.barh(y + 0.2, [down.get(k, 0) for k in keys], height=0.35,
            color=PALETTE["negative"], alpha=0.85, label="-20% weight")
    ax.set_yticks(y)
    ax.set_yticklabels([k.capitalize() for k in keys])
    ax.set_xlabel("Change in Rank (positive = moved up)")
    ax.set_title(f"Weight Sensitivity — {target_state}\n(How ±20% weight change shifts ranking)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.axvline(0, color="black", lw=0.8)
    ax.legend(fontsize=9)
    return _save(fig, "8_weight_sensitivity_tornado")


DEFAULT_WEIGHTS_REF = {
    "financial": 0.30,
    "demand":    0.25,
    "solar":     0.20,
    "policy":    0.15,
    "urban":     0.10,
}


def generate_all_charts(scores_df, state_df, base_fin, mc_df,
                         demand_df, policy_fin, sensitivity_df):
    print("\n── Generating charts ───────────────────────────────────────────────")
    chart_composite_scores(scores_df)
    chart_irr_bubble(scores_df, state_df, base_fin)
    chart_scenario_fan(mc_df)
    chart_ghi_heatmap(state_df)
    chart_demand_forecast(demand_df)
    chart_npv_waterfall(base_fin, policy_fin)
    chart_monte_carlo_hist(mc_df)
    chart_weight_tornado(sensitivity_df, target_state=scores_df.iloc[0]["state"])
    print(f"  All charts saved to: {CHART_DIR}")
