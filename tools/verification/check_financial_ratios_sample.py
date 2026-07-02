import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.execute("""
SELECT *
FROM financial_ratios
LIMIT 5
""")

for row in cursor.fetchall():
    print(row)

conn.close()