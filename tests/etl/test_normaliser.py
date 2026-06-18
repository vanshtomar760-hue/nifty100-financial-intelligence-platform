import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.etl.loader import load_companies
from src.etl.normaliser import normalize_ticker, normalize_year


def test_companies_row_count():
    df = load_companies("data/raw/companies.xlsx")
    assert len(df) == 92


def test_companies_columns():
    df = load_companies("data/raw/companies.xlsx")

    expected_columns = [
        'id',
        'company_logo',
        'company_name',
        'chart_link',
        'about_company',
        'website',
        'nse_profile',
        'bse_profile',
        'face_value',
        'book_value',
        'roce_percentage',
        'roe_percentage'
    ]

    assert list(df.columns) == expected_columns


def test_normalize_ticker():
    assert normalize_ticker("tcs") == "TCS"


def test_normalize_year():
    assert normalize_year("2023") == 2023