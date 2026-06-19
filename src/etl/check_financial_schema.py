import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.cursor()

cursor.execute("PRAGMA table_info(financial_ratios)")

for row in cursor.fetchall():
    print(row)

conn.close()