import os
import sqlite3
import pandas as pd

from cashflow_kpis import (
    calculate_free_cash_flow,
    calculate_cfo_quality_score,
    calculate_capex_intensity,
    calculate_fcf_conversion_rate,
    calculate_fcf_cagr,
    classify_capital_allocation,
    generate_capital_allocation_csv
)

print("=" * 60)
print("Cash Flow Intelligence")
print("=" * 60)

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

profit_loss = pd.read_sql(
    "SELECT * FROM profitandloss",
    conn
)

balance_sheet = pd.read_sql(
    "SELECT * FROM balancesheet",
    conn
)

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print(f"Companies        : {len(companies)}")
print(f"Cash Flow        : {len(cashflow)}")
print(f"Profit & Loss    : {len(profit_loss)}")
print(f"Balance Sheet    : {len(balance_sheet)}")
print(f"Financial Ratios : {len(financial_ratios)}")

os.makedirs("output", exist_ok=True)

results = []
distress_alerts = []

company_list = sorted(
    financial_ratios["company_id"].unique()
)
print("Companies to process:", len(company_list))

def latest(df):
    return df.sort_values("year").iloc[-1]


def last_five(df):
    return df.sort_values("year").tail(5)

capital_allocation_records = []

for company in company_list:

    cf = cashflow[
        cashflow.company_id == company
    ].sort_values("year")

    pnl = profit_loss[
        profit_loss.company_id == company
    ].sort_values("year")

    bs = balance_sheet[
        balance_sheet.company_id == company
    ].sort_values("year")

    ratios = financial_ratios[
        financial_ratios.company_id == company
    ].sort_values("year")

    # Skip companies with missing essential data
    if cf.empty or pnl.empty or bs.empty:
        continue

    cf5 = last_five(cf)
    pnl5 = last_five(pnl)
    bs5 = last_five(bs)

    latest_cf = latest(cf)
    latest_pnl = latest(pnl)
    latest_bs = latest(bs)

    # -----------------------------
    # Free Cash Flow (5 years)
    # -----------------------------
    fcf_values = []

    for _, row in cf5.iterrows():

        fcf = calculate_free_cash_flow(
            row["operating_activity"],
            row["investing_activity"]
        )

        fcf_values.append(fcf)

    fcf_cagr = calculate_fcf_cagr(fcf_values)

    # -----------------------------
    # CFO Quality
    # -----------------------------
    cfo_score, cfo_label = calculate_cfo_quality_score(
        list(cf5["operating_activity"]),
        list(pnl5["net_profit"])
    )

    # -----------------------------
    # CapEx Intensity
    # -----------------------------
    capex_pct, capex_label = calculate_capex_intensity(
        latest_cf["investing_activity"],
        latest_pnl["sales"]
    )

    # -----------------------------
    # FCF Conversion
    # -----------------------------
    latest_fcf = calculate_free_cash_flow(
        latest_cf["operating_activity"],
        latest_cf["investing_activity"]
    )

    fcf_conversion = calculate_fcf_conversion_rate(
        latest_fcf,
        latest_pnl["operating_profit"]
    )
        # -----------------------------
    # Distress Signal
    # -----------------------------
    distress_flag = (
        latest_cf["operating_activity"] < 0
        and latest_cf["financing_activity"] > 0
    )

    # -----------------------------
    # Deleveraging
    # -----------------------------
    deleveraging_flag = False

    if len(bs5) >= 2:

        previous_bs = bs5.iloc[-2]

        if (
            latest_cf["financing_activity"] < 0
            and latest_bs["borrowings"] < previous_bs["borrowings"]
        ):
            deleveraging_flag = True

    # -----------------------------
    # Capital Allocation
    # -----------------------------
    
    # ---------------------------------
# Capital Allocation (All Years)
# ---------------------------------

    for _, cf_row in cf.iterrows():

        year = cf_row["year"]

        pnl_year = pnl[pnl["year"] == year]

        if pnl_year.empty:
         continue

        cfo = cf_row["operating_activity"]
        cfi = cf_row["investing_activity"]
        cff = cf_row["financing_activity"]

        cfo_sign, cfi_sign, cff_sign, pattern = classify_capital_allocation(
            cfo,
            cfi,
            cff,
            cfo_label
        )

        capital_allocation_records.append({
            "company_id": company,
            "year": year,
            "cfo_sign": cfo_sign,
            "cfi_sign": cfi_sign,
            "cff_sign": cff_sign,
            "pattern_label": pattern
        })

    # Latest year label for cashflow_intelligence.xlsx
    capital_label = capital_allocation_records[-1]["pattern_label"]

    # -----------------------------
    # Sector
    # -----------------------------
    sector = "Unknown"

    # -----------------------------
    # Store Results
    # -----------------------------
    print(company)
    results.append({
        "company_id": company,
        "sector": sector,
        "cfo_quality_score": cfo_score,
        "cfo_quality_label": cfo_label,
        "capex_intensity_pct": capex_pct,
        "capex_label": capex_label,
        "fcf_cagr_5yr": fcf_cagr,
        "fcf_conversion_pct": fcf_conversion,
        "distress_flag": distress_flag,
        "deleveraging_flag": deleveraging_flag,
        "capital_allocation_label": capital_label
    })

    if distress_flag:

        distress_alerts.append({
            "company_id": company,
            "cfo_value": latest_cf["operating_activity"],
            "cff_value": latest_cf["financing_activity"],
            "latest_net_profit": latest_pnl["net_profit"]
        })

results_df = pd.DataFrame(results)
distress_df = pd.DataFrame(distress_alerts)

results_df.to_excel(
    "output/cashflow_intelligence.xlsx",
    index=False
)

distress_df.to_csv(
    "output/distress_alerts.csv",
    index=False
)
generate_capital_allocation_csv(capital_allocation_records)

# ==========================================================
# Capital Allocation Distribution Summary
# ==========================================================

capital_df = pd.DataFrame(capital_allocation_records)

latest_year = capital_df["year"].max()

latest_patterns = capital_df[
    capital_df["year"] == latest_year
]

summary = (
    latest_patterns["pattern_label"]
    .value_counts()
    .reset_index()
)

summary.columns = [
    "capital_allocation_pattern",
    "company_count"
]

summary.to_csv(
    "output/capital_allocation_summary.csv",
    index=False
)

print("\nCapital Allocation Summary")
print(summary)


# ==========================================================
# Pattern Changes Report
# ==========================================================

pattern_changes = []

for company in capital_df["company_id"].unique():

    company_df = (
        capital_df[
            capital_df["company_id"] == company
        ]
        .sort_values("year")
    )

    if len(company_df) < 2:
        continue

    previous = company_df.iloc[-2]
    latest = company_df.iloc[-1]

    if previous["pattern_label"] != latest["pattern_label"]:

        pattern_changes.append({
            "company_id": company,
            "previous_year": previous["year"],
            "latest_year": latest["year"],
            "previous_pattern": previous["pattern_label"],
            "latest_pattern": latest["pattern_label"]
        })

pattern_changes_df = pd.DataFrame(pattern_changes)

pattern_changes_df.to_csv(
    "output/pattern_changes.csv",
    index=False
)

print(f"\nPattern Changes : {len(pattern_changes_df)}")


print("\n" + "=" * 60)
print("Cash Flow Intelligence Complete")
print("=" * 60)

print(f"Companies Processed : {len(results_df)}")
print(f"Distress Alerts     : {len(distress_df)}")

print("\nOutput Files")
print("----------------------------")
print("output/cashflow_intelligence.xlsx")
print("output/distress_alerts.csv")