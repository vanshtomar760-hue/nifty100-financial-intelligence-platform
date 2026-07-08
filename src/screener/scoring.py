import pandas as pd


def winsorize(series):
    p10 = series.quantile(0.10)
    p90 = series.quantile(0.90)

    clipped = series.clip(lower=p10, upper=p90)

    normalized = (
        (clipped - clipped.min())
        /
        (clipped.max() - clipped.min())
    ) * 100

    return normalized

def sector_relative_score(df):

    df = df.copy()

    df["sector_quality_score"] = (
        df.groupby("broad_sector")["composite_quality_score"]
        .transform(winsorize)
    )

    return df