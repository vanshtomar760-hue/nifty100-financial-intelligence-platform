import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Nifty 100 Analytics Dashboard")

st.sidebar.success(
    "Select a page from the sidebar."
)

st.write(
    """
    Welcome to the Nifty 100 Financial Intelligence Dashboard.

    Use the navigation menu on the left to explore:
    - Home
    - Company Profile
    - Screener
    - Peer Comparison
    - Trend Analysis
    - Sector Analysis
    - Capital Allocation
    - Annual Reports
    """
)