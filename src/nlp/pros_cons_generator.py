import sqlite3
import pandas as pd
import os

print("=" * 60)
print("NLP Pros & Cons Generator")
print("=" * 60)

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

# Load required tables
companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
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

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

print(f"Companies           : {len(companies)}")
print(f"Financial Ratios    : {len(financial_ratios)}")
print(f"Profit & Loss       : {len(profit_loss)}")
print(f"Balance Sheet       : {len(balance_sheet)}")
print(f"Cash Flow           : {len(cashflow)}")

os.makedirs("output", exist_ok=True)
print("\nCompanies Columns:")
print(companies.columns.tolist())

pros_cons = []

# ---------------- Helper Functions ---------------- #

def latest(df):
    return df.sort_values("year").iloc[-1]


def last_n(df, n):
    return df.sort_values("year").tail(n)


def increasing(values):
    values = list(values)
    return all(values[i] < values[i + 1] for i in range(len(values) - 1))


def decreasing(values):
    values = list(values)
    return all(values[i] > values[i + 1] for i in range(len(values) - 1))


def all_positive(values):
    return all(v > 0 for v in values)


def all_negative(values):
    return all(v < 0 for v in values)


def add_record(company, typ, rule_id, text, confidence):
    if confidence >= 60:
        pros_cons.append({
            "company_id": company,
            "type": typ,
            "rule_id": rule_id,
            "text": text,
            "confidence_pct": confidence
        })


# ---------------- Rule Engine ---------------- #

company_list = sorted(financial_ratios["company_id"].unique())

