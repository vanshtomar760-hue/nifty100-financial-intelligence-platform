import sqlite3
import pandas as pd


def calculate_percentile(df, column, ascending=True):

    temp = df.copy()

    temp["percentile_rank"] = (
        temp[column]
        .rank(
            method="average",
            pct=True,
            ascending=ascending
        )
        * 100
    )

    return temp


print("=" * 60)
print("LOADING PEER GROUPS")
print("=" * 60)

peer_groups = pd.read_excel(
    "data/raw/peer_groups.xlsx"
)

conn = sqlite3.connect("db/nifty100.db")

financial = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    """,
    conn
)

financial["year_num"] = (
    financial["year"]
    .str.extract(r"(\d{4})")[0]
    .fillna(0)
    .astype(int)
)

financial = (
    financial
    .sort_values("year_num")
    .drop_duplicates(
        subset="company_id",
        keep="last"
    )
)

# -------------------------------------------------
# Companies without peer group
# -------------------------------------------------

missing = financial[
    ~financial["company_id"].isin(
        peer_groups["company_id"]
    )
]

if not missing.empty:

    print("\n" + "=" * 60)
    print("NO PEER GROUP ASSIGNED")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("NO PEER GROUP ASSIGNED")
    print("=" * 60)

    print(f"{len(missing)} companies do not belong to any peer group.\n")

    print(
        missing["company_id"]
        .sort_values()
        .to_string(index=False)
    )

# -------------------------------------------------
# Merge peer groups with financials
# -------------------------------------------------

peer_df = peer_groups.merge(
    financial,
    on="company_id",
    how="left"
)

print("\n" + "=" * 60)
print("PEER DATA")
print("=" * 60)

print(peer_df.shape)

print()
print(peer_df.head())

# -------------------------------------------------
# Metrics
# -------------------------------------------------

metrics = {
    "return_on_equity_pct": True,
    "operating_profit_margin_pct": True,
    "net_profit_margin_pct": True,
    "debt_to_equity": False,
    "free_cash_flow_cr": True,
    "pat_cagr_5yr": True,
    "revenue_cagr_5yr": True,
    "eps_cagr_5yr": True,
    "interest_coverage": True,
    "asset_turnover": True
}

all_percentiles = []

print("\n" + "=" * 60)
print("CALCULATING PERCENTILES")
print("=" * 60)

for metric, higher_better in metrics.items():

    print(f"Calculating {metric}")

    for group, data in peer_df.groupby("peer_group_name"):

        temp = calculate_percentile(
            data,
            metric,
            ascending=higher_better
        )

        # Lower Debt = Better
        if metric == "debt_to_equity":
            temp["percentile_rank"] = (
                100 - temp["percentile_rank"]
            )

        temp["peer_group_name"] = group
        temp["metric"] = metric

        all_percentiles.append(temp)

peer_percentiles = pd.concat(
    all_percentiles,
    ignore_index=True
)

# -------------------------------------------------
# Keep required columns
# -------------------------------------------------

peer_percentiles["value"] = peer_percentiles.apply(
    lambda row: row[row["metric"]],
    axis=1
)

peer_percentiles = peer_percentiles[
    [
        "company_id",
        "peer_group_name",
        "metric",
        "value",
        "percentile_rank",
        "year"
    ]
]

# -------------------------------------------------
# Save to SQLite
# -------------------------------------------------

peer_percentiles.to_sql(
    "peer_percentiles",
    conn,
    if_exists="replace",
    index=False
)

print("\n" + "=" * 60)
print("TABLE CREATED")
print("=" * 60)

print("Rows Inserted:", len(peer_percentiles))

print()

print(
    pd.read_sql(
        """
        SELECT *
        FROM peer_percentiles
        LIMIT 20
        """,
        conn
    )
)

conn.close()

print("\nPeer percentile calculation completed successfully!")