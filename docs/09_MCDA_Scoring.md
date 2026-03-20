# [Chapter 09] MCDA Scoring & Normalization

## 1. Comparing Apples to Oranges
How do you compare **IRR (%)**, **Demand (MWh)**, **GHI (Sunlight Index)**, and **Grid Stress (%)**? They all have different units. If you just add them together, the 150k EV volume will drown out the 22% IRR.

I implemented **Multi-Criteria Decision Analysis (MCDA)** to create a fair, normalized ranking.

## 2. Min-Max Normalization Math
I use Min-Max scaling to force every metric onto a uniform **0 to 100 scale**:
$$Normalized\ Score = \frac{x - min(X)}{max(X) - min(X)} \cdot 100$$
- The state with the highest IRR gets a score of **100**.
- The state with the lowest IRR gets **0**.
- Now, all metrics are mathematically comparable "points."

## 3. The Weighted Decision Matrix
The model applies a default "Consultant's Weighting" (which can be adjusted in the dashboard):
1.  **Financial Return (IRR) — 30%:** Profitability drives the engine.
2.  **EV Demand (MWh) — 25%:** Ensures high utilization of the assets.
3.  **Solar Resource (GHI) — 20%:** Quality of the "free" energy source (sunlight).
4.  **Policy Friendliness — 15%:** Ease of doing business and subsidies.
5.  **Urbanization — 10%:** Proxy for land constraints and premium user density.

## 4. Weight Sensitivity: The Tornado Chart
A key part of the model is the **Weight Sensitivity Tornado Chart**. 
- It proves that even if an investor disagrees with my weights (e.g., they care 20% more about Finance), the **top Tier 1 states generally stay the same**. 
- This confirms that our findings are **robust**, not just side-effects of a biased weighting system.

## 5. State Tier List
Based on the final Composite Score:
- **Tier 1 (Premium):** Score > 75
- **Tier 2 (High):** Score 60 – 75
- **Tier 3 (Moderate):** Score 40 – 60
- **Tier 4 (Low):** Score < 40

---
*Next Chapter: Executive Synthesis — Detailed State Profiles.*