for company in company_list:

    ratio = financial_ratios[
        financial_ratios.company_id == company
    ].sort_values("year")

    pnl = profit_loss[
        profit_loss.company_id == company
    ].sort_values("year")

    bs = balance_sheet[
        balance_sheet.company_id == company
    ].sort_values("year")

    cf = cashflow[
        cashflow.company_id == company
    ].sort_values("year")

    if ratio.empty:
        continue

    latest_ratio = latest(ratio)
    latest_pnl = latest(pnl) if not pnl.empty else None
    latest_bs = latest(bs) if not bs.empty else None

    # =====================================================
    # PRO RULE 1
    # ROE >20 for last 3 years
    # =====================================================

    roe3 = last_n(ratio, 3)

    if len(roe3) == 3:

        if all(roe3["return_on_equity_pct"] > 20):

            add_record(
                company,
                "pro",
                "PRO_1",
                "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
                95
            )

    # =====================================================
    # PRO RULE 2
    # Positive FCF for last 5 years
    # =====================================================

    fcf5 = last_n(ratio, 5)

    if len(fcf5) == 5:

        if all_positive(fcf5["free_cash_flow_cr"]):

            add_record(
                company,
                "pro",
                "PRO_2",
                "Strong free cash flow generation over 5 years signals healthy business fundamentals.",
                92
            )

    # =====================================================
    # PRO RULE 3
    # Debt Free
    # =====================================================

    if latest_ratio["debt_to_equity"] == 0:

        add_record(
            company,
            "pro",
            "PRO_3",
            "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
            94
        )

    # =====================================================
    # PRO RULE 4
    # Revenue CAGR
    # =====================================================

    if latest_ratio["revenue_cagr_5yr"] > 15:

        add_record(
            company,
            "pro",
            "PRO_4",
            "Revenue growing above 15% CAGR over 5 years reflects strong business momentum.",
            90
        )

    # =====================================================
    # PRO RULE 5
    # OPM
    # =====================================================

    if latest_ratio["operating_profit_margin_pct"] > 25:

        add_record(
            company,
            "pro",
            "PRO_5",
            "Operating profit margin above 25% indicates strong pricing power and cost discipline.",
            88
        )

    # =====================================================
    # PRO RULE 6
    # PAT CAGR
    # =====================================================

    if latest_ratio["pat_cagr_5yr"] > 20:

        add_record(
            company,
            "pro",
            "PRO_6",
            "Net profit compounding above 20% over five years creates significant shareholder value.",
            91
        )

        # =====================================================
    # PRO RULE 7
    # Interest Coverage > 10 OR Debt Free
    # =====================================================

    if (
        latest_ratio["interest_coverage"] > 10
        or latest_ratio["debt_to_equity"] == 0
    ):

        add_record(
            company,
            "pro",
            "PRO_7",
            "Very high interest coverage ratio reflects negligible financial stress from debt servicing.",
            88
        )

    # =====================================================
    # PRO RULE 8
    # Dividend payout + Positive FCF
    # (Dividend Yield unavailable, using payout ratio)
    # =====================================================

    if (
        latest_ratio["free_cash_flow_cr"] > 0
        and latest_ratio["dividend_payout_ratio_pct"] > 20
    ):

        add_record(
            company,
            "pro",
            "PRO_8",
            "Positive free cash flow supports sustainable shareholder distributions.",
            82
        )

    # =====================================================
    # PRO RULE 9
    # EPS CAGR
    # =====================================================

    if latest_ratio["eps_cagr_5yr"] > 15:

        add_record(
            company,
            "pro",
            "PRO_9",
            "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding.",
            90
        )

    # =====================================================
    # PRO RULE 10
    # ROE improving 3 years
    # =====================================================

    if len(roe3) == 3:

        if increasing(roe3["return_on_equity_pct"]):

            add_record(
                company,
                "pro",
                "PRO_10",
                "Return on equity improving for three consecutive years shows strengthening business quality.",
                87
            )

    # =====================================================
    # PRO RULE 11
    # Revenue CAGR > PAT CAGR (as specified)
    # =====================================================

    if latest_ratio["revenue_cagr_5yr"] > latest_ratio["pat_cagr_5yr"]:

        add_record(
            company,
            "pro",
            "PRO_11",
            "Revenue growth outpacing profit growth indicates improving operating leverage potential.",
            75
        )

    # =====================================================
    # PRO RULE 12
    # Assets increasing while borrowings decreasing
    # =====================================================

    if len(bs) >= 3:

        assets = last_n(bs, 3)["total_assets"]
        debt = last_n(bs, 3)["borrowings"]

        if increasing(assets) and decreasing(debt):

            add_record(
                company,
                "pro",
                "PRO_12",
                "Growing asset base funded with declining debt reflects self-sustaining growth.",
                90
            )

    # =====================================================
    # CON RULE 1
    # D/E > 2
    # (Sector unavailable, applies to all companies)
    # =====================================================

    if latest_ratio["debt_to_equity"] > 2:

        add_record(
            company,
            "con",
            "CON_1",
            f"Debt-to-equity ratio of {latest_ratio['debt_to_equity']:.2f} is elevated and warrants monitoring.",
            90
        )

    # =====================================================
    # CON RULE 2
    # Negative FCF for 3 years
    # =====================================================

    fcf3 = last_n(ratio, 3)

    if len(fcf3) == 3:

        if all_negative(fcf3["free_cash_flow_cr"]):

            add_record(
                company,
                "con",
                "CON_2",
                "Free cash flow negative for three consecutive years raises concern about cash generation quality.",
                92
            )

    # =====================================================
    # CON RULE 3
    # OPM declining
    # =====================================================

    opm3 = last_n(ratio, 3)

    if len(opm3) == 3:

        if decreasing(opm3["operating_profit_margin_pct"]):

            add_record(
                company,
                "con",
                "CON_3",
                "Operating margins declining for three consecutive years suggest pricing or cost pressure.",
                85
            )

    # =====================================================
    # CON RULE 4
    # Net profit loss
    # =====================================================

    if latest_pnl is not None:

        if latest_pnl["net_profit"] < 0:

            add_record(
                company,
                "con",
                "CON_4",
                "Company reported a net loss in the most recent financial year.",
                95
            )

    # =====================================================
    # CON RULE 5
    # Revenue declining
    # =====================================================

    sales2 = last_n(pnl, 2)

    if len(sales2) == 2:

        if decreasing(sales2["sales"]):

            add_record(
                company,
                "con",
                "CON_5",
                "Revenue contraction over two consecutive years indicates weakening business momentum.",
                82
            )

    # =====================================================
    # CON RULE 6
    # Interest Coverage
    # =====================================================

    if latest_ratio["interest_coverage"] < 1.5:

        add_record(
            company,
            "con",
            "CON_6",
            "Interest coverage ratio below 1.5x indicates elevated debt servicing risk.",
            94
        )
        # =====================================================
    # CON RULE 7
    # Dividend payout > 100%
    # =====================================================

    if latest_ratio["dividend_payout_ratio_pct"] > 100:

        add_record(
            company,
            "con",
            "CON_7",
            "Dividend payout ratio above 100% may not be sustainable over the long term.",
            90
        )

    # =====================================================
    # CON RULE 8
    # Debt increasing for 3 consecutive years
    # =====================================================

    if len(bs) >= 3:

        debt3 = last_n(bs, 3)["borrowings"]

        if increasing(debt3):

            add_record(
                company,
                "con",
                "CON_8",
                "Borrowings have increased for three consecutive years, indicating rising leverage.",
                85
            )

    # =====================================================
    # CON RULE 9
    # EPS declining for 3 years
    # =====================================================

    if len(pnl) >= 3:

        eps3 = last_n(pnl, 3)["eps"]

        if decreasing(eps3):

            add_record(
                company,
                "con",
                "CON_9",
                "Earnings per share declining for three consecutive years reflects weakening profitability.",
                88
            )

    # =====================================================
    # CON RULE 10
    # ROCE < 10%
    # =====================================================

    company_info = companies[
        companies["company_name"] == company
    ]

    if not company_info.empty:

        roce = company_info.iloc[0]["roce_percentage"]

        if pd.notna(roce):

            if roce < 10:

                add_record(
                    company,
                    "con",
                    "CON_10",
                    "Return on capital employed below 10% indicates weak capital efficiency.",
                    92
                )

    # =====================================================
    # CON RULE 11
    # NOT IMPLEMENTED
    # Net Debt > 3x EBITDA
    # Missing in database
    # =====================================================

    # Skipped
    # Required fields:
    # Net Debt
    # EBITDA

    # =====================================================
    # CON RULE 12
    # Revenue CAGR < 5%
    # =====================================================

    if latest_ratio["revenue_cagr_5yr"] < 5:

        add_record(
            company,
            "con",
            "CON_12",
            "Revenue growth below 5% over five years suggests weak business momentum.",
            90
        )

