import sqlite3

conn = sqlite3.connect("db/nifty100.db")

for row in conn.execute("PRAGMA table_info(companies)"):
    print(row)

conn.close()