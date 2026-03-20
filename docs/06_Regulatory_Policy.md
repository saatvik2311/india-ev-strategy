# [Chapter 06] The Regulatory Database: Policy Layer

## 1. `policy_incentives.csv`
To build a realistic model, I couldn't just use a flat tax rate or uniform subsidies for all of India. I compiled a dedicated **Regulatory Database (`policy_incentives.csv`)** to map state-by-state variations. 

In reality, an EV project's profitability is heavily dependent on specific state government rules. This module demonstrates the ability to bridge backend data with complex governmental policy logic.

## 2. Subsidy Stacking: The Three Pillars
In the `compute_policy_adjusted_financials` function, we dynamically alter the **Year-0 CAPEX** based on the state. We stack three different incentives to lower the entry cost for investors:

### Pillar 1: Central Subsidy (FAME-II / PM E-DRIVE)
The central government provides a baseline incentive to spur adoption.
- **The Rate:** ₹15,000 per EV supported.
- **Misconception Check:** This is **NOT** a recurring yearly payment. It is a **one-time** subsidy per vehicle sold/purchased, intended to reduce the hardware cost hurdle.
- **The Math:** If our 10 MW station supports 1,000 EVs, we subtract **₹1.5 Crores** from our Year-0 CAPEX.

### Pillar 2: State-Level Subsidies
This is where the divergence happens. States compete for investment.
- **Delhi:** One of the most aggressive, offering an extra **₹30,000 per EV**.
- **Bihar:** Minimal support, offering only **₹3,000 per EV**.
- **Impact:** The same project started in Delhi will have a significantly lower "Effective CAPEX" than one in Bihar, automatically boosting the starting IRR.

### Pillar 3: Accelerated Depreciation
The Indian tax code allows renewable infrastructure companies to claim **40% Accelerated Depreciation** earlier in the project's life.
- **Interpretation:** This is not cash-in-hand; it is a **Tax Shield**. 
- **Impact:** By writing off 40% of the asset's value early (approximately ₹18 Crores for a 10 MW plant), we drastically reduce our taxable profit in Year 1. This keeps more cash *inside* the project when it’s most needed, further boosting NPV.

## 3. Business Inference: Arbitrage over Sunlight
By calculating financials twice (once for "Base" and once for "Policy Adjusted"), we create a **Policy Arbitrage Analysis**.

The model reveals that a state with mediocre sunlight but massive government subsidies (like Delhi) often yields a higher IRR than a state with perfect sunlight but zero subsidies (like Rajasthan). This is a crucial "Boardroom" takeaway: **We are optimizing for capital efficiency, not just solar physics.**

---
*Next Chapter: Risk & Probability — The Monte Carlo Simulation.*
