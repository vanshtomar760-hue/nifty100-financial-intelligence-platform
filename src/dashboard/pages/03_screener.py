import sys
from pathlib import Path

# -------------------------------------------------
# Add src folder to Python path
# -------------------------------------------------

SRC_PATH = Path(__file__).resolve().parents[2]

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# -------------------------------------------------
# Imports
# -------------------------------------------------


import streamlit as st
import pandas as pd

from screener.engine import run_screener


try:
    from screener.presets import (
        QUALITY_COMPOUNDER,
        VALUE_PICK,
        GROWTH_ACCELERATOR,
        DIVIDEND_CHAMPION,
        DEBT_FREE_BLUE_CHIP,
        TURNAROUND_WATCH,
    )
except ImportError:
    from src.screener.presets import (
        QUALITY_COMPOUNDER,
        VALUE_PICK,
        GROWTH_ACCELERATOR,
        DIVIDEND_CHAMPION,
        DEBT_FREE_BLUE_CHIP,
        TURNAROUND_WATCH,
    )

from utils.db import run_query
PRESETS = {
    "Quality": QUALITY_COMPOUNDER,
    "Value": VALUE_PICK,
    "Growth": GROWTH_ACCELERATOR,
    "Dividend": DIVIDEND_CHAMPION,
    "Debt-Free": DEBT_FREE_BLUE_CHIP,
    "Turnaround": TURNAROUND_WATCH,
}

# -------------------------------------------------
# Page Title
# -------------------------------------------------

st.set_page_config(layout="wide")

st.title("🔍 Stock Screener")

st.sidebar.header("Presets")

preset_name = st.sidebar.selectbox(
    "Choose Preset",
    ["Custom"] + list(PRESETS.keys())
)

selected_filters = {}

if preset_name != "Custom":
    selected_filters = PRESETS[preset_name]

# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------

st.sidebar.header("Filters")

roe = st.sidebar.slider(
    "Minimum ROE",
    0.0,
    50.0,
    15.0
)

de = st.sidebar.slider(
    "Maximum D/E",
    0.0,
    10.0,
    1.0
)

fcf = st.sidebar.number_input(
    "Minimum FCF",
    value=0
)

rev = st.sidebar.slider(
    "Revenue CAGR",
    0,
    50,
    10
)

pat = st.sidebar.slider(
    "PAT CAGR",
    0,
    50,
    10
)

opm = st.sidebar.slider(
    "Operating Margin",
    0,
    60,
    10
)

pe = st.sidebar.slider(
    "Maximum PE",
    0,
    100,
    20
)

pb = st.sidebar.slider(
    "Maximum PB",
    0,
    20,
    5
)

dividend = st.sidebar.slider(
    "Dividend Yield",
    0.0,
    10.0,
    1.0
)

icr = st.sidebar.slider(
    "Interest Coverage",
    0,
    20,
    3
)

# -------------------------------------------------
# Filter Dictionary
# -------------------------------------------------

filters = {
    "roe_min": selected_filters.get("roe_min", roe),
    "debt_to_equity_max": selected_filters.get("debt_to_equity_max", de),
    "free_cash_flow_min": selected_filters.get("free_cash_flow_min", fcf),
    "revenue_cagr_5yr_min": selected_filters.get("revenue_cagr_5yr_min", rev),
    "pat_cagr_5yr_min": selected_filters.get("pat_cagr_5yr_min", pat),
    "opm_min": selected_filters.get("opm_min", opm),
    "pe_max": selected_filters.get("pe_max", pe),
    "pb_max": selected_filters.get("pb_max", pb),
    "dividend_yield_min": selected_filters.get("dividend_yield_min", dividend),
    "interest_coverage_min": selected_filters.get("interest_coverage_min", icr),
}

# -------------------------------------------------
# Run Screener
# -------------------------------------------------

result = run_screener(filters)

display = result[
    [
        "company_id",
        "broad_sector",
        "composite_quality_score",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
    ]
]

st.markdown(
    f"### 📊 {len(result)} Companies Match Your Filters"
)

# -------------------------------------------------
# Display Results
# -------------------------------------------------

st.dataframe(
    result,
    use_container_width=True,
    hide_index=True
)

csv = display.to_csv(index=False)

st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="screener_results.csv",
    mime="text/csv",
)

# -------------------------------------------------
# Optional Database Check
# -------------------------------------------------

financial = run_query("""
SELECT *
FROM financial_ratios
""")

market = run_query("""
SELECT *
FROM market_cap
""")

sector = run_query("""
SELECT *
FROM sectors
""")

financial["market_year"] = (
    financial["year"]
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)

market["market_year"] = market["year"].astype(int)

master = financial.merge(
    market,
    on=["company_id", "market_year"],
    how="left"
)

master = master.merge(
    sector,
    on="company_id",
    how="left"
)

st.info(f"Database Records Loaded: {len(master)}")