from src.analytics.cashflow_kpis import *


def test_positive_fcf():
    assert calculate_free_cash_flow(500, -150) == 350


def test_negative_fcf():
    assert calculate_free_cash_flow(100, -300) == -200


def test_missing_value():
    assert calculate_free_cash_flow(None, -100) is None

def test_high_quality_score():

    ratio, label = calculate_cfo_quality_score(
        [120,130,140,150,160],
        [100,100,100,100,100]
    )

    assert label == "High Quality"


def test_moderate_quality_score():

    ratio, label = calculate_cfo_quality_score(
        [60,70,80,90,100],
        [100,100,100,100,100]
    )

    assert label == "Moderate"


def test_accrual_risk():

    ratio, label = calculate_cfo_quality_score(
        [20,30,40,30,20],
        [100,100,100,100,100]
    )

    assert label == "Accrual Risk"


def test_pat_zero():

    ratio, label = calculate_cfo_quality_score(
        [100,100,100,100,100],
        [100,100,0,100,100]
    )

    assert ratio is None

def test_asset_light():

    value, label = calculate_capex_intensity(-20,1000)

    assert label == "Asset Light"


def test_moderate_capex():

    value, label = calculate_capex_intensity(-60,1000)

    assert label == "Moderate"


def test_capital_intensive():

    value, label = calculate_capex_intensity(-120,1000)

    assert label == "Capital Intensive"


def test_zero_sales():

    value, label = calculate_capex_intensity(-100,0)

    assert value is None

def test_fcf_conversion_rate():

    assert calculate_fcf_conversion_rate(150,200) == 75.0


def test_fcf_conversion_rate_negative():

    assert calculate_fcf_conversion_rate(-100,200) == -50.0


def test_fcf_conversion_zero_operating_profit():

    assert calculate_fcf_conversion_rate(100,0) is None

def test_reinvestor():

    _, _, _, label = classify_capital_allocation(
        100,
        -50,
        -20
    )

    assert label == "Reinvestor"


def test_shareholder_returns():

    _, _, _, label = classify_capital_allocation(
        100,
        -50,
        -20,
        "High Quality"
    )

    assert label == "Shareholder Returns"


def test_distress_signal():

    _, _, _, label = classify_capital_allocation(
        -100,
        50,
        30
    )

    assert label == "Distress Signal"


def test_growth_funded_by_debt():

    _, _, _, label = classify_capital_allocation(
        -100,
        -50,
        100
    )

    assert label == "Growth Funded by Debt"


def test_cash_accumulator():

    _, _, _, label = classify_capital_allocation(
        100,
        50,
        20
    )

    assert label == "Cash Accumulator"


def test_pre_revenue():

    _, _, _, label = classify_capital_allocation(
        -100,
        -50,
        -20
    )

    assert label == "Pre-Revenue"


def test_mixed():

    _, _, _, label = classify_capital_allocation(
        100,
        -50,
        20
    )

    assert label == "Mixed"

import os


def test_generate_capital_allocation_csv():

    records = [
        {
            "company_id": "TCS",
            "year": 2025,
            "cfo_sign": "+",
            "cfi_sign": "-",
            "cff_sign": "-",
            "pattern_label": "Reinvestor"
        }
    ]

    generate_capital_allocation_csv(
        records,
        "output/test_capital_allocation.csv"
    )

    assert os.path.exists(
        "output/test_capital_allocation.csv"
    )