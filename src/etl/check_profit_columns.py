import pandas as pd

df = pd.read_excel(
    "data/raw/profitandloss.xlsx",
    header=1
)

print(df.columns.tolist())