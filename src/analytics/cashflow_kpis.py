def calculate_free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow (FCF)

    Formula:
    Operating Activity + Investing Activity

    Negative FCF is allowed.
    """

    if operating_activity is None or investing_activity is None:
        return None

    return operating_activity + investing_activity

def calculate_cfo_quality_score(cfo_values, pat_values):
    """
    Calculate 5-year average CFO/PAT ratio.

    Returns:
        (average_ratio, quality_label)
    """

    if len(cfo_values) != len(pat_values):
        return None, None

    ratios = []

    for cfo, pat in zip(cfo_values, pat_values):

        if pat == 0:
            return None, None

        ratios.append(cfo / pat)

    average_ratio = sum(ratios) / len(ratios)

    if average_ratio > 1:
        label = "High Quality"

    elif average_ratio >= 0.5:
        label = "Moderate"

    else:
        label = "Accrual Risk"

    return round(average_ratio, 2), label

def calculate_capex_intensity(investing_activity, sales):
    """
    CapEx Intensity

    Formula:
    abs(investing_activity) / sales * 100

    Returns:
        (percentage, category)
    """

    if sales == 0:
        return None, None

    intensity = (abs(investing_activity) / sales) * 100

    if intensity < 3:
        category = "Asset Light"

    elif intensity <= 8:
        category = "Moderate"

    else:
        category = "Capital Intensive"

    return round(intensity, 2), category
def calculate_fcf_conversion_rate(fcf, operating_profit):
    """
    FCF Conversion Rate

    Formula:
    (FCF / Operating Profit) * 100

    Returns None if operating_profit is 0.
    """

    if operating_profit == 0:
        return None

    return round((fcf / operating_profit) * 100, 2)
def classify_capital_allocation(
    operating_activity,
    investing_activity,
    financing_activity,
    cfo_quality_label=None
):
    """
    Classify capital allocation pattern
    based on cash flow signs.
    """

    cfo = "+" if operating_activity >= 0 else "-"
    cfi = "+" if investing_activity >= 0 else "-"
    cff = "+" if financing_activity >= 0 else "-"

    pattern = (cfo, cfi, cff)

    if pattern == ("+", "-", "-"):

        if cfo_quality_label == "High Quality":
            return cfo, cfi, cff, "Shareholder Returns"

        return cfo, cfi, cff, "Reinvestor"

    if pattern == ("+", "+", "-"):
        return cfo, cfi, cff, "Liquidating Assets"

    if pattern == ("-", "+", "+"):
        return cfo, cfi, cff, "Distress Signal"

    if pattern == ("-", "-", "+"):
        return cfo, cfi, cff, "Growth Funded by Debt"

    if pattern == ("+", "+", "+"):
        return cfo, cfi, cff, "Cash Accumulator"

    if pattern == ("-", "-", "-"):
        return cfo, cfi, cff, "Pre-Revenue"

    if pattern == ("+", "-", "+"):
        return cfo, cfi, cff, "Mixed"

    return cfo, cfi, cff, "Other"
import csv


def generate_capital_allocation_csv(records, output_file="output/capital_allocation.csv"):
    """
    Generate capital allocation report.

    records should be a list of dictionaries with keys:
    company_id
    year
    cfo_sign
    cfi_sign
    cff_sign
    pattern_label
    """

    with open(output_file, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "company_id",
                "year",
                "cfo_sign",
                "cfi_sign",
                "cff_sign",
                "pattern_label"
            ]
        )

        writer.writeheader()

        for row in records:
            writer.writerow(row)