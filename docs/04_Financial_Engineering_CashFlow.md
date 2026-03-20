# [Chapter 04] Financial Engineering I: Unit Economics

## 1. The Blueprint: 10 MW Solar-EV Hub
In a McKinsey case interview, you move from "Market Sizing" to "Unit Economics." We modeled a standard solar + charging infrastructure project to assess viability.

### 🧠 Standard Benchmarks
- **Station Size:** 10 Megawatt (MW) capacity.
- **CAPEX (Capital Expenditure):** Building 1 MW of solar-integrated charging infrastructure costs **₹4.5 Crores**. Therefore, a 10 MW hub costs **₹45 Crores ($5.5M)**.
- **OPEX (Operational Expenditure):** Maintenance, staff, grid connectivity, and Green Energy Certificates cost approximately **₹15 Lakhs per MW per year**. For a 10 MW hub, this is ₹1.5 Crores/year.
- **Project Lifespan:** 20 Years.

## 2. Revenue Modeling
Profit volume does not equal profit rate. We calculate revenue by multiplying:
1.  **Energy Harvested:** The state's local **Global Horizontal Irradiance (GHI)** (how strong the sunlight is).
2.  **Grid Tariff:** The local price of electricity we can sell back to the grid or to EV users.

## 3. The Physical Reality Check: Solar Degradation
Solar panels aren't magical; they age. I programmed a **DEGRADATION constant of 0.5% per year**. 
- **Impact:** Year 10 will physically generate less power than Year 1. 
- **Business Rationale:** This proves to an interviewer that the model respects **real-world physics**, not just pure Excel math. Most amateur models ignore degradation, which leads to overestimating profits by 5-10% over two decades.

## 4. Building the Cash Flow Array (`_build_cash_flows`)
I wrote a function from scratch to simulate the bank account of this project over 20 years:
- **Year 0 (The Outflow):** We spend the CAPEX. This is a massive negative cash flow.
- **Years 1 to 20 (The Inflow):** We generate revenue (Solar Yield × Tariff) and subtract the recurring OPEX.
- **Result:** An array of 21 values that represents the project's lifetime and allows us to calculate its true value.

## 5. NPV: Net Present Value
We use **Net Present Value (NPV)** to determine if the project is theoretically profitable in "today's money."
- we apply a **10% Discount Rate** (the typical opportunity cost of capital for infrastructure investors).
- NPV takes all future cash flows and discounts them back to today. 
- **Hurdle:** If the NPV is greater than zero, the project is a "Go."

---
*Next Chapter: The IRR Engine — Solving for the Zero Crossing.*
