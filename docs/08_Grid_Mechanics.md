# [Chapter 08] Grid Mechanics & Stability Stress

## 1. The Infrastructure Bottleneck
You can build the world's most profitable charging station, but if it causes the local power grid to collapse, the government will shut you down. Infrastructure investors must ensure that the local grid can survive the incoming EV load.

## 2. Calculating Grid Stress
In `models/grid.py`, I calculate the **Peak Gigawatt (GW) load** of the projected EV fleet for each state and compare it to the state's existing peak demand.

### 🧠 The Math: Peak Load Addition
We assume a charging profile where most vehicles use standard 22 kW fast chargers.
- **Coincidence Factor (0.65):** We assume that during the peak evening or morning hours, **65%** of the vehicle fleet is charging simultaneously.
- **Flagging the load:**
    - If EV demand adds **>10%** to the state's grid load, it is flagged as **"Critical."**
    - If it adds **>5%**, it is **"Stressed."**
    - Anything below 5% is deemed **"Manageable."**

## 3. The DISCOM Component
Electricity in India is managed by **DISCOMs** (Distribution Companies). Many are in deep financial debt, meaning they cannot afford to upgrade transformers to support EV fast chargers.
- The model incorporates **DISCOM Financial Health** into the final "Grid Readiness Score."
- A state with a "Critical" grid and poor DISCOM health (like Haryana) is a dangerous investment without extra capital for grid reinforcement.

## 4. Strategic Recommendation: BESS Integration
For "Critical" states like Delhi, the model suggests a **BESS (Battery Energy Storage System)** strategy. 
- **The Concept:** Draw solar power during the day and store it. Discharge it at night/peak hours to help the grid. 
- **The Impact:** This load-shifting prevents grid "blackouts" and allows the developer to capture higher peak-demand electricity prices.

---
*Next Chapter: MCDA Scoring — Ranking the Winners.*
