import sqlite3

conn = sqlite3.connect("db/nifty100.db")

companies = [
    "ABB",
    "TCS",
    "APOLLOHOSP"
]

for company in companies:

    print(f"\n========== {company} ==========")

    # Latest P&L record
    pnl = conn.execute("""
    SELECT
        year,
        sales,
        net_profit
    FROM profitandloss
    WHERE company_id=?
    ORDER BY year DESC
    LIMIT 1
    """,(company,)).fetchone()

    # Latest Balance Sheet
    bs = conn.execute("""
    SELECT
        equity_capital,
        reserves
    FROM balancesheet
    WHERE company_id=?
    ORDER BY year DESC
    LIMIT 1
    """,(company,)).fetchone()

    # Financial Ratios
    ratio = conn.execute("""
    SELECT
        return_on_equity_pct,
        revenue_cagr_5yr
    FROM financial_ratios
    WHERE company_id=?
    LIMIT 1
    """,(company,)).fetchone()

    year,sales,profit = pnl
    equity,reserves = bs

    manual_roe = round(
        (profit/(equity+reserves))*100,
        2
    )

    print("Year:",year)
    print("Manual ROE:",manual_roe)
    print("Database ROE:",ratio[0])
    print("Revenue CAGR:",ratio[1])

conn.close()