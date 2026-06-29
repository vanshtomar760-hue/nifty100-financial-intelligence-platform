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

def test_debt_to_equity_normal():
    assert calculate_debt_to_equity(500,1000) == 0.5


def test_debt_free_company():
    assert calculate_debt_to_equity(0,1000) == 0


def test_high_leverage_flag():
    assert check_high_leverage_flag(6,"Technology") is True


def test_financial_sector_no_leverage_flag():
    assert check_high_leverage_flag(6,"Financials") is False

def test_icr_normal():
    assert calculate_interest_coverage_ratio(200,50,50) == 5


def test_icr_zero_interest():
    assert calculate_interest_coverage_ratio(200,50,0) is None


def test_icr_debt_free_label():
    assert get_icr_label(None) == "Debt Free"


def test_icr_warning():
    assert check_icr_warning(1.2) is True

def test_icr_normal():
    assert calculate_interest_coverage_ratio(200,50,50) == 5


def test_icr_zero_interest():
    assert calculate_interest_coverage_ratio(200,50,0) is None


def test_icr_debt_free_label():
    assert get_icr_label(None) == "Debt Free"


def test_icr_warning():
    assert check_icr_warning(1.2) is True

def test_net_debt_normal():
    assert calculate_net_debt(1000,300) == 700


def test_net_debt_no_investments():
    assert calculate_net_debt(1000,None) == 1000


def test_asset_turnover_normal():
    assert calculate_asset_turnover(1000,500) == 2


def test_asset_turnover_zero_assets():
    assert calculate_asset_turnover(1000,0) is None

