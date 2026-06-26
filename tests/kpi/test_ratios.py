from src.analytics.ratios import *


def test_net_profit_margin_normal():
    assert calculate_net_profit_margin(100, 1000) == 10


def test_net_profit_margin_zero_sales():
    assert calculate_net_profit_margin(100, 0) is None


def test_opm_normal():
    assert calculate_operating_profit_margin(200, 1000) == 20


def test_roe_negative_equity():
    assert calculate_roe(100, -500) is None


def test_roa_zero_assets():
    assert calculate_roa(100, 0) is None
    def test_opm_cross_check_no_issue():
        assert check_opm_difference(20, 20.5) is False


def test_opm_cross_check_mismatch():
    assert check_opm_difference(20, 22) is True

def test_roce_negative_capital():
    assert calculate_roce(100, -500) is None


def test_opm_cross_check_equal_values():
    assert check_opm_difference(25, 25) is False

def test_opm_logging():

    result = check_opm_difference(
        20,
        23,
        "TESTCO"
    )

    assert result is True

def test_financial_sector_roce_benchmark():
    assert check_roce_benchmark(
        13,
        "Financials"
    ) is True


def test_normal_sector_roce_benchmark():
    assert check_roce_benchmark(
        14,
        "Technology"
    ) is False

