# India EV Charging + Renewable Infrastructure: Investment Strategy Project

**A consulting-grade data analytics project** identifying optimal locations for EV charging and solar infrastructure investment across Indian states, using financial modelling, scenario analysis, and multi-criteria decision frameworks.

---

## 🎯 Problem Statement

> India is targeting 30% EV penetration and 500 GW renewable capacity by 2030. But **where** should infrastructure investment go to maximise financial returns, grid efficiency, and policy impact?

**Market context** (2025):
- India EV charging market: **USD 1.2 billion** (2024) → projected **USD 1.6B by 2025**, growing at **44% CAGR** to FY2029
- Government commitment: **PM E-DRIVE scheme** allocates ₹10,900 crore (FY2024–26), including ₹2,000 crore for 72,000 fast chargers
- Infrastructure gap: **1 charger per 135 EVs** in India vs. 1 per 6–20 EVs globally — massive whitespace exists
- McKinsey identifies wind-solar-storage hybrids becoming **cost-competitive with coal within 4–5 years**

---

## 📐 Analytical Framework (Implemented)

Five quantitative models, following the McKinsey/BCG consulting methodology:

```
Market Understanding → Data Analysis → Financial Model → Scenario Simulation → Strategic Recommendation
```

| Model | Method | Output |
|---|---|---|
| **1. Demand Forecasting** | Per-state exponential growth fitted to 5-yr historical EV data | EV count + MWh demand, 2025–2030 |
| **2. Solar Supply** | GHI × 365 × Performance Ratio (0.76) → MWh/MW/yr | Viable renewable capacity per state |
| **3. Financial Model** | DCF: NPV (20-yr, 10% WACC), IRR (bisection), Payback | Base economics per 10 MW installation |
| **4. Policy-Adjusted Finance** | FAME-II + state subsidies + accelerated depreciation + green certificates | Incentive-stacked IRR uplift of +2–5%pt |
| **5. Monte Carlo** | 1,000 iterations; tariff ±15%, GHI ±8%, CAPEX ±10% | IRR P10/P50/P90 distribution |
| **6. MCDA Scoring** | Weighted composite: Financial 30%, Demand 25%, Solar 20%, Policy 15%, Urban 10% | Tier 1–4 investment ranking |
| **7. Grid Stress** | Peak EV charging load vs. state peak demand; DISCOM + stability index | Grid readiness score + station gap |

---

## 📊 Key Results

**Top Investment Destinations** (Base Scenario, 10 MW solar + EV installation):

| Rank | State | Score (/100) | Tier | IRR (Base) | IRR (Policy-adj.) | Payback |
|---|---|---|---|---|---|---|
| 1 | **Karnataka** | 80.7 | Premium | 22.6% | 27.1% | 5 yrs |
| 2 | **Delhi** | 80.0 | Premium | 20.2% | 24.8% | 5 yrs |
| 3 | **Gujarat** | 78.7 | Premium | 21.2% | 25.6% | 5 yrs |
| 4 | **Maharashtra** | 75.1 | Premium | 21.7% | 26.3% | 5 yrs |
| 5 | **Tamil Nadu** | 73.0 | High | 20.0% | 24.0% | 5 yrs |

**Monte Carlo (1,000 simulations) — Telangana:**
- P10 IRR: 16.2% | P50: 23.5% | P90: 31.0% — strong risk-adjusted case

**Scenario Fan:**
- Karnataka IRR: 20.7% (Low) → 22.6% (Base) → **25.5% (High adoption)**
- Policy incentives (FAME-II + state) improve IRR by **4–5 percentage points** across top states

**Key Insight:**
> "Telangana offers the strongest base IRR (23.2%) due to high solar resource + high tariff combination; Delhi and Maharashtra win on demand scale; Rajasthan dominates solar yield (1,803 MWh/MW/yr, GHI 6.5). A phased strategy prioritising Tier 1 states first, then building utility-scale solar assets in Rajasthan and Gujarat, maximises risk-adjusted portfolio returns."

---

## 🛠 What's Built

```
consulting_project/
├── data/
│   ├── state_data.csv          ← 20 states × 20 variables
│   ├── policy_incentives.csv   ← FAME-II, state subsidies, GST waivers, etc.
│   └── year_timeseries.csv     ← 5-yr historical EV registrations (2020–2024)
├── models/
│   ├── demand.py               ← Trend-fitted CAGR forecasting
│   ├── financial.py            ← IRR/NPV/Payback + Monte Carlo + policy-adj.
│   ├── scoring.py              ← MCDA + weight sensitivity analysis
│   └── grid.py                 ← Grid stress + readiness + station gap
├── visualisations/
│   └── charts.py               ← 8 publication-quality matplotlib charts
├── dashboard/
│   └── app.py                  ← Streamlit 4-page interactive dashboard
├── reports/
│   └── generate_report.py      ← Excel report (4 sheets + conditional formatting)
├── main.py                     ← Full orchestrator (7-step pipeline)
└── outputs/
    ├── charts/                 ← 8 PNG charts
    ├── full_analysis.csv
    ├── monte_carlo_results.csv
    ├── grid_analysis.csv
    └── India_EV_Investment_Report.xlsx
```

