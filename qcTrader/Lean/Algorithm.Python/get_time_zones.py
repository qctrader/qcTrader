import yfinance as yf
from pytz import timezone

def get_exchange_timezone(symbol):
    """
    Fetches the exchange information for a symbol using yfinance and returns the corresponding time zone.
    """
    try:
        ticker = yf.Ticker(symbol)
        exchange = ticker.info.get('exchange')

        # Define a mapping of exchanges to their respective time zones
        exchange_timezones = {
            'NMS': 'America/New_York',  # NASDAQ
            'NYQ': 'America/New_York',  # NYSE
            'ASE': 'America/New_York',  # NYSE American (formerly AMEX)
            'PCX': 'America/Los_Angeles',  # Pacific Exchange
            'LSE': 'Europe/London',  # London Stock Exchange
            'ASX': 'Australia/Sydney',  # Australian Securities Exchange
            # Add more mappings as needed
        }

        # Retrieve the time zone for the given exchange, default to UTC if not found
        return exchange_timezones.get(exchange, 'UTC')

    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return 'UTC'  # Default to UTC in case of an error


def create_symbol_timezone_mapping(symbols):
    """
    Creates a dynamic mapping of symbols to their respective time zones.
    """
    symbol_timezones = {}

    for symbol in symbols:
        time_zone = get_exchange_timezone(symbol)
        symbol_timezones[symbol] = timezone(time_zone)
        print(f"Symbol: {symbol}, Time Zone: {time_zone}")

    return symbol_timezones


