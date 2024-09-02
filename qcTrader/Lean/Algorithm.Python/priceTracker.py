class PriceTracker:
    def __init__(self):
        self.last_known_prices = {}

    def update_price(self, symbol, price):
        """ Update the last known price for the given symbol. """
        self.last_known_prices[symbol] = price

    def get_last_known_price(self, symbol):
        """ Return the last known price for the given symbol or None if not found. """
        return self.last_known_prices.get(symbol)

    def handle_price_update(self, symbol, price):
        """ Handle incoming price update and store it if valid. """
        if price > 0:
            self.update_price(symbol, price)
        else:
            print(f"Invalid price data for {symbol}: {price}")

    def is_valid_price(self, current_price, symbol):
        """ Implement your own logic to determine if the price is valid. """
        if current_price == 0:
            if symbol in self.last_known_prices:
                # Use the last non-zero price if the current price is zero
                return self.last_known_prices[symbol]
            else:
                # Handle the case where no previous non-zero price is available
                raise ValueError(f"No previous price data available for asset: {asset}")
        else:
            # Update the last non-zero price record
            self.last_known_prices[symbol] = current_price
            return current_price

# # Example usage
# tracker = PriceTracker()

# # Simulating price updates
# tracker.handle_price_update("AAPL", 150.25)
# tracker.handle_price_update("GOOGL", None)  # Invalid price

# # Retrieving the last known price
# print(tracker.get_last_known_price("AAPL"))  # Output: 150.25
# print(tracker.get_last_known_price("GOOGL"))  # Output: None

# # Using the last known valid price if the current price is invalid
# def get_price(symbol, current_price):
#     last_price = tracker.get_last_known_price(symbol)
#     return current_price if tracker.is_valid_price(current_price) else last_price

# # Example of using the function
# current_price = None
# print(get_price("AAPL", current_price))  # Output: 150.25
# print(get_price("GOOGL", current_price))  # Output: None
