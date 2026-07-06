import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.cursor()

rows = cursor.execute("""
SELECT
    company_id,
    year,
    COUNT(*)
FROM profitandloss
GROUP BY company_id, year
HAVING COUNT(*) > 1
""").fetchall()

print("Duplicate Rows:", len(rows))

for row in rows[:30]:
    print(row)

conn.close()