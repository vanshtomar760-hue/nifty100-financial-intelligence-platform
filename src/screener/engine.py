import sqlite3
import pandas as pd
import yaml


def run_screener():

    # -------------------------------
    # Load configuration
    # -------------------------------

    with open("config/screener_config.yaml", "r") as file:
        config = yaml.safe_load(file)

    print("=" * 60)
    print("SCREENER CONFIG")
    print("=" * 60)
    print(config)

    # -------------------------------
    # Connect Database
    # -------------------------------

    conn = sqlite3.connect("db/nifty100.db")

    # -------------------------------
    # Load Required Tables
    # -------------------------------

    financial_ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    profitandloss = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            sales,
            net_profit
        FROM profitandloss
        """,
        conn
    )

    # Remove duplicate company-year rows
    profitandloss = profitandloss.drop_duplicates(
        subset=["company_id", "year"],
        keep="first"
    )

    market_cap = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            market_cap_crore,
            pe_ratio,
            pb_ratio,
            dividend_yield_pct
        FROM market_cap
        """,
        conn
    )

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn
    )

    # -------------------------------
    # Merge DataFrames
    # -------------------------------

    df = financial_ratios.merge(
        profitandloss,
        on=["company_id", "year"],
        how="left"
    )

    df["market_year"] = (
        df["year"]
        .str.extract(r"(\d{4})")
        .astype(float)
    )

    market_cap["market_year"] = market_cap["year"]

    df = df.merge(
        market_cap[
            [
                "company_id",
                "market_year",
                "market_cap_crore",
                "pe_ratio",
                "pb_ratio",
                "dividend_yield_pct"
            ]
        ],
        on=["company_id", "market_year"],
        how="left"
    )

    df = df.merge(
        sectors,
        on="company_id",
        how="left"
    )

    # -------------------------------
    # ROE Filter
    # -------------------------------

    print("\nRows before ROE filter:", len(df))

    df = df[
        df["return_on_equity_pct"]
        >= config["filters"]["roe_min"]
    ]

    print("Rows after ROE filter :", len(df))

    # -------------------------------
    # Debt-to-Equity Filter
    # -------------------------------

    print("\nRows before D/E filter:", len(df))

    financial_mask = (
        df["broad_sector"] == "Financials"
    )

    df = df[
        financial_mask |
        (
            df["debt_to_equity"]
            <= config["filters"]["debt_to_equity_max"]
        )
    ]

    print("Rows after D/E filter :", len(df))

    # -------------------------------
    # Free Cash Flow
    # -------------------------------

    print("\nRows before FCF filter:", len(df))

    df = df[
        df["free_cash_flow_cr"]
        >= config["filters"]["free_cash_flow_min"]
    ]

    print("Rows after FCF filter :", len(df))

    # -------------------------------
    # Remaining Filters
    # -------------------------------

    df = df[
        df["revenue_cagr_5yr"]
        >= config["filters"]["revenue_cagr_5yr_min"]
    ]

    df = df[
        df["pat_cagr_5yr"]
        >= config["filters"]["pat_cagr_5yr_min"]
    ]

    df = df[
        df["operating_profit_margin_pct"]
        >= config["filters"]["opm_min"]
    ]

    df = df[
        df["pe_ratio"]
        <= config["filters"]["pe_max"]
    ]

    df = df[
        df["pb_ratio"]
        <= config["filters"]["pb_max"]
    ]

    df = df[
        df["dividend_yield_pct"]
        >= config["filters"]["dividend_yield_min"]
    ]

    icr_limit = config["filters"]["interest_coverage_min"]

    df = df[
        (
            df["interest_coverage"] >= icr_limit
        )
        |
        (
            df["interest_coverage"].isna()
        )
    ]

    df = df[
        df["market_cap_crore"]
        >= config["filters"]["market_cap_min"]
    ]

    df = df[
        df["net_profit"]
        >= config["filters"]["net_profit_min"]
    ]

    df = df[
        df["eps_cagr_5yr"]
        >= config["filters"]["eps_cagr_5yr_min"]
    ]

    df = df[
        df["asset_turnover"]
        >= config["filters"]["asset_turnover_min"]
    ]

    df = df[
        df["sales"]
        >= config["filters"]["sales_min"]
    ]

    # -------------------------------
    # Remove duplicate rows
    # -------------------------------

    df = df.drop_duplicates(
        subset=["company_id", "year"]
    )

    # -------------------------------
    # Sort by Composite Score
    # -------------------------------

    df = df.sort_values(
        by="composite_quality_score",
        ascending=False
    )

    conn.close()

    return df


if __name__ == "__main__":

    result = run_screener()

    print("\n" + "=" * 60)
    print("FINAL SCREENER RESULT")
    print("=" * 60)

    print("Companies Found:", len(result))

    print()

    print(
        result[
            [
                "company_id",
                "year",
                "return_on_equity_pct",
                "debt_to_equity",
                "free_cash_flow_cr",
                "revenue_cagr_5yr",
                "pat_cagr_5yr",
                "composite_quality_score"
            ]
        ].head(30)
    )