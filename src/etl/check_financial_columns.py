import pandas as pd

df = pd.read_excel(
    "data/raw/financial_ratios.xlsx"
)

print(df.columns.tolist())