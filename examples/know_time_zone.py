import yfinance as yf

# Download historical data for MSFT
ticker = yf.Ticker("MSFT")
data = ticker.history(start="2020-01-01", end="2024-08-30")

# Check the timezone of the data
timezone = data.index.tz
print(f"The timezone of the downloaded data is: {timezone}")