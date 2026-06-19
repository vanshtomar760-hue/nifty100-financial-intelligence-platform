import sqlite3

conn = sqlite3.connect("db/nifty100.db")

cursor = conn.cursor()

tables = [
    "companies",
    "analysis",
    "balancesheet",
    "cashflow",
    "documents",
    "profitandloss",
    "prosandcons",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "sectors",
    "stock_prices"
]

for table in tables:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(f"{table}: {count}")

conn.close()