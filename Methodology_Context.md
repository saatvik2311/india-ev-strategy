# India EV + Renewable Infrastructure — Consulting Methodology & Context

This document contains the complete technical methodology, financial logic, and strategic rationale behind the India EV Investment Strategy model. It acts as the "source of truth" to explain *how* and *why* specific recommendations are generated.

---

## 1. The Strategy: Pareto-Inspired Market Selection
We model 20 Indian states (out of 28 states and 8 union territories). This represents an **"Addressable Market Coverage Strategy"** inspired by the Pareto Principle. 
*   **Why 20 States?** These states represent over 90% of India's GDP, population, and current EV market share.
*   **Stratified Sampling vs. Strict Pareto:** A strict Pareto approach (Top 5 states = 80% outcome) would fail because it completely misses high-growth emerging markets (e.g., Bihar, UP) or states with immense solar viability (e.g., Rajasthan). 
*   **The Mix:** The selected states provide a robust mix of "Early Adopter" Tier-1 hubs (Delhi, Maharashtra), "Sun Belt" solar regions (Gujarat, Rajasthan), and massive long-term scale markets (UP, West Bengal), allowing the model to prove its capacity across varying conditions.

---

## 2. Core Financial Concepts (IRR & NPV)
The financial model relies heavily on the **Internal Rate of Return (IRR)** and **Net Present Value (NPV)**.
*   **IRR is Compounded, Not Simple:** IRR represents a *compounded annual return*, not a simple linear rate. If a project has a 20% IRR, it behaves like an investment compounding at 20% annually over its 20-year lifetime.
*   **The Underlying Mathematics:** IRR is the discount rate $r$ that makes the Net Present Value (NPV) of all cash flows (CF) equal zero. The model solves this using a robust bisection search algorithm.
*   **CAPEX vs. Effective CAPEX:** The base model assumes a Gross CAPEX of ₹4.5 Cr per MW of solar installed. However, **Policy Incentives** drastically reduce this. 

### Subsidy Stacking & Policy-Adjusted Returns
To model real-world viability, the financial engine applies "Subsidy Stacking":
1.  **Central Subsidy (FAME-II / PM E-DRIVE):** Provides a baseline ₹15,000 per EV equivalent (the model assumes a 10 MW station supports ~500 EVs, applying the subsidy proportionally).
2.  **State-Level Subsidies:** Varies wildly by state. Delhi offers up to ₹30,000 per EV, pushing effective CAPEX much lower compared to states with no subsidy.
3.  **Accelerated Depreciation (Tax Shield):** Companies can claim a 40% depreciation in Year 1. At a 30% corporate tax rate, this acts as a massive Year 1 tax shield (effectively returning ~12% of Gross CAPEX).
4.  **Green Energy Certificates:** Extra revenue added to annual OPEX models.
**Result:** Effective CAPEX drops by 30-50%, increasing Base IRR by 2–6 percentage points ("Policy IRR").

### Monte Carlo Simulation (Risk Modeling)
The model runs 1,000 simulations per state to handle real-world volatility:
1.  **Grid Tariff:** Modeled as Normal Distribution (µ = base tariff, σ = 15%).
2.  **Solar GHI:** Modeled as Normal Distribution (µ = base GHI, σ = 8%).
3.  **CAPEX:** Modeled as Normal Distribution (µ = ₹4.5Cr, σ = 10%).
It outputs the P10 (Downside), P50 (Expected/Median), and P90 (Upside) IRR.

---

## 3. Operations & Engineering Models

### Demand Forecasting (`demand.py`)
Predicts EV charging demand (MWh) out to 2029/2030 using historical EV registration data.
*   **Algorithm:** Fits an exponential growth curve per state using Ordinary Least Squares (OLS) on the log-transformed historical registrations: `ln(EV) = a + b*year`. The slope `b` is the Compound Annual Growth Rate (CAGR), capped between 5% and 120%.
*   **Conversion:** Assumes each EV consumes 1,800 kWh per year (approx 5 kWh/day × 360 days).
*   **Scenarios:** Base (1.0x), Low (0.65x multiplier), High (1.45x multiplier).

### Grid Integration Readiness (`grid.py`)
Evaluates if a state's electrical grid can survive the incoming EV load.
*   **Stress Calculation:** Computes simultaneous peak charging load assuming a 22 kW fast charger per EV, with a Peak Coincidence Factor of 0.65 (65% charging at the identical peak hour).
*   **Grid Status:** If EV load adds >10% to the state's current peak demand, it is flagged as "Critical". If >5%, "Stressed". Otherwise, "Manageable".
*   **Readiness Score (0-100):** A weighted index combining Grid Stability, DISCOM Financial Health, existing Renewable Capacity, and inverse Grid Stress.

---

## 4. Multi-Criteria Decision Analysis (MCDA) Scoring
The `scoring.py` module ranks the 20 states by computing a composite **Investment Attractiveness Score (0–100)**.
It uses Min-Max normalization to standardise different units (IRR %, MWh, GHI) onto a 0-100 scale: `(x - min) / (max - min) * 100`.

**Default Weights:**
1.  **Financial Return (IRR) - 30%:** Heaviest weight. Profitability drives private capital.
2.  **EV Demand (2029 MWh) - 25%:** Utilization rate of the charging assets.
3.  **Solar Resource (GHI) - 20%:** Quality of the solar yield.
4.  **Policy Environment - 15%:** Regulatory ease and subsidy strength.
5.  **Urbanisation - 10%:** Proxy for land constraints and premium user density.

*(Note: The Streamlit dashboard allows recruiters to dynamically adjust these weights, automatically triggering a recalculation of the Min-Max composite scores and tiers).*

### State Tiering Classification
Based on the final Composite Score:
*   **Tier 1 (Premium):** Score > 75
*   **Tier 2 (High):** Score 60 – 75
*   **Tier 3 (Moderate):** Score 40 – 60
*   **Tier 4 (Low):** Score < 40
