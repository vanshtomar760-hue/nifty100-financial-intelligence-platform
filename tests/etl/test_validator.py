import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import pandas as pd

from src.etl.validator import (
    validate_not_empty,
    validate_required_columns,
    validate_primary_key_not_null,
    validate_primary_key_unique,
    validate_required_field_not_null,
    validate_numeric_column,
    validate_year_format,
    validate_foreign_key
)


def test_validate_not_empty_pass():

    df = pd.DataFrame({"id": [1]})

    result = validate_not_empty(
        df,
        "companies"
    )

    assert len(result) == 0


def test_validate_not_empty_fail():

    df = pd.DataFrame()

    result = validate_not_empty(
        df,
        "companies"
    )

    assert len(result) == 1


def test_required_columns_pass():

    df = pd.DataFrame({
        "id": [1],
        "company_name": ["ABC"]
    })

    result = validate_required_columns(
        df,
        ["id", "company_name"],
        "companies"
    )

    assert len(result) == 0


def test_required_columns_fail():

    df = pd.DataFrame({
        "id": [1]
    })

    result = validate_required_columns(
        df,
        ["id", "company_name"],
        "companies"
    )

    assert len(result) == 1


def test_primary_key_not_null_pass():

    df = pd.DataFrame({
        "id": ["ABB", "TCS"]
    })

    result = validate_primary_key_not_null(
        df,
        "id",
        "companies"
    )

    assert len(result) == 0


def test_primary_key_not_null_fail():

    df = pd.DataFrame({
        "id": ["ABB", None]
    })

    result = validate_primary_key_not_null(
        df,
        "id",
        "companies"
    )

    assert len(result) == 1


def test_primary_key_unique_pass():

    df = pd.DataFrame({
        "id": ["ABB", "TCS"]
    })

    result = validate_primary_key_unique(
        df,
        "id",
        "companies"
    )

    assert len(result) == 0


def test_primary_key_unique_fail():

    df = pd.DataFrame({
        "id": ["ABB", "ABB"]
    })

    result = validate_primary_key_unique(
        df,
        "id",
        "companies"
    )

    assert len(result) == 1


def test_required_field_not_null_pass():

    df = pd.DataFrame({
        "company_name": ["ABB"]
    })

    result = validate_required_field_not_null(
        df,
        ["company_name"],
        "companies"
    )

    assert len(result) == 0


def test_required_field_not_null_fail():

    df = pd.DataFrame({
        "company_name": [None]
    })

    result = validate_required_field_not_null(
        df,
        ["company_name"],
        "companies"
    )

    assert len(result) == 1


def test_numeric_column_pass():

    df = pd.DataFrame({
        "sales": [100, 200]
    })

    result = validate_numeric_column(
        df,
        "sales",
        "profitandloss"
    )

    assert len(result) == 0


def test_numeric_column_fail():

    df = pd.DataFrame({
        "sales": ["abc", "xyz"]
    })

    result = validate_numeric_column(
        df,
        "sales",
        "profitandloss"
    )

    assert len(result) == 1


def test_year_format_pass():

    df = pd.DataFrame({
        "year": ["2023", "2024"]
    })

    result = validate_year_format(
        df,
        "year",
        "profitandloss"
    )

    assert len(result) == 0


def test_year_format_fail():

    df = pd.DataFrame({
        "year": ["ABC", "XYZ"]
    })

    result = validate_year_format(
        df,
        "year",
        "profitandloss"
    )

    assert len(result) == 1


def test_foreign_key_pass():

    parent_df = pd.DataFrame({
        "id": ["TCS", "INFY"]
    })

    child_df = pd.DataFrame({
        "company_id": ["TCS"]
    })

    result = validate_foreign_key(
        child_df,
        parent_df,
        "company_id",
        "id",
        "profitandloss"
    )

    assert len(result) == 0


def test_foreign_key_fail():

    parent_df = pd.DataFrame({
        "id": ["TCS", "INFY"]
    })

    child_df = pd.DataFrame({
        "company_id": ["ABC"]
    })

    result = validate_foreign_key(
        child_df,
        parent_df,
        "company_id",
        "id",
        "profitandloss"
    )

    assert len(result) == 1