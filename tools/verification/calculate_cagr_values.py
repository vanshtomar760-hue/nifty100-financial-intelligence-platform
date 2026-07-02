import sqlite3
from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)

conn = sqlite3.connect("db/nifty100.db")

companies = conn.execute("""
SELECT DISTINCT company_id
FROM profitandloss
ORDER BY company_id
""").fetchall()

for company in companies:

    company_id = company[0]

    rows = conn.execute("""
    SELECT
        year,
        sales,
        net_profit,
        eps
    FROM profitandloss
    WHERE company_id=?
    ORDER BY year
    """, (company_id,)).fetchall()

    sales = [r[1] for r in rows]
    profits = [r[2] for r in rows]
    eps_values = [r[3] for r in rows]

    revenue_value, revenue_flag = revenue_cagr(sales, 5)
    pat_value, pat_flag = pat_cagr(profits, 5)
    eps_value, eps_flag = eps_cagr(eps_values, 5)

    print(
        company_id,
        revenue_value,
        revenue_flag,
        pat_value,
        pat_flag,
        eps_value,
        eps_flag
    )

conn.close()