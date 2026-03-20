# [Chapter 11] Technical FAQ & Portfolio Q&A

## 1. Interview Cheat Sheet: Anticipated Questions
These are derived from common questions I addressed during the model's creation.

### 🧠 Q: Why use Monte Carlo instead of averages?
**A:** "In infrastructure projects lasting 20 years, assuming a fixed price for electricity or construction is dangerous. I used Monte Carlo to simulate **1,000 different futures**. It allows me to tell an investor not just 'You will earn 21%,' but 'I am 90% confident your return will not fall below 16%.' It changes the conversation from blind guessing to quantified risk."

### 🧠 Q: What was the hardest technical part?
**A:** "Building the custom **Bisection Algorithm** for IRR from scratch. Standard libraries often fail or stay as 'black boxes' when dealing with complex, policy-adjusted cash flow patterns (like tax shields and stacked subsidies). Creating a robust solver required deep understanding of both polynomial math and cash flow time-value."

### 🧠 Q: What is MCDA and why not just rank by IRR?
**A:** "Because highest profit doesn't mean highest *viability*. A state might have a 25% IRR on paper, but if its power grid is collapsing or its government bans subsidies tomorrow, the project fails. MCDA (Multi-Criteria Decision Analysis) mathematically balances profit with operational reality."

### 🧠 Q: How did you handle messy registration data?
**A:** "Some states had almost zero early EV adoption, which breaks log-linear regression (ln(0) = undefined). I wrote a production-grade fail-safe: if there are fewer than 2 years of valid data, the model defaults to a conservative **35% CAGR fallback**."

## 2. Technical Stack & Architecture
- **Language:** Python 3.11
- **Data Engineering:** Pandas, Numpy (OLS & Bisection)
- **UI & Visualization:** Streamlit, Matplotlib, Radar Charts
- **Reporting:** Openpyxl (Automated Excel generator)
- **AI Pillar:** Groq API (Llama-3.3-70b) with a custom TF-IDF Graph-RAG retrieval engine.

## 3. Future Enhancements (Roadmap)
If I had 2 more weeks to iterate on this:
1.  **GIS Highway Mapping:** I would integrate the `Folium` library to map high-traffic highway corridors (like the Delhi-Mumbai Expressway). Range anxiety on highways is where the biggest infrastructure gaps—and the highest premium charging revenue—actually exist.
2.  **Dynamic DISCOM API:** Connect the grid stress model to real-time utility health APIs.

## 4. Final Business Statement
"This project demonstrates the ability to bridge complex backend data engineering with C-suite level strategic advisory. It is a proof-of-concept for how data science can drive multi-million dollar capital allocation decisions in the energy sector."

---
*End of Documentation — RAG Methodology Knowledge Base.*
