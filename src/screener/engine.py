import sqlite3
import pandas as pd
import yaml
try:
    from screener.export import export_screeners
    from screener.scoring import sector_relative_score
except ImportError:
    from src.screener.export import export_screeners
    from src.screener.scoring import sector_relative_score

def run_screener(custom_filters=None):

    # -------------------------------
    # Load configuration
    # -------------------------------

    with open("config/screener_config.yaml", "r") as file:
        config = yaml.safe_load(file)

        # Override YAML filters with preset filters
        filters = config["filters"].copy()

        if custom_filters:
            filters.update(custom_filters)

    print("=" * 60)
    print("ACTIVE FILTERS")
    print("=" * 60)
    print(filters)

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
# Keep Latest Year Only
# -------------------------------

    df["year_num"] = (
        df["year"]
        .str.extract(r"(\d{4})")[0]
        .fillna(0)
        .astype(int)
    )

    df = df.sort_values(
        by="year_num",
        ascending=True
    )

    df = df.drop_duplicates(
        subset="company_id",
        keep="last"
    )

    print("=" * 60)
    print("LATEST COMPANY DATA")
    print("=" * 60)
    print("Rows:", len(df))
    # -------------------------------
    # ROE Filter
    # -------------------------------


    if filters["roe_min"] is not None:

        print("\nRows before ROE filter:", len(df))

        df = df[
        df["return_on_equity_pct"] >= filters["roe_min"]
        ]

        print("Rows after ROE filter :", len(df))


    # -------------------------------
# Debt-to-Equity Filter
# -------------------------------

    if filters["debt_to_equity_max"] is not None:

        print("\nRows before D/E filter:", len(df))

        # Skip Financials only when D/E limit is greater than 0
        if filters["debt_to_equity_max"] > 0:

            financial_mask = (
                df["broad_sector"] == "Financials"
            )

            df = df[
                financial_mask |
                (
                    df["debt_to_equity"]
                    <= filters["debt_to_equity_max"]
                )
            ]

        else:

            df = df[
                df["debt_to_equity"]
                <= filters["debt_to_equity_max"]
            ]

        print("Rows after D/E filter :", len(df))


    if filters["free_cash_flow_min"] is not None:

        print("\nRows before FCF filter:", len(df))

        df = df[
        df["free_cash_flow_cr"]
        >= filters["free_cash_flow_min"]
        ]

        print("Rows after FCF filter :", len(df))

    print("\nStart Remaining Filters:", len(df))

    if filters["revenue_cagr_5yr_min"] is not None:
        df =df[df["revenue_cagr_5yr"] >= filters["revenue_cagr_5yr_min"]]
        print("After Revenue CAGR:", len(df))

    if filters["pat_cagr_5yr_min"] is not None:
        df = df[df["pat_cagr_5yr"] >= filters["pat_cagr_5yr_min"]]
        print("After PAT CAGR:", len(df))

    if filters["opm_min"] is not None:
        df = df[df["operating_profit_margin_pct"] >= filters["opm_min"]]
        print("After OPM:", len(df))

    if filters["pe_max"] is not None:
        df = df[df["pe_ratio"] <= filters["pe_max"]]
        print("After PE:", len(df))

    if filters["pb_max"] is not None:
        df = df[df["pb_ratio"] <= filters["pb_max"]]
        print("After PB:", len(df))

    if filters["dividend_yield_min"] is not None:
        df = df[df["dividend_yield_pct"] >= filters["dividend_yield_min"]]
        print("After Dividend Yield:", len(df))

    if filters.get("dividend_payout_ratio_max") is not None:
        df = df[df["dividend_payout_ratio_pct"] <= filters["dividend_payout_ratio_max"]]
        print("After Dividend Payout:", len(df))

    if filters["interest_coverage_min"] is not None:
        icr_limit = filters["interest_coverage_min"]
        df = df[
        (df["interest_coverage"] >= icr_limit)
        | (df["interest_coverage"].isna())
        ]
        print("After ICR:", len(df))

    if filters["market_cap_min"] is not None:
        df = df[df["market_cap_crore"] >= filters["market_cap_min"]]
        print("After Market Cap:", len(df))

    if filters["net_profit_min"] is not None:
        df = df[df["net_profit"] >= filters["net_profit_min"]]
        print("After Net Profit:", len(df))

    if filters["eps_cagr_5yr_min"] is not None:
        df = df[df["eps_cagr_5yr"] >= filters["eps_cagr_5yr_min"]]
        print("After EPS CAGR:", len(df))

    if filters["asset_turnover_min"] is not None:
        df = df[df["asset_turnover"] >= filters["asset_turnover_min"]]
        print("After Asset Turnover:", len(df))

    if filters["sales_min"] is not None:
        df = df[df["sales"] >= filters["sales_min"]]
        print("After Sales:", len(df))

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

    df = sector_relative_score(df)

    conn.close()

    return df


if __name__ == "__main__":

    try:
        from screener.presets import (
            QUALITY_COMPOUNDER,
            VALUE_PICK,
            GROWTH_ACCELERATOR,
            DIVIDEND_CHAMPION,
            DEBT_FREE_BLUE_CHIP,
            TURNAROUND_WATCH,
        )
    except ImportError:
        from src.screener.presets import (
            QUALITY_COMPOUNDER,
            VALUE_PICK,
            GROWTH_ACCELERATOR,
            DIVIDEND_CHAMPION,
            DEBT_FREE_BLUE_CHIP,
            TURNAROUND_WATCH,
        )

    presets = {
        "QUALITY COMPOUNDER": QUALITY_COMPOUNDER,
        "VALUE PICK": VALUE_PICK,
        "GROWTH ACCELERATOR": GROWTH_ACCELERATOR,
        "DIVIDEND CHAMPION": DIVIDEND_CHAMPION,
        "DEBT FREE BLUE CHIP": DEBT_FREE_BLUE_CHIP,
        "TURNAROUND WATCH": TURNAROUND_WATCH,
    }

    all_results = {}

    for name, preset in presets.items():

        result = run_screener(preset)

        all_results[name] = result

        print(f"Companies Found: {len(result)}")

        print(
            result[
                [
                    "company_id",
                    "year",
                    "return_on_equity_pct",
                    "debt_to_equity",
                    "composite_quality_score",
                    "sector_quality_score",
                ]
            ].head(10)
        )

    export_screeners(all_results)