import sqlite3

conn = sqlite3.connect("db/nifty100.db")

columns = [
    "ALTER TABLE financial_ratios ADD COLUMN revenue_cagr_5yr REAL;",
    "ALTER TABLE financial_ratios ADD COLUMN pat_cagr_5yr REAL;",
    "ALTER TABLE financial_ratios ADD COLUMN eps_cagr_5yr REAL;",
    "ALTER TABLE financial_ratios ADD COLUMN composite_quality_score REAL;"
]

for query in columns:
    try:
        conn.execute(query)
        print("Added:", query)
    except sqlite3.OperationalError as e:
        print(e)

conn.commit()
conn.close()

print("Schema updated successfully.")