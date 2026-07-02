import sqlite3

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

companies = cursor.execute("""
SELECT DISTINCT company_id
FROM profitandloss
ORDER BY company_id
""").fetchall()

for company in companies:

    company_id = company[0]

    rows = cursor.execute("""
    SELECT
        year,
        sales,
        net_profit,
        eps
    FROM profitandloss
    WHERE company_id = ?
      AND year != 'TTM'
    ORDER BY year
    """, (company_id,)).fetchall()

    # Need at least 6 yearly records to compute a 5-year CAGR
    if len(rows) < 6:
        continue

    # Calculate rolling CAGR for every year from the 6th record onwards
    for i in range(5, len(rows)):

        year = rows[i][0]

        sales_history = [r[1] for r in rows[:i + 1]]
        profit_history = [r[2] for r in rows[:i + 1]]
        eps_history = [r[3] for r in rows[:i + 1]]

        revenue_value, _ = revenue_cagr(sales_history, 5)
        pat_value, _ = pat_cagr(profit_history, 5)
        eps_value, _ = eps_cagr(eps_history, 5)

        # Composite Quality Score
        values = [
            revenue_value,
            pat_value,
            eps_value
        ]

        valid = [v for v in values if v is not None]

        if valid:
            score = round(sum(valid) / len(valid), 2)
        else:
            score = None

        cursor.execute("""
        UPDATE financial_ratios
        SET
            revenue_cagr_5yr = ?,
            pat_cagr_5yr = ?,
            eps_cagr_5yr = ?,
            composite_quality_score = ?
        WHERE company_id = ?
          AND year = ?
        """,
        (
            revenue_value,
            pat_value,
            eps_value,
            score,
            company_id,
            year
        ))

conn.commit()

print("Financial ratios updated successfully.")

conn.close()