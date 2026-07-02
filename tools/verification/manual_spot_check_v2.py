import sqlite3
from src.analytics.cagr import revenue_cagr

conn = sqlite3.connect("db/nifty100.db")

companies = [
    "ABB",
    "TCS",
    "APOLLOHOSP"
]

for company in companies:

    print("\n" + "=" * 60)
    print(company)
    print("=" * 60)

    # Latest common financial year (ignore TTM)
    year = conn.execute("""
    SELECT year
    FROM profitandloss
    WHERE company_id=?
      AND year!='TTM'
    ORDER BY year DESC
    LIMIT 1
    """, (company,)).fetchone()[0]

    print("Year:", year)

    # Profit & Loss
    sales, net_profit = conn.execute("""
    SELECT sales, net_profit
    FROM profitandloss
    WHERE company_id=? AND year=?
    """, (company, year)).fetchone()

    # Balance Sheet
    equity, reserves = conn.execute("""
    SELECT equity_capital, reserves
    FROM balancesheet
    WHERE company_id=? AND year=?
    """, (company, year)).fetchone()

    # Manual ROE
    manual_roe = round(
        (net_profit / (equity + reserves)) * 100,
        2
    )

    # Database ROE
    db_roe = conn.execute("""
    SELECT return_on_equity_pct
    FROM financial_ratios
    WHERE company_id=? AND year=?
    LIMIT 1
    """, (company, year)).fetchone()[0]

    # Revenue history
    rows = conn.execute("""
    SELECT sales
    FROM profitandloss
    WHERE company_id=?
      AND year!='TTM'
    ORDER BY year
    """, (company,)).fetchall()

    sales_history = [r[0] for r in rows]

    manual_revenue_cagr, _ = revenue_cagr(sales_history, 5)

    db_revenue_cagr = conn.execute("""
    SELECT revenue_cagr_5yr
    FROM financial_ratios
    WHERE company_id=? AND year=?
    LIMIT 1
    """, (company, year)).fetchone()[0]

    print("\nROE")
    print("Manual :", manual_roe)
    print("Database:", db_roe)
    print("Difference:", round(abs(manual_roe - db_roe), 2))

    print("\nRevenue CAGR")
    print("Manual :", manual_revenue_cagr)
    print("Database:", db_revenue_cagr)

conn.close()