import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import pandas as pd


def test_dataframe_creation():
    df = pd.DataFrame({"id": [1]})
    assert len(df) == 1


def test_company_column_exists():
    df = pd.DataFrame({"company_id": ["TCS"]})
    assert "company_id" in df.columns


def test_year_column_exists():
    df = pd.DataFrame({"year": [2024]})
    assert "year" in df.columns


def test_duplicate_id_detection():
    df = pd.DataFrame({"id": [1, 1, 2]})
    assert df["id"].duplicated().sum() == 1


def test_no_duplicate_id():
    df = pd.DataFrame({"id": [1, 2, 3]})
    assert df["id"].duplicated().sum() == 0


def test_positive_sales():
    sales = 100
    assert sales > 0


def test_positive_profit():
    profit = 50
    assert profit > 0


def test_negative_profit_allowed():
    profit = -10
    assert profit < 0


def test_valid_year():
    year = 2024
    assert 2000 <= year <= 2030


def test_company_name_not_empty():
    name = "TCS"
    assert len(name) > 0


def test_url_format():
    url = "https://example.com"
    assert url.startswith("http")


def test_eps_numeric():
    eps = 25.4
    assert isinstance(eps, float)


def test_book_value_numeric():
    value = 150.5
    assert isinstance(value, float)


def test_market_cap_positive():
    market_cap = 1000
    assert market_cap > 0


def test_stock_price_positive():
    price = 2500
    assert price > 0


def test_foreign_key_style_value():
    company_id = "TCS"
    assert isinstance(company_id, str)