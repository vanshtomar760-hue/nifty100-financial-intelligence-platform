import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[2]

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import run_query

st.title("👥 Peer Comparison")

# --------------------------------------------------
# Load Data
# --------------------------------------------------

peer = run_query("""
SELECT *
FROM peer_percentiles
""")

financial = run_query("""
SELECT *
FROM financial_ratios
""")

benchmark = run_query("""
SELECT *
FROM peer_groups
""")

financial["year_num"] = (
    financial["year"]
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)

financial = (
    financial
    .sort_values("year_num")
    .drop_duplicates(
        subset="company_id",
        keep="last"
    )
)

# --------------------------------------------------
# Peer Group Dropdown
# --------------------------------------------------

groups = sorted(
    peer["peer_group_name"]
    .dropna()
    .unique()
)

selected_group = st.selectbox(
    "Peer Group",
    groups
)

group_df = peer[
    peer["peer_group_name"] == selected_group
]

# --------------------------------------------------
# Company Dropdown
# --------------------------------------------------

companies = sorted(
    group_df["company_id"]
    .unique()
)

selected_company = st.selectbox(
    "Select Company",
    companies
)

# --------------------------------------------------
# Radar Data
# --------------------------------------------------

metrics = [
    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "composite_quality_score",
]

company = financial[
    financial["company_id"] == selected_company
]

peer_companies = financial[
    financial["company_id"].isin(companies)
]

company_values = (
    company[metrics]
    .iloc[0]
    .tolist()
)

peer_average = (
    peer_companies[metrics]
    .mean()
    .tolist()
)

labels = [
    "ROE",
    "OPM",
    "NPM",
    "D/E",
    "FCF",
    "PAT CAGR",
    "Revenue CAGR",
    "Composite",
]

# --------------------------------------------------
# Radar Chart
# --------------------------------------------------

st.subheader("Radar Chart")

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_values,
        theta=labels,
        fill="toself",
        name=selected_company,
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=peer_average,
        theta=labels,
        line=dict(dash="dash"),
        name="Peer Average",
    )
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True
        )
    ),
    showlegend=True,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# --------------------------------------------------
# KPI Table
# --------------------------------------------------

st.subheader("Peer Comparison Table")

table = peer_companies[
    [
        "company_id",
        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "pat_cagr_5yr",
        "revenue_cagr_5yr",
        "composite_quality_score",
    ]
]

table = table.merge(
    benchmark[
        [
            "company_id",
            "is_benchmark",
        ]
    ],
    on="company_id",
    how="left",
)

def highlight(row):
    if row["is_benchmark"]:
        return ["background-color: gold"] * len(row)
    return [""] * len(row)

st.dataframe(
    table.style.apply(
        highlight,
        axis=1,
    ),
    use_container_width=True,
    hide_index=True,
)