# [Chapter 02] Demand forecasting Methodology (OLS Math)

## 1. The Modeling Objective
The Demand Model (`models/demand.py`) is designed to answer a singular question: **How many Kilowatt-Hours (kWh) of electricity will EVs consume in each state by 2030?** 

Rather than using simple linear growth, we assume that technology adoption follows an **Exponential Growth Curve** during its early mass-adoption phase.

## 2. The Core Engine: np.polyfit & Log-Linear Regression
To find the Compound Annual Growth Rate (CAGR) for each state, we use **Ordinary Least Squares (OLS) Regression** on a log-transformed dataset.

### 🧠 The Mathematical Transformation
Technology adoption (Y) follows the equation:
$$Y = A \cdot e^{r \cdot t}$$
Where **r** is the growth rate. To solve for **r** using linear regression, we take the natural log of both sides:
$$\ln(Y) = \ln(A) + r \cdot t$$
This turns a curve into a straight line where the **slope (r)** is our CAGR.

### 🧠 Code Logic: The `np.polyfit` Implementation
The critical line of code in the project is:
```python
slope = np.polyfit(y_v - y_v.mean(), log_r - log_r.mean(), 1)[0]
```

### 🧠 Why Mean-Centering?
I mean-centered the data (subtracting the average year from the year array) to stabilize the variance and ensure the algorithm converges accurately on the slope.
- **Without Centering:** Calculations involving large year numbers (like 2024) can lead to rounding errors and numerical instability in the algorithm.
- **With Centering:** We shift the data so the "middle" is at 0 (e.g., 2020, 2022, 2024 becomes -2, 0, 2). This is much easier for the computer to handle accurately, reducing numerical error and making the trend-line fitting more stable.

## 3. Conversion to Energy Demand (MWh)
Once the CAGR is determined, the model projects EV registrations through 2030. We then convert vehicle counts into energy consumption:
- **Vehicle Benchmark:** We assume each EV consumes approximately **1,800 kWh per year** (based on approx 5 kWh/day × 360 days).
- **MWh Calculation:** `Total Energy (MWh) = (Projected EVs × 1,800) / 1,000`.

## 4. Scenario Multipliers
To provide flexibility for recruiters or investors, the model includes **Scenario Analysis**:
- **Base Case:** 1.0x (Standard projection).
- **Low Adoption:** 0.65x multiplier (modeling a 35% slowdown due to charging bottlenecks).
- **High Adoption:** 1.45x multiplier (modeling an aggressive "Tipping Point" scenario).

---
*Next Chapter: The Reality Guardrails — Fail-Safes and Clipping Logic.*
