import sqlite3

conn = sqlite3.connect("db/nifty100.db")

rows = conn.execute("""
SELECT
company_id,
year,
revenue_cagr_5yr,
pat_cagr_5yr,
eps_cagr_5yr,
composite_quality_score
FROM financial_ratios
WHERE revenue_cagr_5yr IS NOT NULL
LIMIT 10
""").fetchall()

for row in rows:
    print(row)

conn.close()