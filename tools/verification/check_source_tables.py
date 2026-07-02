import sqlite3

conn = sqlite3.connect("db/nifty100.db")

tables = [
    "profitandloss",
    "balancesheet",
    "cashflow"
]

for table in tables:
    print(f"\n===== {table.upper()} =====")

    for row in conn.execute(f"PRAGMA table_info({table})"):
        print(row)

conn.close()