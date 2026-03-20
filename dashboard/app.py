"""
dashboard/app.py
Streamlit interactive dashboard — 4 pages:
  Overview | Financial Deep Dive | Demand Forecast | State Comparison
Run: streamlit run dashboard/app.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from models.demand    import build_demand_forecast, apply_scenario
from models.financial import (compute_base_financials, compute_policy_adjusted_financials,
                               run_monte_carlo)
from models.scoring   import compute_scores, weight_sensitivity
from models.grid      import compute_grid_stress

DATA_DIR = Path(__file__).parent.parent / "data"

st.set_page_config(
    page_title="India EV Investment Strategy",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F8F9FA; }
    .metric-card {
        background: white; border-radius: 10px; padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 12px;
    }
    .tier-pill {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 12px; font-weight: 600; color: white;
    }
    .tier1 { background: #1B4F8A; }
    .tier2 { background: #27AE60; }
    .tier3 { background: #E67E22; }
    .tier4 { background: #C0392B; }
    h1 { color: #1B4F8A; }
    h2 { color: #2C3E50; }
    h3 { color: #34495E; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    sd  = pd.read_csv(DATA_DIR / "state_data.csv")
    pi  = pd.read_csv(DATA_DIR / "policy_incentives.csv")
    return sd, pi

@st.cache_data
def load_and_vectorize_docs():
    import glob
    from sklearn.feature_extraction.text import TfidfVectorizer
    docs_dir = DATA_DIR.parent / "docs"
    docs_files = glob.glob(str(docs_dir / "*.md"))
    
    docs_texts = []
    docs_names = []
    for f in docs_files:
        with open(f, "r", encoding="utf-8") as file:
            docs_texts.append(file.read())
            docs_names.append(Path(f).name)
            
    if not docs_texts:
        return None, None, [], []
        
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(docs_texts)
    return vectorizer, tfidf_matrix, docs_texts, docs_names

def retrieve_top_k(query, vectorizer, tfidf_matrix, docs_texts, docs_names, k=2):
    if not vectorizer:
        return ""
    from sklearn.metrics.pairwise import cosine_similarity
    query_vec = vectorizer.transform([query])
    sim = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_k_idx = sim.argsort()[-k:][::-1]
    
    context = ""
    for idx in top_k_idx:
        if sim[idx] > 0.05:  # Only include if somewhat relevant
            context += f"\n\n--- Deep Dive Context ({docs_names[idx]}) ---\n{docs_texts[idx]}\n"
    return context.strip()

@st.cache_data
def compute_all(scenario: str, w_financial: float, w_demand: float,
                w_solar: float, w_policy: float, w_urban: float):
    sd, pi   = load_data()
    weights  = dict(financial=w_financial, demand=w_demand,
                    solar=w_solar, policy=w_policy, urban=w_urban)
    total    = sum(weights.values())
    weights  = {k: v / total for k, v in weights.items()}

    demand_base = build_demand_forecast()
    demand_df   = apply_scenario(demand_base, scenario)

    base_fin    = compute_base_financials(sd)
    policy_fin  = compute_policy_adjusted_financials(sd, pi)
    scores_df   = compute_scores(sd, base_fin, demand_df, weights=weights)
    grid_df     = compute_grid_stress(sd, demand_df)

    return sd, pi, demand_df, demand_base, base_fin, policy_fin, scores_df, grid_df


# ── Sidebar controls ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/1200px-Flag_of_India.svg.png",
             width=80)
    st.markdown("## ⚡ EV Investment Model")
    st.markdown("---")

    scenario = st.selectbox("📊 Scenario", ["Base", "Low", "High"], index=0)

    st.markdown("#### Weight Configuration")
    st.caption("Drag to adjust MCDA priorities (auto-normalised)")
    w_fin    = st.slider("Financial Returns",  0.0, 1.0, 0.30, 0.05)
    w_dem    = st.slider("EV Demand",          0.0, 1.0, 0.25, 0.05)
    w_sol    = st.slider("Solar Resource",     0.0, 1.0, 0.20, 0.05)
    w_pol    = st.slider("Policy Environment", 0.0, 1.0, 0.15, 0.05)
    w_urb    = st.slider("Urbanisation",       0.0, 1.0, 0.10, 0.05)

    total_w = w_fin + w_dem + w_sol + w_pol + w_urb
    st.caption(f"Total weight: {total_w:.2f} (auto-normalised to 1.0)")

    page = st.radio("📄 Page", ["Overview", "Financial Deep Dive",
                                 "Demand Forecast", "State Comparison"])

    st.markdown("---")
    
    # Pre-compute data for use in Export and Main Pages
    sd, pi, demand_df, demand_base, base_fin, policy_fin, scores_df, grid_df = compute_all(
        scenario, w_fin, w_dem, w_sol, w_pol, w_urb
    )

    st.markdown("#### 📥 Export Data")
    if "excel_data" not in st.session_state:
        st.session_state.excel_data = None

    if st.button("Generate Excel Report"):
        with st.spinner("Running Monte Carlo + Compiling Report..."):
            mc_df = run_monte_carlo(sd, n=1000)
            scenarios_data = {}
            for s in ["Low", "Base", "High"]:
                d_df = apply_scenario(demand_base, s)
                s_df = compute_scores(sd, base_fin, d_df)
                scenarios_data[s] = s_df[["state", "irr_pct", "demand_mwh_2029"]]
            
            from reports.generate_report import generate_excel_report
            st.session_state.excel_data = generate_excel_report(
                scores_df, base_fin, policy_fin, mc_df, scenarios_data, in_memory=True
            )

    if st.session_state.excel_data:
        st.download_button(
            label="Click here to Download .xlsx",
            data=st.session_state.excel_data,
            file_name=f"India_EV_Investment_Report_{scenario}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("India EV + Renewable Infrastructure — Investment Strategy")
    st.caption(f"Scenario: **{scenario}** | Weights: Financial {w_fin:.0%} | Demand {w_dem:.0%} | Solar {w_sol:.0%} | Policy {w_pol:.0%} | Urban {w_urb:.0%}")

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    top = scores_df.iloc[0]
    col1.metric("🥇 Top State",       top["state"],                     f"Score: {top['composite_score']:.1f}/100")
    col2.metric("📈 Best IRR",         f"{base_fin['irr_pct'].max():.1f}%", f"{base_fin.sort_values('irr_pct', ascending=False).iloc[0]['state']}")
    col3.metric("⚡ Total EV Demand",  f"{demand_df['demand_mwh_2029'].sum()/1e6:.1f} TWh/yr", "2029 Projected")
    col4.metric("🏆 Tier 1 States",    str(len(scores_df[scores_df["tier"] == "Tier 1 (Premium)"])), "Premium investment")

    # RAG Assistant: AI Technical Advisor
    st.markdown("---")
    st.subheader("🧠 AI Technical Consultant")
    st.caption("Ask our McKinsey-trained Oracle any question about this model's math, datasets, or the current state rankings.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    groq_api_key = st.secrets.get("GROQ_API_KEY", "")
    if not groq_api_key or groq_api_key == "paste_your_key_here":
        st.warning("⚠️ GROQ_API_KEY not found in Streamlit secrets.")
    else:
        if prompt_text := st.chat_input("Why is Delhi ranked so high? Or how is IRR compounded here?"):
            st.session_state.messages.append({"role": "user", "content": prompt_text})
            with st.chat_message("user"):
                st.markdown(prompt_text)

            with st.chat_message("assistant"):
                with st.spinner("Consulting methodology base..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=groq_api_key)
                        
                        # Load global baseline and dynamic TF-IDF context
                        try:
                            with open(DATA_DIR.parent / "Methodology_Context.md", "r") as f:
                                base_context = f.read()
                        except:
                            base_context = "Baseline documentation missing."
                            
                        vec, mat, txts, names = load_and_vectorize_docs()
                        deep_dive_context = retrieve_top_k(prompt_text, vec, mat, txts, names, k=2)
                        
                        context_docs = f"{base_context}\n\n{deep_dive_context}"
                            
                        top_3 = scores_df.head(3).to_dict(orient="records")
                        sys_prompt = f"""
