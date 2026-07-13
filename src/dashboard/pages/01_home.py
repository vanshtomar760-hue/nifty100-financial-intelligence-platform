import streamlit as st
import plotly.express as px
import pandas as pd

from utils.db import (
    get_market_cap,
    get_sectors,
    run_query,
)

st.title("🏠 Home Dashboard")

# --------------------------
# Sidebar Year Selector
# --------------------------

year = st.sidebar.selectbox(
    "Select Year",
    [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ],
    index=5,
)

# --------------------------
# Load Financial Ratios
# --------------------------

ratios = run_query(
    """
    SELECT *
    FROM financial_ratios
    WHERE year = ?
    """,
    [year]
)

market = get_market_cap()

sectors = get_sectors()

st.markdown("---")
st.subheader("Sector Breakdown")

sector_count = (
    sectors.groupby("broad_sector")
    .size()
    .reset_index(name="Companies")
)

fig = px.pie(
    sector_count,
    names="broad_sector",
    values="Companies",
    hole=0.5,
    title="Nifty 100 Sector Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("---")
st.subheader("Top 5 Companies by Composite Quality Score")

top5 = (
    ratios.sort_values(
        "composite_quality_score",
        ascending=False
    )[
        [
            "company_id",
            "composite_quality_score",
            "return_on_equity_pct",
            "revenue_cagr_5yr"
        ]
    ]
    .head(5)
)

st.dataframe(
    top5,
    use_container_width=True,
    hide_index=True
)

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric(
    "Average ROE",
    f"{ratios['return_on_equity_pct'].mean():.2f}%"
)

col2.metric(
    "Median P/E",
    f"{market['pe_ratio'].median():.2f}"
)

col3.metric(
    "Median D/E",
    f"{ratios['debt_to_equity'].median():.2f}"
)

col4.metric(
    "Total Companies",
    ratios["company_id"].nunique()
)

col5.metric(
    "Median Revenue CAGR",
    f"{ratios['revenue_cagr_5yr'].median():.2f}%"
)

col6.metric(
    "Debt-Free Companies",
    (ratios["debt_to_equity"] <= 0).sum()
)