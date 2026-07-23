import os
import sqlite3
import pandas as pd

from tearsheet import TearsheetGenerator

DB_PATH = "db/nifty100.db"

OUTPUT_DIR = "reports/tearsheets"

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

companies = pd.read_sql(
    """
    SELECT id
    FROM companies
    ORDER BY id
    """,
    conn
)

generator = TearsheetGenerator()

print(f"Companies Found : {len(companies)}")

generated = 0

skipped = []

for company in companies["id"]:

    years = pd.read_sql(
        """
        SELECT COUNT(*) AS cnt
        FROM financial_ratios
        WHERE company_id=?
        """,
        conn,
        params=(company,)
    ).iloc[0]["cnt"]

    if years < 3:

        skipped.append({
            "company": company,
            "reason": "Less than 3 years of data"
        })

        print(f"Skipped {company}")

        continue

    try:

        generator.create_pdf(company)

        generated += 1

        print(f"✓ {company}")

    except Exception as e:

        skipped.append({
            "company": company,
            "reason": str(e)
        })

        print(f"✗ {company} -> {e}")


pd.DataFrame(skipped).to_csv(
    "output/skipped_tearsheets.csv",
    index=False
)

print()

print("Skipped :", len(skipped))

print()

print("Generation Complete")

print("Reports :", generated)