**Run the full analysis:**
```bash
pip install -r requirements.txt
python main.py
```
**Run the interactive dashboard:**
```bash
streamlit run dashboard/app.py
```

---

## 📈 8 Charts Generated

| # | Chart | What it shows |
|---|---|---|
| 1 | Composite Score Bar | All 20 states ranked, colour-coded Tier 1–4 |
| 2 | IRR Bubble Scatter | IRR vs. tariff, bubble size = demand |
| 3 | Scenario Fan (P10–P90) | Monte Carlo IRR spread, top 8 states |
| 4 | Solar GHI Heatmap | State-level solar resource quality |
| 5 | Demand Forecast Lines | EV charging demand 2025–2030, top 6 states |
| 6 | NPV Waterfall | CAPEX → Base NPV → Policy uplift → Policy NPV |
| 7 | Monte Carlo Histogram | IRR distribution (1,000 draws) for top 3 states |
| 8 | Weight Sensitivity Tornado | How ±20% weight changes shift rankings |

---

## 🔭 Future Enhancements

### Near-Term (can add)
- **Highway Corridor Analysis**: model investment along India's NH corridors (Char Dham, Delhi-Mumbai, NH-44), where range anxiety drives greatest charger demand. PM E-DRIVE specifically targets 1 charger every 25 km.
- **Battery Swapping Model**: separate financial model for swap-station economics (lower CAPEX, higher utilisation) vs. conventional charging — especially relevant for 2W/3W fleet operators
- **Vehicle Segment Breakdown**: separate demand by 2W, 3W, 4W, commercial fleet — different charging speeds, frequency, and tariff sensitivity per segment
- **DISCOM Financial Health Integration**: weight DISCOM creditworthiness more heavily in scoring — states with financially stressed DISCOMs create payment risk for power purchase agreements

### Medium-Term
- **Corridor Heat Map**: GIS-style map (using Folium) plotting investment scores as a choropleth map overlay on India's state boundaries — visual centrepiece for presentations
- **Public-Private Partnership (PPP) Model**: model the risk-sharing structure between government VGF (Viability Gap Funding) and private capital — BCG identifies this as key to unlocking debt financing
- **Carbon Credit Revenue Stream**: Add carbon credit pricing as an additional revenue line in the financial model (CBAM-equivalent savings + Indian carbon market projections for 2027+)
- **Charger Reliability / Utilisation Model**: India has 73% charger failure rate; model the impact of utilisation rate assumptions (20–65%) on IRR — a major hidden sensitivity
- **Green Hydrogen Extension**: extend the solar model to include co-located green hydrogen electrolysis as an alternate revenue use for solar generation — emerging opportunity in Gujarat industrial clusters

### Advanced / Publication-Level
- **Decarbonisation Pathway Alignment**: overlay state-level targets with India's NDC commitments and model how EV+solar investments contribute to sector-level emission reduction targets (McKinsey framework)
- **BCG Matrix Overlay**: classify each state's EV charging investment as Star / Cash Cow / Question Mark / Dog based on market growth (EV adoption rate) vs relative competitive position (infrastructure density)
- **Real Data Integration**: plug in actual CERC/MNRE/Ember datasets via their APIs for live data refresh instead of proxy data
- **Agent-Based Market Simulation**: model CPO (Charge Point Operator) competition across states — price wars, network effects, and first-mover advantage dynamics using agent-based simulation

---

## 🧠 Interview Talking Points

> *"I built a data-driven investment strategy model evaluating EV charging and solar infrastructure deployment across 20 Indian states, using financial modelling (IRR, NPV, Monte Carlo simulation), multi-criteria scoring, and grid stress analysis — producing prioritised investment recommendations under Low/Base/High adoption scenarios."*

**Key consulting signals in this project:**
- ✅ Structured problem framing (market gap → investment question → analytical framework)
- ✅ Quantified financial model (not just descriptive)
- ✅ Scenario analysis and uncertainty quantification (Monte Carlo)
- ✅ Multi-factor decision framework (MCDA with configurable weights)
- ✅ Clear recommendation with Tier classification
- ✅ Deliverable format: Excel report + interactive dashboard

---

## 📚 Data Sources & References

- **MNRE**: Solar/wind capacity by state — [mnre.gov.in](https://mnre.gov.in)
- **Ember India**: State electricity generation and emissions — [ember-energy.org](https://ember-energy.org/data/india-electricity-data)
- **NITI Aayog ICED**: Solar irradiance by state — [iced.niti.gov.in](https://iced.niti.gov.in)
- **World Bank**: Solar PV potential maps — [datacatalog.worldbank.org](https://datacatalog.worldbank.org)
- **AIKosh**: Telangana EV charging dataset — [aikosh.indiaai.gov.in](https://aikosh.indiaai.gov.in)
- **PM E-DRIVE Scheme**: PIB, Oct 2024 — [pib.gov.in](https://pib.gov.in)
- **McKinsey**: India decarbonisation pathway reports — [mckinsey.com](https://mckinsey.com)
- **BCG**: Clean industrialisation in India — [bcg.com](https://bcg.com)
- **IMARC/PS Market Research**: EV charging market sizing — India EV Charging Station Market Report 2024

---

*Project by Saatvik Bhardwaj — BITS Pilani Hyderabad (B.E. EEE + M.Sc. Bio) | March 2026*
