import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

datasets = {

    "companies": {
        "file": "data/raw/companies.xlsx",
        "header": 1
    },

    "analysis": {
        "file": "data/raw/analysis.xlsx",
        "header": 1
    },

    "balancesheet": {
        "file": "data/raw/balancesheet.xlsx",
        "header": 1
    },

    "cashflow": {
        "file": "data/raw/cashflow.xlsx",
        "header": 1
    },

    "documents": {
        "file": "data/raw/documents.xlsx",
        "header": 1
    },

    "profitandloss": {
        "file": "data/raw/profitandloss.xlsx",
        "header": 1
    },

    "prosandcons": {
        "file": "data/raw/prosandcons.xlsx",
        "header": 1
    },

    "financial_ratios": {
        "file": "data/raw/financial_ratios.xlsx",
        "header": 0
    },

    "market_cap": {
        "file": "data/raw/market_cap.xlsx",
        "header": 0
    },

    "peer_groups": {
        "file": "data/raw/peer_groups.xlsx",
        "header": 0
    },

    "sectors": {
        "file": "data/raw/sectors.xlsx",
        "header": 0
    },

    "stock_prices": {
        "file": "data/raw/stock_prices.xlsx",
        "header": 0
    }
}

for table_name, config in datasets.items():

    print(f"\nLoading {table_name}...")

    df = pd.read_excel(
        config["file"],
        header=config["header"]
    )

    df.columns = [
        str(col).strip().lower()
        .replace(" ", "_")
        .replace("%", "pct")
        .replace("-", "_")
        for col in df.columns
    ]

    df.to_sql(
        table_name,
        conn,
        if_exists="append",
        index=False
    )

    print(f"Loaded {len(df)} rows")

conn.commit()
conn.close()

print("\nAll tables loaded successfully.")