import re
import sqlite3
import pandas as pd

print("=" * 60)
print("NLP Analysis Parser")
print("=" * 60)

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

analysis = pd.read_sql("SELECT * FROM analysis", conn)

print(f"Rows loaded : {len(analysis)}")
print()
print(analysis.head())

fields = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

pattern = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%")

parsed_rows = []
failed_rows = []

for _, row in analysis.iterrows():

    company_id = row["company_id"]

    for field in fields:

        text = str(row[field])

        match = pattern.search(text)

        if match:

            parsed_rows.append({
                "company_id": company_id,
                "metric_type": field,
                "period_years": int(match.group(1)),
                "value_pct": float(match.group(2))
            })

        else:

            failed_rows.append({
                "company_id": company_id,
                "metric_type": field,
                "raw_text": text
            })

parsed_df = pd.DataFrame(parsed_rows)
failed_df = pd.DataFrame(failed_rows)

import os

os.makedirs("output", exist_ok=True)

parsed_df.to_csv(
    "output/analysis_parsed.csv",
    index=False
)

failed_df.to_csv(
    "output/parse_failures.csv",
    index=False
)

print()
print("analysis_parsed.csv created")
print("parse_failures.csv created")

print()
print("Parsed Records :", len(parsed_df))
print("Failed Records :", len(failed_df))

print()
print(parsed_df.head())

tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table'",
    conn
)

print("\nDatabase Tables:")
print(tables)

# -------------------------------------------------------
# Sprint Requirement:
# Cross-validate parsed CAGR values against computed CAGR
# from the Ratio Engine.
#
# Current database does not contain precomputed CAGR values
# or a dedicated Ratio Engine output table. Therefore,
# automated validation is skipped.
# -------------------------------------------------------

print()
print("CAGR cross-validation skipped (computed CAGR data not available).")