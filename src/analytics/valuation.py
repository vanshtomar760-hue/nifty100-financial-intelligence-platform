import os
import sqlite3
import pandas as pd

print("=" * 60)
print("VALUATION MODULE")
print("=" * 60)

# --------------------------------------------------
# Connect Database
# --------------------------------------------------

conn = sqlite3.connect("db/nifty100.db")

# --------------------------------------------------
# Load Tables
# --------------------------------------------------

financial = pd.read_sql("""
SELECT
    company_id,
    year,
    free_cash_flow_cr
FROM financial_ratios
""", conn)

market = pd.read_sql("""
SELECT
    company_id,
    year,
    market_cap_crore,
    pe_ratio,
    pb_ratio,
    ev_ebitda
FROM market_cap
""", conn)

sector = pd.read_sql("""
SELECT
    company_id,
    broad_sector
FROM sectors
""", conn)

companies = pd.read_sql("""
SELECT
    id,
    company_name
FROM companies
""", conn)

# --------------------------------------------------
# Keep Latest Financial Year
# --------------------------------------------------

financial["year_num"] = (
    financial["year"]
    .str.extract(r"(\d{4})")[0]
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

market = (
    market
    .sort_values("year")
    .drop_duplicates(
        subset="company_id",
        keep="last"
    )
)

# --------------------------------------------------
# Merge Tables
# --------------------------------------------------

df = financial.merge(
    market,
    on="company_id",
    how="left"
)

df = df.merge(
    sector,
    on="company_id",
    how="left"
)

df = df.merge(
    companies,
    left_on="company_id",
    right_on="id",
    how="left"
)

print(df.shape)

# --------------------------------------------------
# FCF Yield
# --------------------------------------------------

df["FCF_yield_pct"] = (
    df["free_cash_flow_cr"]
    / df["market_cap_crore"]
) * 100

# --------------------------------------------------
# Sector Median PE
# --------------------------------------------------

sector_pe = (
    df.groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)

sector_pe.columns = [
    "broad_sector",
    "sector_median_pe"
]

df = df.merge(
    sector_pe,
    on="broad_sector",
    how="left"
)

# --------------------------------------------------
# PE vs Sector Median
# --------------------------------------------------

df["PE_vs_sector_median_pct"] = (
    df["pe_ratio"]
    /
    df["sector_median_pe"]
) * 100

# --------------------------------------------------
# Valuation Flag
# --------------------------------------------------

def valuation_flag(row):

    if pd.isna(row["pe_ratio"]) or pd.isna(row["sector_median_pe"]):
        return "N/A"

    if row["pe_ratio"] > row["sector_median_pe"] * 1.5:
        return "Caution"

    elif row["pe_ratio"] < row["sector_median_pe"] * 0.7:
        return "Discount"

    else:
        return "Fair"

# CREATE FLAG COLUMN
df["flag"] = df.apply(
    valuation_flag,
    axis=1
)

# --------------------------------------------------
# Final Summary
# --------------------------------------------------

df["5yr_median_PE"] = df["sector_median_pe"]

summary = df[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
        "flag",
    ]
].copy()

summary.columns = [
    "company_id",
    "company_name",
    "sector",
    "P/E",
    "P/B",
    "EV/EBITDA",
    "FCF_yield_pct",
    "5yr_median_PE",
    "PE_vs_sector_median_pct",
    "flag",
]

# Round numeric columns

numeric_cols = [
    "P/E",
    "P/B",
    "EV/EBITDA",
    "FCF_yield_pct",
    "5yr_median_PE",
    "PE_vs_sector_median_pct",
]

summary[numeric_cols] = summary[numeric_cols].round(2)

# --------------------------------------------------
# Create Output Folder
# --------------------------------------------------

os.makedirs("output", exist_ok=True)

# --------------------------------------------------
# Export Excel
# --------------------------------------------------

summary.to_excel(
    "output/valuation_summary.xlsx",
    index=False
)

print("✅ valuation_summary.xlsx created")

# --------------------------------------------------
# Export Flags CSV
# --------------------------------------------------

flags = summary[
    summary["flag"].isin(
        ["Caution", "Discount"]
    )
]

flags.to_csv(
    "output/valuation_flags.csv",
    index=False
)

print("✅ valuation_flags.csv created")

print("\nSummary:")
print(summary.head())

print("\nFlag Counts:")
print(summary["flag"].value_counts())

# --------------------------------------------------
# Close Connection
# --------------------------------------------------

conn.close()

print("\n✅ Day 26 completed successfully!")