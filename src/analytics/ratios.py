def calculate_net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = Net Profit / Sales * 100
    """
    if sales == 0 or sales is None:
        return None

    return (net_profit / sales) * 100


def calculate_operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = Operating Profit / Sales * 100
    """
    if sales == 0 or sales is None:
        return None

    return (operating_profit / sales) * 100


def calculate_roe(net_profit, equity):
    """
    ROE = Net Profit / Equity * 100
    """

    if equity is None or equity <= 0:
        return None

    return (net_profit / equity) * 100


def calculate_roce(ebit, capital_employed):
    """
    ROCE = EBIT / Capital Employed * 100
    """

    if capital_employed is None or capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def calculate_roa(net_profit, total_assets):
    """
    ROA = Net Profit / Total Assets * 100
    """

    if total_assets is None or total_assets == 0:
        return None

    return (net_profit / total_assets) * 100
def check_opm_difference(calculated_opm, source_opm, company_id=None):
    """
    Compare calculated OPM with source OPM.
    Logs mismatch if difference > 1%
    """

    if calculated_opm is None or source_opm is None:
        return False

    difference = abs(calculated_opm - source_opm)

    if difference > 1:

        with open("output/opm_mismatches.log", "a") as file:
            file.write(
                f"Company: {company_id}\n"
                f"Calculated OPM: {calculated_opm}\n"
                f"Source OPM: {source_opm}\n"
                f"Difference: {difference}%\n"
                "----------------------\n"
            )

        return True

    return False
def check_roce_benchmark(roce, sector, financial_sector_average=12, normal_threshold=15):
    """
    ROCE benchmark handling.

    Financials sector:
    compare against sector average

    Other sectors:
    compare against normal threshold
    """

    if roce is None:
        return None

    if sector == "Financials":
        return roce >= financial_sector_average

    return roce >= normal_threshold

def calculate_debt_to_equity(borrowings, equity):
    """
    Debt to Equity = Borrowings / (Equity + Reserves)

    Returns 0 if company has no debt
    """

    if borrowings == 0:
        return 0

    if equity is None or equity <= 0:
        return None

    return borrowings / equity


def check_high_leverage_flag(debt_to_equity, sector):
    """
    High leverage if D/E > 5
    Except Financials sector
    """

    if debt_to_equity is None:
        return False

    if sector == "Financials":
        return False

    return debt_to_equity > 5

def calculate_interest_coverage_ratio(operating_profit, other_income, interest):
    """
    ICR = (Operating Profit + Other Income) / Interest

    Returns None if interest = 0
    """

    if interest == 0:
        return None

    return (operating_profit + other_income) / interest



def get_icr_label(icr):
    """
    Add display label for debt-free companies
    """

    if icr is None:
        return "Debt Free"

    return None



def check_icr_warning(icr):
    """
    Warning if ICR < 1.5
    """

    if icr is None:
        return False

    return icr < 1.5
def calculate_net_debt(borrowings, investments):
    """
    Net Debt = Borrowings - Investments

    Investments treated as liquid asset proxy
    """

    if borrowings is None:
        return None

    if investments is None:
        investments = 0

    return borrowings - investments



def calculate_asset_turnover(sales, total_assets):
    """
    Asset Turnover = Sales / Total Assets

    Returns None if total_assets = 0
    """

    if total_assets == 0 or total_assets is None:
        return None

    return sales / total_assets