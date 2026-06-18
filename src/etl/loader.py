import pandas as pd


def load_companies(file_path):
    """
    Load companies dataset and clean header rows.
    """

    df = pd.read_excel(file_path, header=None)

    # Row 1 contains actual column names
    df.columns = df.iloc[1]

    # Remove title row and header row
    df = df.iloc[2:].reset_index(drop=True)

    return df


if __name__ == "__main__":
    companies = load_companies("data/raw/companies.xlsx")

    print(companies[[
        "id",
        "roce_percentage",
        "roe_percentage"
    ]].head(10))