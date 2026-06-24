import sqlite3


DB = "db/nifty100.db"


conn = sqlite3.connect(DB)


companies = conn.execute(
    """
    SELECT id
    FROM companies
    ORDER BY RANDOM()
    LIMIT 5
    """
).fetchall()


print("Manual Review - 5 Random Companies")
print("-----------------------------------")


for company in companies:

    cid = company[0]

    print("\nCompany:", cid)


    for table in [
        "profitandloss",
        "balancesheet",
        "cashflow",
        "stock_prices"
    ]:

        result = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM {table}
            WHERE company_id = ?
            """,
            (cid,)
        ).fetchone()


        print(
            table,
            "records:",
            result[0]
        )


conn.close()


print("\nManual review completed")