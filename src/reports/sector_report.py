import os
import sqlite3
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

DB_PATH = "db/nifty100.db"

OUTPUT_DIR = "reports/sector"

os.makedirs(OUTPUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    s.broad_sector,
    c.company_name,
    c.id,
    fr.year,
    fr.return_on_equity_pct,
    fr.net_profit_margin_pct,
    fr.debt_to_equity,
    fr.interest_coverage,
    fr.asset_turnover,
    fr.revenue_cagr_5yr,
    fr.pat_cagr_5yr,
    fr.composite_quality_score
FROM sectors s
JOIN companies c
    ON s.company_id = c.id
JOIN financial_ratios fr
    ON c.id = fr.company_id
"""
df = pd.read_sql(query, conn)

df["year_num"] = (
    df["year"]
      .astype(str)
      .str.extract(r"(\d{4})")[0]
      .astype(float)
)

df = (
    df.sort_values("year_num")
      .groupby("id")
      .tail(1)
)
metrics = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "composite_quality_score",
]

for sector in sorted(df["broad_sector"].dropna().unique()):

    sector_df = df[df["broad_sector"] == sector].copy()

    pdf_path = os.path.join(
        OUTPUT_DIR,
        f"{sector.replace('/', '-').replace(' ', '_')}_report.pdf"
    )

    doc = SimpleDocTemplate(pdf_path)

    story = []

    story.append(
        Paragraph(
            f"<b>{sector} Sector Report</b>",
            styles["Title"],
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    story.append(
        Paragraph(
            f"Companies in Sector : {len(sector_df)}",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 0.2 * inch))

    summary = []

    for metric in metrics:
        summary.append(
            [
                metric.replace("_", " ").title(),
                f"{sector_df[metric].median():.2f}",
            ]
        )

    summary_table = Table(summary, colWidths=[260, 120])

    summary_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, -1), colors.beige),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ]
        )
    )

    story.append(summary_table)

    story.append(Spacer(1, 0.35 * inch))

    story.append(
        Paragraph(
            "<b>Company-wise Metrics</b>",
            styles["Heading2"],
        )
    )

    table_data = [[
        "Company",
        "ROE",
        "Margin",
        "D/E",
        "Interest",
        "Asset",
        "Rev CAGR",
        "PAT CAGR",
        "Score",
    ]]

    for _, row in sector_df.sort_values("company_name").iterrows():

        table_data.append([
            row["company_name"],
            f"{row['return_on_equity_pct']:.2f}" if pd.notna(row["return_on_equity_pct"]) else "N/A",
            f"{row['net_profit_margin_pct']:.2f}" if pd.notna(row["net_profit_margin_pct"]) else "N/A",
            f"{row['debt_to_equity']:.2f}" if pd.notna(row["debt_to_equity"]) else "N/A",
            f"{row['interest_coverage']:.2f}" if pd.notna(row["interest_coverage"]) else "N/A",
            f"{row['asset_turnover']:.2f}" if pd.notna(row["asset_turnover"]) else "N/A",
            f"{row['revenue_cagr_5yr']:.2f}" if pd.notna(row["revenue_cagr_5yr"]) else "N/A",
            f"{row['pat_cagr_5yr']:.2f}" if pd.notna(row["pat_cagr_5yr"]) else "N/A",
            f"{row['composite_quality_score']:.2f}" if pd.notna(row["composite_quality_score"]) else "N/A",
        ])

    company_table = Table(table_data, repeatRows=1)

    company_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.3, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ]
        )
    )

    story.append(company_table)

    doc.build(story)

    print(f"Created : {pdf_path}")

print(df.head())

print(df["broad_sector"].unique())