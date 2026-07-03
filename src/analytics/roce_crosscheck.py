import sqlite3
from src.analytics.ratios import calculate_roce

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

with open("output/ratio_edge_cases.log", "w") as log_file:

    companies = cursor.execute("""
    SELECT id, roce_percentage
    FROM companies
    ORDER BY id
    """).fetchall()

    anomaly_count = 0

    for company_id, source_roce in companies:

        if source_roce is None:
            continue

        row = cursor.execute("""
        SELECT
            p.year,
            p.operating_profit,
            p.other_income,
            b.equity_capital,
            b.reserves,
            b.borrowings
        FROM profitandloss p
        JOIN balancesheet b
          ON p.company_id = b.company_id
         AND p.year = b.year
        WHERE p.company_id = ?
          AND p.year != 'TTM'
        ORDER BY CAST(SUBSTR(p.year, -4) AS INTEGER) DESC
        LIMIT 1
        """, (company_id,)).fetchone()

        if row is None:
            continue

        (
            year,
            operating_profit,
            other_income,
            equity,
            reserves,
            borrowings
        ) = row

        if operating_profit is None:
            continue

        other_income = other_income or 0
        equity = equity or 0
        reserves = reserves or 0
        borrowings = borrowings or 0

        capital_employed = equity + reserves + borrowings

        if capital_employed <= 0:
            continue

        ebit = operating_profit + other_income

        calculated_roce = calculate_roce(
            ebit,
            capital_employed
        )

        if calculated_roce is None:
            continue

        difference = abs(calculated_roce - source_roce)

        if difference > 5:

            anomaly_count += 1

            if difference > 15:
                category = "Version Difference"
            elif difference > 8:
                category = "Formula Discrepancy"
            else:
                category = "Data Source Issue"

            log_file.write(
                f"Company: {company_id}\n"
                f"Year: {year}\n"
                f"Calculated ROCE: {round(calculated_roce,2)}\n"
                f"Source ROCE: {round(source_roce,2)}\n"
                f"Difference: {round(difference,2)}\n"
                f"Category: {category}\n"
                "----------------------------------------\n"
            )

print(f"ROCE anomalies logged: {anomaly_count}")

conn.close()