Act as a Senior Partner at McKinsey specializing in Energy & Infrastructure. You built this investment screening model.
You are extremely technical, sharp, and concise. Use bold text for key terms.
Answer the user's questions based strictly on the following project context and formulas:

PROJECT METHODOLOGY KNOWLEDGE BASE:
{context_docs}

CURRENT APP STATE:
Scenario: {scenario}
Weights: Financial: {w_fin}, Demand: {w_dem}, Solar: {w_sol}, Policy: {w_pol}, Urbanization: {w_urb}.
Current Top 3 States: {top_3}
"""
                        api_messages = [{"role": "system", "content": sys_prompt}]
                        for m in st.session_state.messages:
                            api_messages.append({"role": m["role"], "content": m["content"]})
                            
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=api_messages,
                            temperature=0.2,
                            max_tokens=800
                        )
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"AI Chat failed: {str(e)}")

    st.markdown("---")

    # Composite score chart
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.subheader("Composite Investment Attractiveness")
        top15 = scores_df.head(15).sort_values("composite_score")
        tier_colors = {
            "Tier 1 (Premium)":  "#1B4F8A",
            "Tier 2 (High)":     "#27AE60",
            "Tier 3 (Moderate)": "#E67E22",
            "Tier 4 (Low)":      "#C0392B",
        }
        colors = [tier_colors.get(str(t), "#607D8B") for t in top15["tier"]]
        fig, ax = plt.subplots(figsize=(7, 6))
        bars = ax.barh(top15["state"], top15["composite_score"], color=colors, height=0.65)
        ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=8)
        ax.set_xlabel("Score (0–100)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlim(0, 110)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col_r:
        st.subheader("Top 5 Recommendations")
        for i, (_, row) in enumerate(scores_df.head(5).iterrows(), 1):
            tier_cls = row["tier"].lower().replace(" (", "").replace(")", "").replace(" ", "")
            irr = base_fin[base_fin["state"] == row["state"]]["irr_pct"].values
            irr_str = f"{irr[0]:.1f}%" if len(irr) > 0 else "N/A"
            st.markdown(f"""
