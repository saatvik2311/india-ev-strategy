#!/usr/bin/env bash
# ============================================================
#  India EV + Renewable Investment Strategy — Project Launcher
#  Usage: bash run.sh [--analysis-only | --dashboard-only]
# ============================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

banner() {
  echo ""
  echo -e "${BLUE}${BOLD}======================================================================${RESET}"
  echo -e "${BLUE}${BOLD}   ⚡  INDIA EV + RENEWABLE INFRASTRUCTURE — INVESTMENT MODEL  ⚡   ${RESET}"
  echo -e "${BLUE}${BOLD}======================================================================${RESET}"
  echo ""
}

step() { echo -e "${GREEN}▶ $1${RESET}"; }
info() { echo -e "${YELLOW}  $1${RESET}"; }

banner

MODE="full"
if [[ "$1" == "--analysis-only" ]]; then MODE="analysis"; fi
if [[ "$1" == "--dashboard-only" ]]; then MODE="dashboard"; fi

# ── 1. Check Python ──────────────────────────────────────────────────────────
step "Checking Python environment..."
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
  echo "❌  Python not found. Install Python 3.9+ and try again."
  exit 1
fi
PYTHON=$(command -v python3 || command -v python)
info "Using: $($PYTHON --version)"

# ── 2. Install dependencies ──────────────────────────────────────────────────
step "Installing dependencies..."
$PYTHON -m pip install -q pandas numpy matplotlib streamlit openpyxl scipy 2>/dev/null \
  && info "All packages ready." \
  || { echo "⚠️  pip install had warnings (continuing anyway)"; }

# ── 3. Run full analysis pipeline ───────────────────────────────────────────
if [[ "$MODE" == "full" || "$MODE" == "analysis" ]]; then
  echo ""
  step "Running full analysis pipeline (7 steps)..."
  echo -e "  ${YELLOW}This will:${RESET}"
  info "  [1] Load state + policy data (20 states × 20 variables)"
  info "  [2] Forecast EV demand 2025–2030 (per-state exponential fit)"
  info "  [3] Compute base financial model (IRR, NPV, Payback)"
  info "  [4] Run policy-adjusted financials (FAME-II, subsidies, green certs)"
  info "  [5] Monte Carlo simulation — 1,000 iterations per state"
  info "  [6] MCDA location scoring + weight sensitivity"
  info "  [7] Grid stress analysis"
  info "  [8] Generate 8 charts → outputs/charts/"
  info "  [9] Generate Excel report → outputs/India_EV_Investment_Report.xlsx"
  echo ""
  $PYTHON main.py
  echo ""
  step "Analysis complete. Outputs:"
  info "  📊  outputs/charts/        (8 PNG charts)"
  info "  📄  outputs/full_analysis.csv"
  info "  📄  outputs/monte_carlo_results.csv"
  info "  📄  outputs/grid_analysis.csv"
  info "  📋  outputs/India_EV_Investment_Report.xlsx"

  # Open charts folder on Mac
  if command -v open &>/dev/null; then
    echo ""
    info "Opening outputs folder..."
    open outputs/
  fi
fi

# ── 4. Launch Streamlit dashboard ────────────────────────────────────────────
if [[ "$MODE" == "full" || "$MODE" == "dashboard" ]]; then
  echo ""
  step "Launching interactive dashboard..."
  echo -e "  ${YELLOW}Dashboard has 4 pages:${RESET}"
  info "  📌 Overview        — Ranked states, KPI cards, grid readiness"
  info "  💰 Financial       — IRR table, live Monte Carlo for any state"
  info "  📈 Demand Forecast — Multi-state EV demand lines, scenario bands"
  info "  🔍 State Comparison — Side-by-side radar chart of any 2 states"
  echo ""
  info "Opening at: http://localhost:8501"
  info "Press Ctrl+C to stop the dashboard."
  echo ""
  $PYTHON -m streamlit run dashboard/app.py \
    --server.headless false \
    --browser.gatherUsageStats false \
    --theme.base light \
    --theme.primaryColor "#1B4F8A"
fi
