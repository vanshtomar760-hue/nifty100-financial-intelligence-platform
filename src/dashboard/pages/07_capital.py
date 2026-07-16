import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import run_query

st.title("🌳 Capital Allocation Map")

financial = run_query("""
SELECT *
FROM financial_ratios
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

def classify(row):

    roe = row["return_on_equity_pct"]
    debt = row["debt_to_equity"]
    payout = row["dividend_payout_ratio_pct"]

    if roe > 25 and debt < 0.5:
        return "High Quality Compounder"

    elif payout > 60:
        return "Dividend Champion"

    elif debt < 0.1:
        return "Debt Free"

    elif roe < 10:
        return "Turnaround"

    elif debt > 2:
        return "Highly Leveraged"

    elif row["free_cash_flow_cr"] > 0:
        return "Cash Generator"

    elif row["pat_cagr_5yr"] > 20:
        return "Growth"

    else:
        return "Balanced"

financial["Pattern"] = financial.apply(
    classify,
    axis=1
)
st.write(financial.shape)

st.write(
    financial[
        [
            "company_id",
            "Pattern",
            "free_cash_flow_cr",
            "return_on_equity_pct",
        ]
    ].head(10)
)

fig = px.treemap(
    financial,
    path=["Pattern", "company_id"],
    color="return_on_equity_pct",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

pattern = st.selectbox(
    "Capital Allocation Pattern",
    sorted(
        financial["Pattern"].unique()
    )
)

st.dataframe(
    financial[
        financial["Pattern"] == pattern
    ][
        [
            "company_id",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
        ]
    ],
    use_container_width=True,
)

