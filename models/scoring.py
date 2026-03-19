"""
models/scoring.py
MCDA (Multi-Criteria Decision Analysis) with configurable weights.
Computes composite investment attractiveness score per state.
"""
import numpy as np
import pandas as pd

# Default weights (must sum to 1.0)
DEFAULT_WEIGHTS = {
    "financial":  0.30,   # IRR
    "demand":     0.25,   # EV demand 2029
    "solar":      0.20,   # GHI
    "policy":     0.15,   # EV policy score
    "urban":      0.10,   # Urbanisation %
}


def _minmax(series: pd.Series) -> pd.Series:
    rng = series.max() - series.min()
    if rng < 1e-9:
        return pd.Series([50.0] * len(series), index=series.index)
    return (series - series.min()) / rng * 100


def compute_scores(state_df: pd.DataFrame,
                   base_financials: pd.DataFrame,
                   demand_df: pd.DataFrame,
                   weights: dict = None) -> pd.DataFrame:
    """
    Compute composite MCDA scores for all states.

    Parameters
    ----------
    state_df        : enriched state data
    base_financials : output from financial.compute_base_financials
    demand_df       : output from demand.build_demand_forecast
    weights         : dict with keys matching DEFAULT_WEIGHTS (must sum to 1.0)

    Returns
    -------
    DataFrame with state, component scores (0-100), composite score, tier.
    """
    w = weights or DEFAULT_WEIGHTS

    merged = (
        state_df
        .merge(base_financials[["state", "irr_pct"]], on="state")
        .merge(demand_df[["state", "demand_mwh_2029"]], on="state")
    )

    merged["score_financial"] = _minmax(merged["irr_pct"])
    merged["score_demand"]    = _minmax(merged["demand_mwh_2029"])
    merged["score_solar"]     = _minmax(merged["solar_ghi_kwh_m2_day"])
    merged["score_policy"]    = _minmax(merged["ev_policy_score"])
    merged["score_urban"]     = _minmax(merged["urban_pct"])

    merged["composite_score"] = (
        w["financial"] * merged["score_financial"] +
        w["demand"]    * merged["score_demand"]    +
        w["solar"]     * merged["score_solar"]     +
        w["policy"]    * merged["score_policy"]    +
        w["urban"]     * merged["score_urban"]
    ).round(1)

    # Tier classification
    merged["tier"] = pd.cut(
        merged["composite_score"],
        bins=[0, 40, 60, 75, 100],
        labels=["Tier 4 (Low)", "Tier 3 (Moderate)", "Tier 2 (High)", "Tier 1 (Premium)"],
        right=True,
    )

    cols = ["state", "composite_score", "tier", "score_financial",
            "score_demand", "score_solar", "score_policy", "score_urban",
            "irr_pct", "demand_mwh_2029", "solar_ghi_kwh_m2_day",
            "ev_policy_score", "urban_pct"]
    return merged[cols].sort_values("composite_score", ascending=False).reset_index(drop=True)


def weight_sensitivity(state_df, base_financials, demand_df,
                        top_n: int = 5, delta: float = 0.20) -> pd.DataFrame:
    """
    Show how top_n state rankings shift when each weight is varied ±delta.
    Returns a summary DataFrame with rank deltas per weight change.
    """
    base_scores = compute_scores(state_df, base_financials, demand_df)
    base_ranks  = base_scores.reset_index()[["state", "index"]].rename(columns={"index": "base_rank"})
    top_states  = base_scores.head(top_n)["state"].tolist()

    results = []
    for key in DEFAULT_WEIGHTS:
        for direction, sign in [("up", 1), ("down", -1)]:
            w_new = DEFAULT_WEIGHTS.copy()
            w_new[key] = max(0.0, min(1.0, w_new[key] + sign * delta))
            # Re-normalise
            total = sum(w_new.values())
            w_new = {k: v / total for k, v in w_new.items()}

            new_scores = compute_scores(state_df, base_financials, demand_df, weights=w_new)
            new_ranks  = new_scores.reset_index()[["state", "index"]].rename(columns={"index": "new_rank"})
            merged_r   = base_ranks.merge(new_ranks, on="state")
            merged_r["rank_delta"] = merged_r["base_rank"] - merged_r["new_rank"]

            for state in top_states:
                row = merged_r[merged_r["state"] == state]
                if not row.empty:
                    results.append({
                        "weight":     key,
                        "direction":  direction,
                        "state":      state,
                        "rank_delta": int(row["rank_delta"].values[0]),
                    })

    return pd.DataFrame(results)


if __name__ == "__main__":
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models.financial import compute_base_financials
    from models.demand    import build_demand_forecast

    DATA_DIR = Path(__file__).parent.parent / "data"
    sd = pd.read_csv(DATA_DIR / "state_data.csv")
    bf = compute_base_financials(sd)
    dd = build_demand_forecast()

    scores = compute_scores(sd, bf, dd)
    print(scores[["state", "composite_score", "tier", "irr_pct"]].to_string(index=False))
