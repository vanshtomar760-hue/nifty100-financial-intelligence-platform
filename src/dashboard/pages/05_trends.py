import streamlit as st
import plotly.graph_objects as go

from utils.db import (
    get_company_details,
    get_ratios,
)

st.title("📈 Trend Analysis")

companies = get_company_details()

selected = st.selectbox(
    "Select Company",
    companies["id"] + " - " + companies["company_name"]
)

ticker = selected.split(" - ")[0]

df = get_ratios(ticker)

if df.empty:
    st.warning("No financial history available.")
    st.stop()

metrics = [
    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
]

selected_metrics = st.multiselect(
    "Choose up to 3 metrics",
    metrics,
    default=["return_on_equity_pct"],
    max_selections=3
)

fig = go.Figure()

for metric in selected_metrics:

    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df[metric],
            mode="lines+markers",
            name=metric,
        )
    )
    for i in range(1, len(df)):

        previous = df.iloc[i - 1][metric]
        current = df.iloc[i][metric]

    if previous != 0:

        yoy = ((current - previous) / abs(previous)) * 100

        fig.add_annotation(
            x=df.iloc[i]["year"],
            y=current,
            text=f"{yoy:.1f}%",
            showarrow=False,
            font=dict(size=10),
        )

fig.update_layout(
    title="Financial Trends",
    xaxis_title="Year",
    yaxis_title="Value",
)

st.plotly_chart(
    fig,
    use_container_width=True
)