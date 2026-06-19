import pandas as pd
from pathlib import Path

raw_path = Path("data/raw")

for file in raw_path.glob("*.xlsx"):

    print("\n" + "=" * 80)
    print(file.name)

    df = pd.read_excel(file, header=None)

    print(df.head(5))