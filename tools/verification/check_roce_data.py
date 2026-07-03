import sqlite3

conn = sqlite3.connect("db/nifty100.db")

rows = conn.execute("""
SELECT
    p.company_id,
    p.year,
    p.operating_profit,
    p.other_income,
    b.equity_capital,
    b.reserves,
    b.borrowings,
    c.roce_percentage
FROM profitandloss p
JOIN balancesheet b
ON p.company_id = b.company_id
AND p.year = b.year
JOIN companies c
ON p.company_id = c.id
LIMIT 10
""").fetchall()

for row in rows:
    print(row)

conn.close()