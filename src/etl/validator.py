import pandas as pd


def validate_not_empty(df, table_name):
    """
    DQ-01: Check whether dataframe is empty.
    """

    errors = []

    if df.empty:
        errors.append({
            "table": table_name,
            "rule": "DQ-01",
            "message": "Table is empty"
        })

    return errors


def validate_required_columns(df, required_columns, table_name):
    """
    DQ-02: Check whether required columns exist.
    """

    errors = []

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        errors.append({
            "table": table_name,
            "rule": "DQ-02",
            "message": f"Missing columns: {missing_columns}"
        })

    return errors


def validate_primary_key_not_null(df, primary_key, table_name):
    """
    DQ-03: Check for null primary keys.
    """

    errors = []

    null_count = df[primary_key].isna().sum()

    if null_count > 0:
        errors.append({
            "table": table_name,
            "rule": "DQ-03",
            "message": f"{null_count} null primary key values found"
        })

    return errors


def validate_primary_key_unique(df, primary_key, table_name):
    """
    DQ-04: Check for duplicate primary keys.
    """

    errors = []

    duplicate_count = df[primary_key].duplicated().sum()

    if duplicate_count > 0:
        errors.append({
            "table": table_name,
            "rule": "DQ-04",
            "message": f"{duplicate_count} duplicate primary key values found"
        })

    return errors


def validate_required_field_not_null(
    df,
    required_fields,
    table_name
):
    """
    DQ-05: Check required fields for null values.
    """

    errors = []

    for field in required_fields:

        null_count = df[field].isna().sum()

        if null_count > 0:
            errors.append({
                "table": table_name,
                "rule": "DQ-05",
                "message": f"{field} has {null_count} null values"
            })

    return errors


def validate_numeric_column(df, column_name, table_name):
    """
    DQ-06: Check whether column contains numeric values.
    """

    errors = []

    try:
        pd.to_numeric(df[column_name])

    except Exception:

        errors.append({
            "table": table_name,
            "rule": "DQ-06",
            "message": f"{column_name} contains non-numeric values"
        })

    return errors


def validate_year_format(df, year_column, table_name):
    """
    DQ-07: Validate year format.
    """

    errors = []

    invalid_years = []

    for value in df[year_column]:

        try:
            int(str(value)[:4])

        except Exception:
            invalid_years.append(value)

    if invalid_years:

        errors.append({
            "table": table_name,
            "rule": "DQ-07",
            "message": f"Invalid years found: {invalid_years}"
        })

    return errors


def validate_foreign_key(
    child_df,
    parent_df,
    child_key,
    parent_key,
    table_name
):
    """
    DQ-08: Validate foreign key relationship.
    """

    errors = []

    invalid_keys = set(
        child_df[child_key]
    ) - set(
        parent_df[parent_key]
    )

    if invalid_keys:

        errors.append({
            "table": table_name,
            "rule": "DQ-08",
            "message": f"Invalid foreign keys: {list(invalid_keys)}"
        })

    return errors


if __name__ == "__main__":

    sample_df = pd.DataFrame({"id": [1, 2, 3]})

    result = validate_not_empty(
        sample_df,
        "companies"
    )

    print(result)