# =====================================================
# Convert to DataFrame
# =====================================================

pros_cons_df = pd.DataFrame(pros_cons)

# =====================================================
# Verification
# Every company must have at least one Pro and one Con
# =====================================================

for company in company_list:

    company_rows = pros_cons_df[
        pros_cons_df["company_id"] == company
    ]

    if "pro" not in company_rows["type"].values:

        pros_cons_df.loc[len(pros_cons_df)] = {
            "company_id": company,
            "type": "pro",
            "rule_id": "FALLBACK_PRO",
            "text": "No major strengths identified using the available financial rules.",
            "confidence_pct": 60
        }

    if "con" not in company_rows["type"].values:

        pros_cons_df.loc[len(pros_cons_df)] = {
            "company_id": company,
            "type": "con",
            "rule_id": "FALLBACK_CON",
            "text": "No significant financial risks identified using the available financial rules.",
            "confidence_pct": 60
        }

# =====================================================
# Save CSV
# =====================================================

pros_cons_df = pros_cons_df.sort_values(
    ["company_id", "type"]
)

pros_cons_df.to_csv(
    "output/pros_cons_generated.csv",
    index=False
)

print("\n" + "=" * 60)
print("Pros & Cons Generation Complete")
print("=" * 60)

print(f"Total Records : {len(pros_cons_df)}")
print(
    f"Companies Covered : {pros_cons_df['company_id'].nunique()}"
)

print("\nOutput File:")
print("output/pros_cons_generated.csv")

print("\nUnsupported Rules")
print("----------------------------")
print("PRO_8 : Dividend Yield unavailable (used payout ratio + FCF)")
print("CON_1 : Financial sector classification unavailable")
print("CON_11: Net Debt & EBITDA unavailable")

conn.close()