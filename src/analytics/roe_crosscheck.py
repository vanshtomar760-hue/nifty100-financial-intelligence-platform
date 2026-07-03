import sqlite3
from src.analytics.ratios import calculate_roe

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

with open("output/ratio_edge_cases.log", "a") as log_file:

    companies = cursor.execute("""
    SELECT id, roe_percentage
    FROM companies
    ORDER BY id
    """).fetchall()

    anomaly_count = 0

    for company_id, source_roe in companies:

        if source_roe is None:
            continue

        row = cursor.execute("""
        SELECT
            p.year,
            p.net_profit,
            b.equity_capital,
            b.reserves
        FROM profitandloss p
        JOIN balancesheet b
            ON p.company_id = b.company_id
           AND p.year = b.year
        WHERE p.company_id = ?
          AND p.year != 'TTM'
        ORDER BY CAST(SUBSTR(p.year,-4) AS INTEGER) DESC
        LIMIT 1
        """, (company_id,)).fetchone()

        if row is None:
            continue

        year, net_profit, equity, reserves = row

        if net_profit is None:
            continue

        equity = (equity or 0) + (reserves or 0)

        if equity <= 0:
            continue

        calculated_roe = calculate_roe(
            net_profit,
            equity
        )

        if calculated_roe is None:
            continue

        difference = abs(calculated_roe - source_roe)

        if difference > 5:

            anomaly_count += 1

            if source_roe < 1:
                category = "Source Value Anomaly"

            elif difference > 15:
                category = "Version Difference"

            elif difference > 8:
                category = "Formula Discrepancy"

            else:
                category = "Data Source Issue"

            log_file.write(
                "\n========== ROE CHECK ==========\n"
                f"Company: {company_id}\n"
                f"Year: {year}\n"
                f"Calculated ROE: {round(calculated_roe,2)}\n"
                f"Source ROE: {round(source_roe,2)}\n"
                f"Difference: {round(difference,2)}\n"
                f"Category: {category}\n"
                "----------------------------------------\n"
            )

print(f"ROE anomalies logged: {anomaly_count}")

conn.close()