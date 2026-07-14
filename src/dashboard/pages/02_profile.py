import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_company_details,
    get_ratios,
    get_pl,
    get_sectors,
    get_pros_cons,
)

st.title("🏢 Company Profile")

companies = get_company_details()

company_options = (
    companies["id"] + " - " + companies["company_name"]
).tolist()

selected = st.selectbox(
    "Search Company",
    company_options
)

ticker = selected.split(" - ")[0]

ratios = get_ratios(ticker)

pl = get_pl(ticker)

sector = get_sectors()

pros = get_pros_cons()

company_data = companies[
    companies["id"] == ticker
]

if company_data.empty:
    st.warning("Ticker not found — please try another.")
    st.stop()

company = company_data.iloc[0]

sector_info = sector[
    sector["company_id"] == ticker
]

st.markdown("---")

st.subheader(company["company_name"])

col1, col2 = st.columns(2)

with col1:
    st.write(f"**Ticker:** {ticker}")

    if not sector_info.empty:
        st.write(
            f"**Sector:** {sector_info.iloc[0]['broad_sector']}"
        )

with col2:
    st.write(
        f"**Website:** {company['website']}"
    )

st.write(company["about_company"])

if ratios.empty:
    st.warning("Financial data not available for this company.")
    st.stop()

latest = ratios.iloc[-1]

c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)

c1.metric(
    "ROE",
    f"{latest['return_on_equity_pct']:.2f}%"
)

c2.metric(
    "ROCE",
    f"{company['roce_percentage']:.2f}%"
)

c3.metric(
    "Net Profit Margin",
    f"{latest['net_profit_margin_pct']:.2f}%"
)

c4.metric(
    "Debt / Equity",
    f"{latest['debt_to_equity']:.2f}"
)

c5.metric(
    "Revenue CAGR",
    f"{latest['revenue_cagr_5yr']:.2f}%"
)

c6.metric(
    "Free Cash Flow",
    f"{latest['free_cash_flow_cr']:.0f} Cr"
)

st.markdown("---")
st.subheader("Revenue & Net Profit (10 Years)")

if not pl.empty:

    fig = px.bar(
        pl,
        x="year",
        y=["sales", "net_profit"],
        barmode="group",
        title="Revenue vs Net Profit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
else:
    st.info("Revenue and Net Profit data not available.")

st.markdown("---")
st.subheader("ROE vs ROCE")

chart = ratios.merge(
    companies[
        ["id", "roce_percentage"]
    ],
    left_on="company_id",
    right_on="id",
    how="left"
)

if not chart.empty:

    fig = px.line(
        chart,
        x="year",
        y=[
            "return_on_equity_pct",
            "roce_percentage"
        ],
        markers=True,
        title="ROE vs ROCE"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
else:
    st.info("ROE / ROCE history not available.")

st.markdown("---")
st.subheader("Pros & Cons")

company_pc = pros[
    pros["company_id"] == ticker
]

if company_pc.empty:

    st.info("No Pros & Cons available.")

else:

    pros_list = (
        company_pc["pros"]
        .dropna()
        .tolist()
    )

    cons_list = (
        company_pc["cons"]
        .dropna()
        .tolist()
    )

    left, right = st.columns(2)

    with left:
        st.success("Pros")
        for item in pros_list:
            st.markdown(f"✅ {item}")

    with right:
        st.error("Cons")
        for item in cons_list:
            st.markdown(f"❌ {item}")