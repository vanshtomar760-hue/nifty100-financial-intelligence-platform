import re


def normalize_ticker(ticker):
    if ticker is None:
        return None

    ticker = str(ticker).strip().upper()

    return ticker.replace(".NS", "")


def normalize_year(value):
    """
    Extract year from different formats.
    """

    if value is None:
        return None

    match = re.search(r'20\d{2}', str(value))

    if match:
        return int(match.group())

    return None