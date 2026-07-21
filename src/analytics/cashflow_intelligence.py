import os
import sqlite3
import pandas as pd

from cashflow_kpis import (
    calculate_free_cash_flow,
    calculate_cfo_quality_score,
    calculate_capex_intensity,
    calculate_fcf_conversion_rate,
    calculate_fcf_cagr,
    classify_capital_allocation
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

company_list = sorted(cashflow["company_id"].unique())

def latest(df):
    return df.sort_values("year").iloc[-1]


def last_five(df):
    return df.sort_values("year").tail(5)

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
    _, _, _, capital_label = classify_capital_allocation(
        latest_cf["operating_activity"],
        latest_cf["investing_activity"],
        latest_cf["financing_activity"],
        cfo_label
    )

    # -----------------------------
    # Sector
    # -----------------------------
    sector = "Unknown"

    # -----------------------------
    # Store Results
    # -----------------------------
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

print("\n" + "=" * 60)
print("Cash Flow Intelligence Complete")
print("=" * 60)

print(f"Companies Processed : {len(results_df)}")
print(f"Distress Alerts     : {len(distress_df)}")

print("\nOutput Files")
print("----------------------------")
print("output/cashflow_intelligence.xlsx")
print("output/distress_alerts.csv")