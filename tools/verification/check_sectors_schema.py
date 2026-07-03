import sqlite3

conn = sqlite3.connect("db/nifty100.db")

print("===== SCHEMA =====")

for row in conn.execute("PRAGMA table_info(sectors)"):
    print(row)

print("\n===== SAMPLE DATA =====")

rows = conn.execute("""
SELECT *
FROM sectors
LIMIT 10
""").fetchall()

for row in rows:
    print(row)

conn.close()