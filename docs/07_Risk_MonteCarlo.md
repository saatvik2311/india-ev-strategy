# [Chapter 07] Risk Analysis: Monte Carlo Simulation

## 1. The Fallacy of Averages
McKinsey and BCG clients don't just ask **"How much money will I make?"** They ask, **"What is the probability that I lose everything?"** 

Using static averages in infrastructure is dangerous. If you assume electricity prices will stay the same for 20 years, your model is a work of fiction. Variables fluctuate. I wrote a **Monte Carlo engine (`run_monte_carlo`)** to quantify this uncertainty.

## 2. Running "1,000 Alternate Realities"
Instead of assuming fixed numbers, the model pulls from **Gaussian (Normal) Probability Distributions** for every state across 1,000 separate iterations:
1.  **Grid Tariffs ($\pm 15\%$):** State governments frequently change electricity prices for political reasons.
2.  **CAPEX ($\pm 10\%$):** Standard engineering margin for construction cost overruns and material price spikes.
3.  **Solar Irradiance ($\pm 8\%$):** Weather, cloud cover, and air quality (SMOG/pollution) vary year-by-year.

For a state like Karnataka, the algorithm randomly mixes these variables 1,000 times and generates 1,000 different possible IRRs.

## 3. Quantifying Risk: Percentiles (P10, P50, P90)
We don't look at the single highest return; we look at the **Probability Distribution**:
- **P10 (The Worst Case / The Floor):** 90% of the time, the project will perform **better** than this number. This is the "Conservative Guardrail." If the P10 is negative, the state is a high-risk gamble.
- **P50 (The Expected Case / Median):** The most realistic, middle-of-the-road return.
- **P90 (The Best Case / Blue Sky):** 10% of the time, everything goes perfectly and we hit this massive return.

## 4. The Business "Pivot" Case
Consider two states:
- **State A:** Average IRR of **20%**, but a P10 of **-5%**.
- **State B:** Average IRR of **18%**, but a P10 of **12%**.

**State B is vastly superior** for a risk-averse institutional investor (like a Pension Fund). We have successfully **quantified the risk**, allowing decision-makers to choose stability over volatile "paper profits."

---
*Next Chapter: Grid Mechanics — Predicting Stability and Stress.*
