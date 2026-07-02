import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.execute(
    "PRAGMA table_info(financial_ratios)"
)

for column in cursor.fetchall():
    print(column)

conn.close()