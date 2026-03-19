"""
models/grid.py
Grid stress proxy model.
Estimates EV charging demand addition as % of state peak load.
Flags grid-constrained states and computes integration readiness score.
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR      = Path(__file__).parent.parent / "data"
GRID_WARN_PCT = 5.0   # flag if EV demand > 5% of peak load
GRID_CRIT_PCT = 10.0  # critical if > 10%

# Average charging efficiency and simultaneous demand coefficient
EV_KW_PER_CHARGER     = 22.0   # kW (AC fast charger)
PEAK_COINCIDENCE_FACTOR = 0.65  # fraction of EVs charging at peak simultaneously


def compute_grid_stress(state_df: pd.DataFrame,
                         demand_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each state:
      - Estimate simultaneous peak EV charging load (GW)
      - Compare to state's current peak demand (GW)
      - Compute grid stress % and integration readiness score

    Integration readiness combines:
      - Grid stability index
      - DISCOM financial health
      - Renewable capacity (higher = better grid absorption)
    """
    merged = state_df.merge(
        demand_df[["state", "ev_2029"]], on="state"
    )

    # Estimated peak charging load
    merged["peak_ev_charging_gw"] = (
        merged["ev_2029"] * EV_KW_PER_CHARGER * PEAK_COINCIDENCE_FACTOR / 1e6
    ).round(3)

    # Grid stress as % of current peak demand
    merged["grid_stress_pct"] = (
        merged["peak_ev_charging_gw"] / merged["peak_demand_gw"] * 100
    ).round(1)

    # Flag
    def _flag(pct):
        if pct >= GRID_CRIT_PCT:
            return "Critical"
        elif pct >= GRID_WARN_PCT:
            return "Stressed"
        else:
            return "Manageable"

    merged["grid_status"] = merged["grid_stress_pct"].apply(_flag)

    # Integration readiness score (0-100): higher = better grid for EV integration
    def _minmax(s):
        rng = s.max() - s.min()
        return (s - s.min()) / rng * 100 if rng > 0 else pd.Series([50.0] * len(s), index=s.index)

    merged["readiness_score"] = (
        0.35 * _minmax(merged["grid_stability_index"]) +
        0.30 * _minmax(merged["discom_health_score"])   +
        0.20 * _minmax(merged["renewable_capacity_mw"]) +
        0.15 * _minmax(100 - merged["grid_stress_pct"].clip(0, 30))
    ).round(1)

    # Needed new charging stations to support projected demand
    # Assume 1 station serves 10 EVs/day (urban fast charger)
    merged["charging_stations_needed"] = (merged["ev_2029"] / 10).astype(int)
    merged["stations_gap"] = (
        merged["charging_stations_needed"] - merged["ev_charging_stations"]
    ).clip(lower=0)

    cols = ["state", "peak_ev_charging_gw", "peak_demand_gw", "grid_stress_pct",
            "grid_status", "readiness_score", "charging_stations_needed", "stations_gap",
            "grid_stability_index", "discom_health_score"]
    return merged[cols].sort_values("readiness_score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    from models.demand import build_demand_forecast
    sd = pd.read_csv(DATA_DIR / "state_data.csv")
    dd = build_demand_forecast()
    df = compute_grid_stress(sd, dd)
    print(df[["state", "grid_stress_pct", "grid_status",
              "readiness_score", "stations_gap"]].to_string(index=False))
