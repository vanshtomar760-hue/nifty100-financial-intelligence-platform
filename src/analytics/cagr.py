def calculate_cagr(start, end, years):
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Formula:
    CAGR = ((End / Start) ** (1 / Years) - 1) * 100
    """

    if years <= 0:
        return None

    if start == 0:
        return None

    return ((end / start) ** (1 / years) - 1) * 100


def calculate_cagr_with_flag(start, end, years):
    """
    Calculate CAGR with edge case handling.

    Returns:
        (cagr_value, flag)
    """

    # Less than required years
    if years <= 0:
        return None, "INSUFFICIENT"

    # Zero base
    if start == 0:
        return None, "ZERO_BASE"

    # Positive -> Negative
    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    # Negative -> Positive
    if start < 0 and end > 0:
        return None, "TURNAROUND"

    # Negative -> Negative
    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    # Normal CAGR calculation
    cagr = ((end / start) ** (1 / years) - 1) * 100

    return round(cagr, 2), None


def calculate_metric_cagr(values, years):
    """
    Calculate CAGR for a metric history.

    Parameters:
        values : list
            Ordered from oldest to newest.

        years : int
            CAGR period (3, 5, or 10)

    Returns:
        (cagr_value, flag)
    """

    # Need at least (years + 1) values
    if len(values) <= years:
        return None, "INSUFFICIENT"

    start = values[-(years + 1)]
    end = values[-1]

    return calculate_cagr_with_flag(start, end, years)


def revenue_cagr(values, years):
    """
    Revenue CAGR
    """
    return calculate_metric_cagr(values, years)


def pat_cagr(values, years):
    """
    Profit After Tax CAGR
    """
    return calculate_metric_cagr(values, years)


def eps_cagr(values, years):
    """
    Earnings Per Share CAGR
    """
    return calculate_metric_cagr(values, years)