**{i}. {row["state"]}** &nbsp; — Score: `{row['composite_score']:.1f}`
- IRR: **{irr_str}** | Policy: {row['ev_policy_score']}/10
- Tier: **{row['tier']}** | GHI: {row['solar_ghi_kwh_m2_day']} kWh/m²/day
""")

    # Grid stress table
    st.subheader("Grid Integration Readiness")
    grid_show = grid_df[["state", "grid_stress_pct", "grid_status", "readiness_score", "stations_gap"]].head(10)
    st.dataframe(grid_show.style.applymap(
        lambda v: "background-color: #C0392B; color: white" if v == "Critical"
             else ("background-color: #E67E22; color: white" if v == "Stressed" else ""),
        subset=["grid_status"]
    ), use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2: FINANCIAL DEEP DIVE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Financial Deep Dive":
    st.title("Financial Analysis — 10 MW Solar + EV Charging")
    st.caption("IRR, NPV, Policy-adjusted returns, and Monte Carlo simulation")

    # Full financials table
    merged_fin = base_fin.merge(
        policy_fin[["state", "irr_pct_policy", "npv_cr_policy", "adj_capex_cr"]], on="state"
    )
    merged_fin["irr_uplift"] = (merged_fin["irr_pct_policy"] - merged_fin["irr_pct"]).round(1)
    st.subheader("Base vs. Policy-Adjusted Returns")
    st.dataframe(merged_fin[["state", "irr_pct", "irr_pct_policy", "irr_uplift",
                              "npv_cr", "npv_cr_policy", "payback_yrs"]].rename(columns={
        "irr_pct": "Base IRR (%)", "irr_pct_policy": "Policy IRR (%)",
        "irr_uplift": "Uplift (%pt)", "npv_cr": "Base NPV (₹Cr)", 
        "npv_cr_policy": "Policy NPV (₹Cr)", "payback_yrs": "Payback (Yrs)"
    }).sort_values("Policy IRR (%)", ascending=False).reset_index(drop=True),
    use_container_width=True)

    st.markdown("---")

    # Monte Carlo for selected state
    st.subheader("Monte Carlo Simulation (1,000 iterations)")
    sel_state = st.selectbox("Select state", scores_df["state"].tolist(), index=0)
    with st.spinner("Running Monte Carlo..."):
        mc_single = run_monte_carlo(sd[sd["state"] == sel_state], n=1000)
    if not mc_single.empty:
        row = mc_single.iloc[0]
        irrs = np.array(row["irr_all"])
        c1, c2, c3 = st.columns(3)
        c1.metric("P10 IRR (Downside)",  f"{row['irr_p10']:.1f}%")
        c2.metric("P50 IRR (Median)",    f"{row['irr_p50']:.1f}%")
        c3.metric("P90 IRR (Upside)",    f"{row['irr_p90']:.1f}%")

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(irrs, bins=50, color="#1B4F8A", alpha=0.8, edgecolor="white", lw=0.3)
        ax.axvline(row["irr_p10"], color="#C0392B", lw=1.5, ls="--", label=f"P10: {row['irr_p10']:.1f}%")
        ax.axvline(row["irr_p50"], color="black",   lw=2.0, ls="-",  label=f"P50: {row['irr_p50']:.1f}%")
        ax.axvline(row["irr_p90"], color="#27AE60", lw=1.5, ls="--", label=f"P90: {row['irr_p90']:.1f}%")
        ax.set_xlabel("IRR (%)"); ax.set_ylabel("Frequency")
        ax.set_title(f"IRR Distribution — {sel_state}")
        ax.legend(); ax.spines[["top","right"]].set_visible(False)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3: DEMAND FORECAST
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Demand Forecast":
    st.title("EV Demand Forecast 2025–2030")

    top_states = st.multiselect(
        "Select states to display",
        options=demand_df["state"].tolist(),
        default=demand_df.nlargest(5, "demand_mwh_2029")["state"].tolist()
    )
    scen_compare = st.checkbox("Show Low/Base/High bands", value=True)

    if top_states:
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.tab10(np.linspace(0, 0.9, len(top_states)))

        for i, state in enumerate(top_states):
            row = demand_base[demand_base["state"] == state].iloc[0]
            yrs  = sorted(row["demand_by_year"].keys())
            base_vals = [row["demand_by_year"][y] / 1000 for y in yrs]
            ax.plot(yrs, base_vals, marker="o", lw=2, color=colors[i], label=state)

            if scen_compare:
                row_low  = apply_scenario(demand_base, "Low")[demand_base["state"] == state]
                row_high = apply_scenario(demand_base, "High")[demand_base["state"] == state]
                if not row_low.empty and not row_high.empty:
                    low_29  = float(row_low["demand_mwh_2029"].values[0]) / 1000
                    high_29 = float(row_high["demand_mwh_2029"].values[0]) / 1000
                    ax.axhspan(low_29 * 0.9, high_29 * 1.05, alpha=0.05, color=colors[i])

        ax.set_xlabel("Year"); ax.set_ylabel("EV Charging Demand (GWh/yr)")
        ax.set_title(f"EV Charging Demand Forecast — {scenario} Scenario")
        ax.legend(fontsize=9); ax.grid(alpha=0.2)
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.subheader("Demand Forecast Data Table")
    st.dataframe(demand_df[["state", "fitted_cagr", "ev_2024", "ev_2029",
                              "demand_mwh_2029"]].rename(columns={
        "fitted_cagr": "CAGR (%)", "ev_2024": "EVs 2024", "ev_2029": "EVs 2029E",
        "demand_mwh_2029": "Demand 2029 (MWh/yr)"
    }).sort_values("Demand 2029 (MWh/yr)", ascending=False).reset_index(drop=True),
    use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4: STATE COMPARISON
# ═════════════════════════════════════════════════════════════════════════════
elif page == "State Comparison":
    st.title("Side-by-Side State Comparison")

    col_a, col_b = st.columns(2)
    state_a = col_a.selectbox("State A", scores_df["state"].tolist(), index=0)
    state_b = col_b.selectbox("State B", scores_df["state"].tolist(), index=1)

    dims = ["Score (/100)", "IRR (%)", "Demand 2029 (MWh)", "Solar GHI", "Policy Score",
            "Urban %", "Grid Readiness"]

    def _get_vals(state):
        s_row  = scores_df[scores_df["state"] == state].iloc[0]
        g_row  = grid_df[grid_df["state"] == state].iloc[0]
        return [s_row["composite_score"], s_row["irr_pct"],
                s_row["demand_mwh_2029"], s_row["solar_ghi_kwh_m2_day"],
                s_row["ev_policy_score"], s_row["urban_pct"],
                g_row["readiness_score"]]

    vals_a = _get_vals(state_a)
    vals_b = _get_vals(state_b)

    comp_df = pd.DataFrame({"Dimension": dims, state_a: vals_a, state_b: vals_b})
    comp_df["Winner"] = comp_df.apply(
        lambda r: state_a if r[state_a] > r[state_b]
                  else (state_b if r[state_b] > r[state_a] else "Tie"), axis=1
    )
    st.dataframe(comp_df.style.apply(
        lambda row: ["", "background-color: #D5E8D4" if row["Winner"] == state_a else
                         ("background-color: #DAE8FC" if row["Winner"] == state_b else ""),
                     "background-color: #DAE8FC" if row["Winner"] == state_b else
                         ("background-color: #D5E8D4" if row["Winner"] == state_a else ""), ""],
        axis=1
    ), use_container_width=True)

    # Radar chart
    categories = ["Score", "IRR", "Demand", "Solar", "Policy", "Urban", "Grid"]
    angles      = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles     += angles[:1]

    def _norm(vals):
        mx = [100, 25, max(max(vals_a[2], vals_b[2]), 1), 7, 10, 100, 100]
        return [v / m * 100 for v, m in zip(vals, mx)] + [vals[0] / mx[0] * 100]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    for state, vals, color in [(state_a, vals_a, "#1B4F8A"), (state_b, vals_b, "#E8932A")]:
        nv = _norm(vals)
        ax.plot(angles, nv, lw=2, color=color, label=state)
        ax.fill(angles, nv, alpha=0.15, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=9)
    ax.set_yticklabels([])
    ax.set_title(f"{state_a} vs. {state_b}", size=12, fontweight="bold", pad=15)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
