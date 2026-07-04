import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

rows = cursor.execute("""
SELECT
    company_id,
    year,
    return_on_equity_pct,
    debt_to_equity
FROM financial_ratios f
WHERE
    year = (
        SELECT MAX(year)
        FROM financial_ratios f2
        WHERE f2.company_id = f.company_id
    )
    AND return_on_equity_pct > 15
    AND debt_to_equity < 1
ORDER BY return_on_equity_pct DESC;
""").fetchall()

print("=" * 60)
print("SCREENER PREVIEW")
print("=" * 60)

print(f"\nCompanies Found: {len(rows)}\n")

for company in rows:
    print(company)

conn.close()