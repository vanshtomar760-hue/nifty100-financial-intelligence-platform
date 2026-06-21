import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

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

results = []

for table in tables:

    count = pd.read_sql_query(
        f"SELECT COUNT(*) AS cnt FROM {table}",
        conn
    )["cnt"][0]

    results.append({
        "table": table,
        "rows_loaded": count,
        "rejected_rows": 0
    })

audit_df = pd.DataFrame(results)

audit_df.to_csv(
    "output/load_audit.csv",
    index=False
)

print(audit_df)

conn.close()