import streamlit as st

from utils.db import (
    get_company_details,
    run_query,
)

st.title("📄 Annual Reports")

companies = get_company_details()

selected = st.selectbox(
    "Select Company",
    companies["id"] + " - " + companies["company_name"]
)

ticker = selected.split(" - ")[0]

reports = run_query(f"""
SELECT *
FROM documents
WHERE company_id='{ticker}'
""")

if reports.empty:

    st.error("No reports available.")

    st.stop()

for _, row in reports.iterrows():

    st.write(
        f"### {row['year']}"
    )

    url = row["annual_report"]

    if (
        url is None
        or url == ""
    ):

        st.error("Report unavailable")

    else:

        st.link_button(
            "Open BSE Report",
            url,
        )

    st.divider()