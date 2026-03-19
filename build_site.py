"""
build_site.py
Generates a self-contained index.html — a McKinsey-style consulting report page.
Embeds all chart PNGs as base64 so the HTML file is fully portable.
Run: python build_site.py
"""
import base64, json
from pathlib import Path
import pandas as pd

ROOT      = Path(__file__).parent
CHART_DIR = ROOT / "outputs" / "charts"
OUT_FILE  = ROOT / "index.html"

import sys
sys.path.insert(0, str(ROOT))
from models.financial import compute_base_financials
from models.demand    import build_demand_forecast

state_df  = pd.read_csv(ROOT / "data" / "state_data.csv")

# Load scoring results (has composite_score, irr_pct, tier, etc.)
analysis  = pd.read_csv(ROOT / "outputs" / "full_analysis.csv")
mc_res    = pd.read_csv(ROOT / "outputs" / "monte_carlo_results.csv")
grid_res  = pd.read_csv(ROOT / "outputs" / "grid_analysis.csv")

# Get NPV + payback from financial model
fin       = compute_base_financials(state_df)
analysis  = analysis.merge(fin[["state","npv_cr","payback_yrs"]], on="state", how="left")


top5    = analysis.sort_values("composite_score", ascending=False).head(5)
top_irr = analysis.sort_values("irr_pct", ascending=False).iloc[0]

def img64(name):
    p = CHART_DIR / f"{name}.png"
    if not p.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()

imgs = {
    "scores":   img64("1_composite_scores"),
    "bubble":   img64("2_irr_bubble_scatter"),
    "fan":      img64("3_scenario_fan_mcarlo"),
    "ghi":      img64("4_ghi_heatmap"),
    "demand":   img64("5_demand_forecast_lines"),
    "waterfall":img64("6_npv_waterfall"),
    "mc":       img64("7_monte_carlo_histogram"),
    "tornado":  img64("8_weight_sensitivity_tornado"),
}

# ── Build top-5 table rows ────────────────────────────────────────────────────
tier_badge = {
    "Tier 1 (Premium)":  ("tier1", "Tier 1 — Premium"),
    "Tier 2 (High)":     ("tier2", "Tier 2 — High"),
    "Tier 3 (Moderate)": ("tier3", "Tier 3 — Moderate"),
    "Tier 4 (Low)":      ("tier4", "Tier 4 — Low"),
}

def ranking_rows():
    rows = []
    for i, (_, r) in enumerate(top5.iterrows(), 1):
        tc, tl = tier_badge.get(str(r.get("tier", "")), ("tier3", ""))
        mc_row = mc_res[mc_res["state"] == r["state"]]
        p10 = f"{mc_row['irr_p10'].values[0]:.1f}%" if not mc_row.empty else "—"
        p90 = f"{mc_row['irr_p90'].values[0]:.1f}%" if not mc_row.empty else "—"
        rows.append(f"""
        <tr>
          <td class="rank">#{i}</td>
          <td class="state-name">{r['state']}</td>
          <td class="score-cell"><span class="score-bar-wrap"><span class="score-bar" style="width:{r['composite_score']}%"></span></span> {r['composite_score']:.1f}</td>
          <td><span class="badge {tc}">{tl}</span></td>
          <td class="metric">{r['irr_pct']:.1f}%</td>
          <td class="metric">₹{r['npv_cr']:.0f} Cr</td>
          <td class="metric">{r.get('payback_yrs','—')} yrs</td>
          <td class="metric range">{p10} – {p90}</td>
        </tr>""")
    return "\n".join(rows)

