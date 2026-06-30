from src.analytics.cagr import *


def test_normal_cagr():
    result = calculate_cagr(100,200,5)

    assert round(result,2) == 14.87


def test_zero_base():
    assert calculate_cagr(0,100,5) is None

def test_positive_to_positive():

    value, flag = calculate_cagr_with_flag(100,200,5)

    assert flag is None
    assert round(value,2) == 14.87



def test_decline_to_loss():

    value, flag = calculate_cagr_with_flag(100,-50,5)

    assert value is None
    assert flag == "DECLINE_TO_LOSS"



def test_turnaround():

    value, flag = calculate_cagr_with_flag(-50,100,5)

    assert value is None
    assert flag == "TURNAROUND"



def test_both_negative():

    value, flag = calculate_cagr_with_flag(-50,-20,5)

    assert value is None
    assert flag == "BOTH_NEGATIVE"



def test_zero_base_flag():

    value, flag = calculate_cagr_with_flag(0,100,5)

    assert value is None
    assert flag == "ZERO_BASE"



def test_insufficient_data():

    value, flag = calculate_cagr_with_flag(100,200,0)

    assert value is None
    assert flag == "INSUFFICIENT"

def test_revenue_cagr_5_year():

    values = [100,120,140,160,180,220]

    result, flag = revenue_cagr(values,5)

    assert flag is None
    assert round(result,2) == 17.08



def test_pat_cagr():

    values = [50,60,70,80,100,120]

    result, flag = pat_cagr(values,5)

    assert flag is None
    assert result > 0



def test_eps_cagr():

    values = [10,12,15,18,20,25]

    result, flag = eps_cagr(values,5)

    assert flag is None
    assert result > 0



def test_insufficient_history():

    values = [100,120]

    result, flag = revenue_cagr(values,5)

    assert result is None
    assert flag == "INSUFFICIENT"