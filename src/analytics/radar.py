import os
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# -------------------------------------------------
# Load Data
# -------------------------------------------------

conn = sqlite3.connect("db/nifty100.db")

financial = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    """,
    conn
)

peer_groups = pd.read_excel(
    "data/raw/peer_groups.xlsx"
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

peer_df = peer_groups.merge(
    financial,
    on="company_id",
    how="right"
)

conn.close()


# -------------------------------------------------
# Radar Metrics
# -------------------------------------------------

metrics = [
    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "composite_quality_score",
]

labels = [
    "ROE",
    "OPM",
    "NPM",
    "D/E",
    "FCF",
    "PAT CAGR",
    "Revenue CAGR",
    "Composite",
]


# -------------------------------------------------
# Normalize
# -------------------------------------------------

def normalize(series):

    minimum = series.min()
    maximum = series.max()

    if minimum == maximum:
        return pd.Series(50, index=series.index)

    return (
        (series - minimum)
        /
        (maximum - minimum)
    ) * 100


for metric in metrics:
    peer_df[metric + "_score"] = normalize(peer_df[metric])


# -------------------------------------------------
# Create Output Folder
# -------------------------------------------------

os.makedirs(
    "reports/radar_charts",
    exist_ok=True
)


# -------------------------------------------------
# Generate Charts
# -------------------------------------------------

for _, company in peer_df.iterrows():

    peer_group = company["peer_group_name"]

    # -----------------------------------------
    # Reference Line
    # -----------------------------------------

    if pd.isna(peer_group):

        peer_average = peer_df[
            [
                "return_on_equity_pct_score",
                "operating_profit_margin_pct_score",
                "net_profit_margin_pct_score",
                "debt_to_equity_score",
                "free_cash_flow_cr_score",
                "pat_cagr_5yr_score",
                "revenue_cagr_5yr_score",
                "composite_quality_score_score",
            ]
        ].mean()

        peer_label = "Nifty 100 Avg"

    else:

        peer_average = (
            peer_df[
                peer_df["peer_group_name"] == peer_group
            ][
                [
                    "return_on_equity_pct_score",
                    "operating_profit_margin_pct_score",
                    "net_profit_margin_pct_score",
                    "debt_to_equity_score",
                    "free_cash_flow_cr_score",
                    "pat_cagr_5yr_score",
                    "revenue_cagr_5yr_score",
                    "composite_quality_score_score",
                ]
            ]
            .mean()
        )

        peer_label = "Peer Average"

    # -----------------------------------------
    # Company Values
    # -----------------------------------------

    values = [
        company["return_on_equity_pct_score"],
        company["operating_profit_margin_pct_score"],
        company["net_profit_margin_pct_score"],
        company["debt_to_equity_score"],
        company["free_cash_flow_cr_score"],
        company["pat_cagr_5yr_score"],
        company["revenue_cagr_5yr_score"],
        company["composite_quality_score_score"],
    ]

    values += values[:1]

    peer_values = peer_average.tolist()
    peer_values += peer_values[:1]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False,
    ).tolist()

    angles += angles[:1]

    # -----------------------------------------
    # Plot
    # -----------------------------------------

    fig, ax = plt.subplots(
        figsize=(7, 7),
        subplot_kw={"polar": True},
    )

    ax.plot(
        angles,
        values,
        linewidth=2,
        label=company["company_id"],
    )

    ax.fill(
        angles,
        values,
        alpha=0.25,
    )

    ax.plot(
        angles,
        peer_values,
        linestyle="--",
        linewidth=2,
        label=peer_label,
    )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    plt.title(
        f"{company['company_id']} Radar Chart"
    )

    plt.legend(
        loc="upper right"
    )

    filename = (
        f"reports/radar_charts/"
        f"{company['company_id']}_radar.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Generated: {company['company_id']}"
    )


print("\nRadar charts generated successfully!")
print(
    f"Total Charts: {len(peer_df)}"
)