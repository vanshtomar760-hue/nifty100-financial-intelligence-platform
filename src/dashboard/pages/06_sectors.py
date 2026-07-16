import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import run_query

st.title("🏭 Sector Analysis")

# --------------------------------------------------
# Load Tables
# --------------------------------------------------

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

pl = run_query("""
SELECT
    company_id,
    year,
    sales,
    net_profit
FROM profitandloss
""")

# --------------------------------------------------
# Prepare Financial Data
# --------------------------------------------------

financial["year_num"] = (
    financial["year"]
    .str.extract(r"(\d{4})")[0]
)

financial["year_num"] = pd.to_numeric(
    financial["year_num"],
    errors="coerce"
)

financial = financial.dropna(subset=["year_num"])

financial["year_num"] = financial["year_num"].astype(int)

financial = (
    financial
    .sort_values("year_num")
    .drop_duplicates(
        subset="company_id",
        keep="last"
    )
)

# --------------------------------------------------
# Prepare Market Data
# --------------------------------------------------

market["market_year"] = pd.to_numeric(
    market["year"],
    errors="coerce"
)

market = market.dropna(subset=["market_year"])

market["market_year"] = market["market_year"].astype(int)

# --------------------------------------------------
# Prepare Profit & Loss Data
# --------------------------------------------------

pl["market_year"] = (
    pl["year"]
    .str.extract(r"(\d{4})")[0]
)

pl["market_year"] = pd.to_numeric(
    pl["market_year"],
    errors="coerce"
)

pl = pl.dropna(subset=["market_year"])

pl["market_year"] = pl["market_year"].astype(int)

# --------------------------------------------------
# Merge
# --------------------------------------------------

financial["market_year"] = financial["year_num"]

master = financial.merge(
    market[
        [
            "company_id",
            "market_year",
            "market_cap_crore",
            "pe_ratio",
            "pb_ratio",
            "ev_ebitda",
            "dividend_yield_pct",
        ]
    ],
    on=["company_id", "market_year"],
    how="left",
)

master = master.merge(
    pl[
        [
            "company_id",
            "market_year",
            "sales",
            "net_profit",
        ]
    ],
    on=["company_id", "market_year"],
    how="left",
)

master = master.merge(
    sector,
    on="company_id",
    how="left",
)

# --------------------------------------------------
# Sector Selector
# --------------------------------------------------

sector_name = st.selectbox(
    "Select Sector",
    sorted(
        master["broad_sector"]
        .dropna()
        .unique()
    )
)

sector_df = master[
    master["broad_sector"] == sector_name
].copy()

# Remove rows missing required values
sector_df = sector_df.dropna(
    subset=[
        "sales",
        "return_on_equity_pct",
        "market_cap_crore",
    ]
)

# --------------------------------------------------
# Bubble Chart
# --------------------------------------------------

st.subheader("Sector Bubble Chart")

fig = px.scatter(
    sector_df,
    x="sales",
    y="return_on_equity_pct",
    size="market_cap_crore",
    color="sub_sector",
    hover_name="company_id",
    hover_data=[
        "market_cap_crore",
        "sales",
        "return_on_equity_pct",
    ],
    title=f"{sector_name} Companies",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# --------------------------------------------------
# Sector Median KPIs
# --------------------------------------------------

st.subheader("Sector Median KPIs")

median = (
    sector_df[
        [
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "operating_profit_margin_pct",
        ]
    ]
    .median()
    .reset_index()
)

median.columns = [
    "Metric",
    "Median",
]

fig = px.bar(
    median,
    x="Metric",
    y="Median",
    text_auto=".2f",
    title=f"{sector_name} Median KPIs",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)