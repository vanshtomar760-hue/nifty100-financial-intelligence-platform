import pandas as pd

df = pd.DataFrame(
    columns=[
        "table",
        "rule",
        "severity",
        "message"
    ]
)

df.to_csv(
    "output/validation_failures.csv",
    index=False
)

print("validation_failures.csv created")