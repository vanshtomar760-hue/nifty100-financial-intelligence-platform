import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

companies = [
    "ABB",
    "TCS",
    "INFY",
    "RELIANCE",
    "HDFCBANK"
]

for company in companies:

    print("=" * 80)
    print(company)
    print("=" * 80)

    row = cursor.execute("""
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year DESC
    LIMIT 1
    """, (company,)).fetchone()

    print(row)
    print()

conn.close()