# ── HTML ──────────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>India EV + Renewable Infrastructure — Investment Strategy</title>
<meta name="description" content="Data-driven investment strategy identifying optimal EV charging and solar infrastructure deployment across Indian states, using financial modelling, Monte Carlo simulation, and multi-criteria decision analysis.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
  :root {{
    --navy:   #0F2D54;
    --blue:   #1B4F8A;
    --accent: #E8932A;
    --green:  #1E7A4A;
    --red:    #C0392B;
    --amber:  #E67E22;
    --light:  #F4F6FA;
    --border: #DDE3EE;
    --text:   #1A2332;
    --muted:  #5A6A80;
  }}
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: 'Inter', sans-serif;
    color: var(--text);
    background: #fff;
    line-height: 1.65;
  }}

  /* NAV */
  nav {{
    position: sticky; top: 0; z-index: 100;
    background: var(--navy);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 40px; height: 56px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
  }}
  nav .logo {{ color: #fff; font-weight: 700; font-size: 15px; letter-spacing: .3px; }}
  nav .logo span {{ color: var(--accent); }}
  nav ul {{ list-style: none; display: flex; gap: 28px; }}
  nav a {{ color: rgba(255,255,255,0.78); text-decoration: none; font-size: 13px; font-weight: 500; transition: color .2s; }}
  nav a:hover {{ color: #fff; }}

  /* HERO */
  .hero {{
    background: linear-gradient(135deg, var(--navy) 0%, #1a3a6e 60%, #0d2240 100%);
    color: #fff; padding: 100px 40px 80px; text-align: center;
    position: relative; overflow: hidden;
  }}
  .hero::before {{
    content: ''; position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  }}
  .hero-tag {{
    display: inline-block; background: rgba(232,147,42,0.2); color: var(--accent);
    border: 1px solid rgba(232,147,42,0.4); border-radius: 20px;
    padding: 4px 16px; font-size: 12px; font-weight: 600; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 24px;
  }}
  .hero h1 {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(28px, 5vw, 52px); font-weight: 700;
    line-height: 1.2; max-width: 860px; margin: 0 auto 20px;
  }}
  .hero h1 span {{ color: var(--accent); }}
  .hero .sub {{
    font-size: 18px; color: rgba(255,255,255,0.72); max-width: 680px;
    margin: 0 auto 48px; font-weight: 300;
  }}
  .hero-stats {{
    display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;
    margin-top: 48px;
  }}
  .hero-stat {{ text-align: center; }}
  .hero-stat .val {{
    font-size: 38px; font-weight: 800; color: #fff; line-height: 1;
    display: block; letter-spacing: -1px;
  }}
  .hero-stat .val span {{ color: var(--accent); }}
  .hero-stat .lbl {{ font-size: 13px; color: rgba(255,255,255,0.6); margin-top: 4px; }}\
  .divider {{ height: 4px; background: linear-gradient(90deg, var(--accent), var(--blue)); }}

  /* SECTIONS */
  section {{ padding: 80px 40px; max-width: 1100px; margin: 0 auto; }}
  section.full {{ max-width: 100%; padding: 80px 40px; background: var(--light); }}
  section.full .inner {{ max-width: 1100px; margin: 0 auto; }}
  .section-tag {{
    font-size: 11px; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: var(--accent); margin-bottom: 12px;
  }}
  h2.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(24px, 3vw, 38px); font-weight: 700;
    color: var(--navy); margin-bottom: 16px; line-height: 1.25;
  }}
  .section-lead {{
    font-size: 17px; color: var(--muted); max-width: 700px; margin-bottom: 48px;
  }}

  /* PROBLEM CARDS */
  .problem-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 24px;
    margin-top: 40px;
  }}
  .problem-card {{
    background: #fff; border: 1px solid var(--border); border-radius: 12px;
    padding: 28px 24px; position: relative; overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  }}
  .problem-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent);
  }}
  .problem-card .icon {{ font-size: 28px; margin-bottom: 12px; }}
  .problem-card .big {{ font-size: 28px; font-weight: 800; color: var(--navy); }}
  .problem-card .label {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}

  /* FRAMEWORK */
  .framework-steps {{
    display: flex; align-items: flex-start; gap: 0; margin-top: 40px;
    flex-wrap: wrap;
  }}
  .fw-step {{
    flex: 1; min-width: 160px; text-align: center; position: relative; padding: 0 8px;
  }}
  .fw-step:not(:last-child)::after {{
    content: '→'; position: absolute; right: -10px; top: 20px;
    font-size: 20px; color: var(--accent); font-weight: 700;
  }}
  .fw-num {{
    width: 48px; height: 48px; border-radius: 50%;
    background: var(--navy); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 16px; margin: 0 auto 12px;
  }}
  .fw-step h4 {{ font-size: 13px; font-weight: 700; color: var(--navy); margin-bottom: 6px; }}
  .fw-step p {{ font-size: 12px; color: var(--muted); line-height: 1.5; }}
  .model-pills {{
    display: flex; flex-wrap: wrap; gap: 10px; margin-top: 32px;
  }}
  .pill {{
    background: #fff; border: 1px solid var(--border); border-radius: 20px;
    padding: 6px 16px; font-size: 12px; font-weight: 600; color: var(--navy);
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }}
  .pill.highlight {{ background: var(--navy); color: #fff; border-color: var(--navy); }}

  /* RESULTS TABLE */
  .results-table {{ width: 100%; border-collapse: collapse; margin-top: 32px; font-size: 14px; }}
  .results-table thead th {{
    background: var(--navy); color: #fff; padding: 12px 16px;
    text-align: left; font-weight: 600; font-size: 12px; letter-spacing: .3px;
  }}
  .results-table thead th:first-child {{ border-radius: 8px 0 0 0; }}
  .results-table thead th:last-child {{ border-radius: 0 8px 0 0; }}
  .results-table tbody tr {{ border-bottom: 1px solid var(--border); transition: background .15s; }}
  .results-table tbody tr:hover {{ background: var(--light); }}
  .results-table td {{ padding: 14px 16px; vertical-align: middle; }}
  .rank {{ font-weight: 800; font-size: 18px; color: var(--navy); }}
  .state-name {{ font-weight: 700; color: var(--navy); font-size: 15px; }}
  .metric {{ font-weight: 600; font-size: 14px; color: var(--text); }}
  .range {{ color: var(--muted); font-size: 13px; }}
  .score-bar-wrap {{ display: inline-block; width: 80px; height: 6px; background: #e0e6f0; border-radius: 3px; vertical-align: middle; margin-right: 8px; }}
  .score-bar {{ display: block; height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--blue), var(--accent)); }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; }}
  .tier1 {{ background: #dceeff; color: var(--navy); }}
  .tier2 {{ background: #d4f0e1; color: var(--green); }}
  .tier3 {{ background: #fdebd0; color: #a04000; }}
  .tier4 {{ background: #fce8e6; color: var(--red); }}

  /* CHART GRID */
  .chart-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 32px; margin-top: 40px; }}
  .chart-card {{
    background: #fff; border-radius: 16px; border: 1px solid var(--border);
    overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  }}
  .chart-card .chart-header {{
    padding: 20px 24px 12px; border-bottom: 1px solid var(--border);
  }}
  .chart-card .chart-header h3 {{ font-size: 15px; font-weight: 700; color: var(--navy); }}
  .chart-card .chart-header p {{ font-size: 12px; color: var(--muted); margin-top: 3px; }}
  .chart-card img {{ width: 100%; display: block; padding: 8px 0; }}
  .chart-single {{ grid-column: 1 / -1; }}

  /* KEY INSIGHTS */
  .insight-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 32px; }}
  .insight-card {{
    background: #fff; border-left: 4px solid var(--accent); border-radius: 0 12px 12px 0;
    padding: 20px 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  }}
  .insight-card h4 {{ font-size: 13px; font-weight: 700; color: var(--navy); margin-bottom: 8px; text-transform: uppercase; letter-spacing: .5px; }}
  .insight-card p {{ font-size: 14px; color: var(--muted); line-height: 1.6; }}
  .insight-card strong {{ color: var(--navy); }}

  /* RECOMMENDATIONS */
  .reco-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-top: 40px; }}
  @media (max-width: 768px) {{ .reco-grid {{ grid-template-columns: 1fr; }} }}
  .reco-card {{
    background: #fff; border-radius: 16px; padding: 32px 28px;
    border: 1px solid var(--border); position: relative;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  }}
  .reco-card .phase-tag {{
    font-size: 11px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: var(--accent); margin-bottom: 10px;
  }}
  .reco-card h3 {{ font-size: 18px; font-weight: 700; color: var(--navy); margin-bottom: 12px; }}
  .reco-card p {{ font-size: 14px; color: var(--muted); line-height: 1.65; }}
  .reco-card .metric-tag {{
    display: inline-block; background: var(--light); color: var(--navy);
    border-radius: 8px; padding: 4px 12px; font-size: 12px; font-weight: 700;
    margin-top: 16px;
  }}
  .reco-card.highlight-card {{ background: var(--navy); border-color: var(--navy); }}
  .reco-card.highlight-card .phase-tag {{ color: var(--accent); }}
  .reco-card.highlight-card h3, .reco-card.highlight-card p {{ color: rgba(255,255,255,0.9); }}
  .reco-card.highlight-card .metric-tag {{ background: rgba(255,255,255,0.12); color: #fff; }}

  /* SOURCES */
  .sources-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 32px; }}
  .source-item {{
    display: flex; align-items: flex-start; gap: 12px;
    background: #fff; border: 1px solid var(--border); border-radius: 10px; padding: 16px;
  }}
  .source-item .src-icon {{ font-size: 20px; flex-shrink: 0; }}
  .source-item h5 {{ font-size: 13px; font-weight: 700; color: var(--navy); }}
  .source-item p {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
  .source-item a {{ font-size: 12px; color: var(--blue); }}

  /* FOOTER */
  footer {{
    background: var(--navy); color: rgba(255,255,255,0.65);
    text-align: center; padding: 40px 40px 32px; font-size: 13px;
  }}
  footer strong {{ color: #fff; }}
  footer .footer-links {{ margin-top: 12px; display: flex; gap: 24px; justify-content: center; flex-wrap: wrap; }}
  footer a {{ color: rgba(255,255,255,0.5); text-decoration: none; font-size: 12px; }}

  /* RESPONSIVE */
  @media (max-width: 768px) {{
    .chart-grid {{ grid-template-columns: 1fr; }}
    .framework-steps {{ gap: 16px; }}
    .fw-step:not(:last-child)::after {{ display: none; }}
    nav ul {{ display: none; }}
  }}
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <div class="logo">⚡ India EV <span>Investment Strategy</span></div>
  <ul>
    <li><a href="#problem">Problem</a></li>
    <li><a href="#methodology">Methodology</a></li>
    <li><a href="#results">Results</a></li>
    <li><a href="#recommendations">Recommendations</a></li>
    <li><a href="#sources">Sources</a></li>
  </ul>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-tag">Consulting Analytics</div>
  <h1>India <span>EV Charging</span> + Renewable Infrastructure<br>Investment Strategy</h1>
  <p class="sub">A data-driven framework to identify optimal locations for EV charging and solar investment across 20 Indian states — using financial modelling, Monte Carlo simulation, and multi-criteria decision analysis.</p>
  <div class="hero-stats">
    <div class="hero-stat"><span class="val">20</span><div class="lbl">States Analysed</div></div>
    <div class="hero-stat"><span class="val"><span>₹</span>4.5B+</span><div class="lbl">Investment Opportunity</div></div>
    <div class="hero-stat"><span class="val">1000<span>×</span></span><div class="lbl">Monte Carlo Iterations</div></div>
    <div class="hero-stat"><span class="val">22.6<span>%</span></span><div class="lbl">Top State IRR</div></div>
    <div class="hero-stat"><span class="val">5</span><div class="lbl">Yr Payback Period</div></div>
  </div>
</div>
<div class="divider"></div>

<!-- PROBLEM STATEMENT -->
<section id="problem">
  <div class="section-tag">The Problem</div>
  <h2 class="section-title">India's EV boom needs infrastructure — but where exactly?</h2>
  <p class="section-lead">India is targeting 30% EV penetration and 500 GW of renewable capacity by 2030. Capital is available. The question is where to deploy it for maximum financial and strategic impact.</p>
  <div class="problem-grid">
    <div class="problem-card">
      <div class="icon">🔌</div>
      <div class="big">135:1</div>
      <div class="label">EVs per public charger in India — vs 6–20:1 globally. The infrastructure gap is enormous.</div>
    </div>
    <div class="problem-card" style="border-top-color: var(--blue)">
      <div class="icon">📈</div>
      <div class="big">44%</div>
      <div class="label">CAGR of India's EV charging market (FY2024–29). Growing faster than most tech sectors.</div>
    </div>
    <div class="problem-card" style="border-top-color: var(--green)">
      <div class="icon">🏛️</div>
      <div class="big">₹10,900 Cr</div>
      <div class="label">PM E-DRIVE scheme allocation (FY2024–26), targeting 72,000 fast chargers nationwide.</div>
    </div>
    <div class="problem-card" style="border-top-color: #8e44ad">
      <div class="icon">⚡</div>
      <div class="big">500 GW</div>
      <div class="label">India's 2030 renewable target. Solar + EV co-investment creates compounding returns.</div>
    </div>
    <div class="problem-card" style="border-top-color: var(--red)">
      <div class="icon">📊</div>
      <div class="big">73%</div>
      <div class="label">EV owners reporting failed charging attempts — reliability is as big a gap as coverage.</div>
    </div>
    <div class="problem-card" style="border-top-color: var(--amber)">
      <div class="icon">💰</div>
      <div class="big">$1.2B</div>
      <div class="label">India EV charging market size (2024). Projected $1.6B by 2025 — rapid expansion underway.</div>
    </div>
  </div>
</section>

<!-- METHODOLOGY -->
<section class="full" id="methodology">
  <div class="inner">
    <div class="section-tag">Methodology</div>
    <h2 class="section-title">A five-step consulting analytical framework</h2>
    <p class="section-lead">Modelled on McKinsey/BCG frameworks for infrastructure investment — combining bottom-up financial analysis with scenario simulation and structured decision scoring.</p>
    <div class="framework-steps">
      <div class="fw-step">
        <div class="fw-num">1</div>
        <h4>Market Understanding</h4>
        <p>EV demand estimation using 5-year historical registration trends with state-level exponential growth fitting</p>
      </div>
      <div class="fw-step">
        <div class="fw-num">2</div>
        <h4>Solar Supply Analysis</h4>
        <p>GHI-based solar yield calculation (PR = 0.76), viable capacity estimation per state</p>
      </div>
      <div class="fw-step">
        <div class="fw-num">3</div>
        <h4>Financial Modelling</h4>
        <p>20-yr DCF, IRR (bisection solver), NPV at 10% WACC, policy-adjusted incentive stacking (FAME-II + subsidies)</p>
      </div>
      <div class="fw-step">
        <div class="fw-num">4</div>
        <h4>Scenario Simulation</h4>
        <p>Monte Carlo (1,000 iterations); tariff ±15%, GHI ±8%, CAPEX ±10% — yielding P10/P50/P90 IRR distributions</p>
      </div>
      <div class="fw-step">
        <div class="fw-num">5</div>
        <h4>Strategic Scoring</h4>
        <p>MCDA: weighted composite across Financial (30%), Demand (25%), Solar (20%), Policy (15%), Urban (10%)</p>
      </div>
    </div>
    <div style="margin-top:40px">
      <p style="font-size:13px;color:var(--muted);margin-bottom:12px;font-weight:600;">MODELS BUILT:</p>
      <div class="model-pills">
        <span class="pill highlight">Demand Forecasting</span>
        <span class="pill highlight">IRR / NPV / Payback</span>
        <span class="pill highlight">Monte Carlo (1,000 iter)</span>
        <span class="pill highlight">Policy-Adjusted IRR</span>
        <span class="pill highlight">MCDA Scoring</span>
        <span class="pill highlight">Grid Stress Analysis</span>
        <span class="pill">7 quantitative models</span>
        <span class="pill">20 states × 20 variables</span>
        <span class="pill">3 scenarios (Low / Base / High)</span>
        <span class="pill">8 analytical charts</span>
      </div>
    </div>
  </div>
</section>

<!-- RESULTS -->
<section id="results">
  <div class="section-tag">Key Results</div>
  <h2 class="section-title">State-level investment rankings</h2>
  <p class="section-lead">Composite attractiveness scores across 20 states, based on financial returns, EV demand trajectory, solar resource, policy environment, and urbanisation. All figures for a 10 MW solar + EV charging installation.</p>

  <table class="results-table">
    <thead>
      <tr>
        <th>Rank</th><th>State</th><th>Score</th><th>Tier</th>
        <th>IRR (Base)</th><th>20-yr NPV</th><th>Payback</th><th>Monte Carlo (P10–P90)</th>
      </tr>
    </thead>
    <tbody>
      {ranking_rows()}
    </tbody>
  </table>

  <p style="font-size:12px;color:var(--muted);margin-top:12px;">
    ✦ IRR based on 10 MW installation, ₹4.5 Cr/MW CAPEX, 20-yr project life, 10% WACC, 0.5% annual degradation. Monte Carlo samples 1,000 draws with tariff ±15%, GHI ±8%, CAPEX ±10% uncertainty.
  </p>
</section>

<!-- CHARTS -->
<section class="full">
  <div class="inner">
    <div class="section-tag">Visual Analysis</div>
    <h2 class="section-title">From the data</h2>
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3>Investment Attractiveness — All 20 States</h3>
          <p>Composite MCDA score. Tier 1 (navy) = Premium, Tier 2 (green) = High, Tier 3 (orange) = Moderate, Tier 4 (red) = Low</p>
        </div>
        <img src="{imgs['scores']}" alt="Composite Score Bar Chart" loading="lazy">
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>IRR vs. Grid Tariff — Bubble Chart</h3>
          <p>X-axis = state electricity tariff (₹/kWh). Y-axis = base IRR (%). Bubble size ∝ projected EV demand. Colour = composite score.</p>
        </div>
        <img src="{imgs['bubble']}" alt="IRR Bubble Chart" loading="lazy">
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>Monte Carlo IRR — P10 / Median / P90 Range</h3>
          <p>Horizontal bars show the full uncertainty band for each state's IRR under 1,000 simulated scenarios. Wider bar = more sensitivity to input assumptions.</p>
        </div>
        <img src="{imgs['fan']}" alt="Monte Carlo Fan Chart" loading="lazy">
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>Solar Resource — GHI Heatmap</h3>
          <p>Global Horizontal Irradiance (kWh/m²/day) by state. Higher GHI → higher solar yield per MW → better project economics. Rajasthan leads at 6.5.</p>
        </div>
        <img src="{imgs['ghi']}" alt="GHI Heatmap" loading="lazy">
      </div>
      <div class="chart-card chart-single">
        <div class="chart-header">
          <h3>EV Charging Demand Forecast 2025–2030 — Top States</h3>
          <p>Trend-fitted CAGR per state applied to 2024 registration base. Delhi and Maharashtra lead on absolute demand; Karnataka and Tamil Nadu show the highest trailing growth rates.</p>
        </div>
        <img src="{imgs['demand']}" alt="Demand Forecast" loading="lazy">
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>NPV Waterfall — Karnataka (10 MW)</h3>
          <p>How value is built: CAPEX outflow → gross NPV → policy incentive uplift (FAME-II + state subsidies + accelerated depreciation + green certificates) → final adjusted NPV.</p>
        </div>
        <img src="{imgs['waterfall']}" alt="NPV Waterfall" loading="lazy">
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>Monte Carlo Histograms — Top 3 States</h3>
          <p>IRR distribution across 1,000 scenarios. The spread reflects input uncertainty. All three states show IRR > 15% even at P10 — robust investment case.</p>
        </div>
        <img src="{imgs['mc']}" alt="Monte Carlo Histogram" loading="lazy">
      </div>
    </div>
  </div>
</section>

<!-- KEY INSIGHTS -->
<section>
  <div class="section-tag">Analytical Insights</div>
  <h2 class="section-title">What the data tells us</h2>
  <div class="insight-grid">
    <div class="insight-card">
      <h4>Policy incentives are material</h4>
      <p>FAME-II + state subsidies + accelerated depreciation uplift IRR by <strong>+4–5 percentage points</strong> across top states — turning an 18% base case into a 22–27% policy-adjusted return. Delhi, Maharashtra, and Karnataka benefit most.</p>
    </div>
    <div class="insight-card">
      <h4>Solar resource ≠ highest IRR</h4>
      <p>Rajasthan leads on solar yield (1,803 MWh/MW/yr, GHI 6.5) but ranks below Karnataka and Delhi on composite score because <strong>demand depth and policy environment</strong> are equally decisive. Rajasthan is optimal for utility-scale capacity, not urban fast-charging.</p>
    </div>
    <div class="insight-card">
      <h4>IRR is robust under uncertainty</h4>
      <p>Monte Carlo results show top states deliver <strong>IRR &gt; 15% even at P10</strong> (downside scenario). Karnataka's P10 is 16.0%, P90 is 30.2% — confirming a strong risk-adjusted investment case with limited downside exposure.</p>
    </div>
    <div class="insight-card">
      <h4>Grid stress is the hidden constraint</h4>
      <p>Delhi's EV charging load reaches <strong>135% of current peak demand</strong> by 2029 — the highest grid stress of any state. Phase 1 investments in Delhi must include grid reinforcement as a co-investment requirement, or face utilisation risk.</p>
    </div>
    <div class="insight-card">
      <h4>High adoption scenario is transformative</h4>
      <p>Under the High EV adoption trajectory, Karnataka's IRR rises from 22.6% to <strong>25.5%</strong>. This confirms that EV adoption policy (FAME-III, GST cuts) is the single most powerful lever governments can pull to improve infrastructure economics.</p>
    </div>
    <div class="insight-card">
      <h4>Station supply gap is severe</h4>
      <p>Delhi needs <strong>51,000 additional charging stations</strong> by 2029 to serve projected EV demand at 1 charger per 10 EVs. Gujarat and Tamil Nadu each require 36,000–38,000. Current government targets of 72,000 total nationwide are structurally insufficient.</p>
    </div>
  </div>
</section>

<!-- RECOMMENDATIONS -->
<section class="full" id="recommendations">
  <div class="inner">
    <div class="section-tag">Strategic Recommendation</div>
    <h2 class="section-title">A phased investment strategy</h2>
    <p class="section-lead">Capital deployment sequenced by risk-adjusted return, grid readiness, and policy leverage — modelled after BCG's "Stars → Scale → Extend" framework for infrastructure rollout.</p>
    <div class="reco-grid">
      <div class="reco-card highlight-card">
        <div class="phase-tag">Phase 1 — Years 1–2</div>
        <h3>Anchor in Tier 1 Urban Markets</h3>
        <p>Deploy 10–50 MW installations in Karnataka, Delhi, Gujarat, and Maharashtra. These states combine high tariffs (7.5–8.5 ₹/kWh), strong policy environments (score 8–9/10), and deep EV demand. Fastest payback at 5 years, IRR 20–27%.</p>
        <span class="metric-tag">₹450–2,250 Cr capital | IRR 20–27%</span>
      </div>
      <div class="reco-card">
        <div class="phase-tag">Phase 2 — Years 2–4</div>
        <h3>Build Utility-Scale Solar in Sun Belt</h3>
        <p>Develop large-scale solar + EV charging hubs in Rajasthan and Gujarat. GHI &gt; 6.0 makes these the lowest cost-per-MWh locations. Co-locate with highway corridors (PM E-DRIVE mandates 1 charger per 25 km on NH routes).</p>
        <span class="metric-tag">Lower LCOE | Long-term capacity</span>
      </div>
      <div class="reco-card">
        <div class="phase-tag">Phase 3 — Years 3–5</div>
        <h3>Capture Tier 2 Growth Markets</h3>
        <p>Expand into Tamil Nadu, Telangana, and Andhra Pradesh as EV fleets scale. These states offer CAGR &gt; 60% on EV registrations and improving DISCOM health scores — creating a more investable grid environment than current metrics suggest.</p>
        <span class="metric-tag">High growth | 20–23% IRR</span>
      </div>
    </div>
  </div>
</section>

<!-- SOURCES -->
<section id="sources">
  <div class="section-tag">Sources & Citations</div>
  <h2 class="section-title">Data & references</h2>
  <p class="section-lead">All analysis uses publicly available government, research, and industry data. No proprietary datasets.</p>
  <div class="sources-grid">
    <div class="source-item">
      <div class="src-icon">🏛️</div>
      <div>
        <h5>PM E-DRIVE Scheme</h5>
        <p>Ministry of Heavy Industries, ₹10,900 Cr EV acceleration scheme (Oct 2024)</p>
        <a href="https://pib.gov.in" target="_blank">pib.gov.in →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">☀️</div>
      <div>
        <h5>MNRE — Renewable Capacity Data</h5>
        <p>State-wise installed renewable capacity, solar irradiance maps</p>
        <a href="https://mnre.gov.in" target="_blank">mnre.gov.in →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">🔬</div>
      <div>
        <h5>Ember India Electricity Data</h5>
        <p>State-level electricity generation, demand, and emissions (2020–2024)</p>
        <a href="https://ember-energy.org" target="_blank">ember-energy.org →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">🌍</div>
      <div>
        <h5>NITI Aayog — Solar Potential</h5>
        <p>ICED portal solar resource maps, GHI by district and state</p>
        <a href="https://iced.niti.gov.in" target="_blank">iced.niti.gov.in →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">📊</div>
      <div>
        <h5>IMARC / PS Market Research</h5>
        <p>India EV Charging Station Market Report 2024 — $1.2B market size, 44% CAGR</p>
        <a href="https://www.imarcgroup.com" target="_blank">imarcgroup.com →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">🚗</div>
      <div>
        <h5>AIKosh — EV Registration Data</h5>
        <p>Telangana and pan-India EV registration datasets (2020–2024)</p>
        <a href="https://aikosh.indiaai.gov.in" target="_blank">aikosh.indiaai.gov.in →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">💡</div>
      <div>
        <h5>Tata Power EV Charging</h5>
        <p>EV charging station ROI benchmarks (25–50% IRR range), industry economics</p>
        <a href="https://www.tatapower.com" target="_blank">tatapower.com →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">📋</div>
      <div>
        <h5>McKinsey & BCG India Reports</h5>
        <p>India decarbonisation pathway; clean industrialisation investment frameworks</p>
        <a href="https://www.mckinsey.com" target="_blank">mckinsey.com →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">🏗️</div>
      <div>
        <h5>Ministry of Power — EV Guidelines 2024</h5>
        <p>Revised EV charging infrastructure guidelines, Sept 2024 — mandates, interoperability, tariff framework</p>
        <a href="https://powermin.gov.in" target="_blank">powermin.gov.in →</a>
      </div>
    </div>
    <div class="source-item">
      <div class="src-icon">🌐</div>
      <div>
        <h5>World Bank — Solar Potential Maps</h5>
        <p>Global solar irradiance datasets, India state-level GHI benchmarks</p>
        <a href="https://datacatalog.worldbank.org" target="_blank">datacatalog.worldbank.org →</a>
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <strong>India EV + Renewable Infrastructure — Investment Strategy</strong><br>
  Built by Shashwat Bhardwaj &nbsp;·&nbsp; B.E. EEE + M.Sc. Biological Sciences &nbsp;·&nbsp; BITS Pilani Hyderabad Campus &nbsp;·&nbsp; 2026
  <div class="footer-links">
    <a href="#problem">Problem</a>
    <a href="#methodology">Methodology</a>
    <a href="#results">Results</a>
    <a href="#recommendations">Recommendations</a>
    <a href="#sources">Sources</a>
  </div>
</footer>

</body>
</html>"""

OUT_FILE.write_text(html, encoding="utf-8")
print(f"✓  Built: {OUT_FILE}")
print(f"   Size:  {OUT_FILE.stat().st_size / 1024:.0f} KB")
