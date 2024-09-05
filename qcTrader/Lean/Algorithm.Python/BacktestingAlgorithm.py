import json
from datetime import timedelta, datetime
from QuantConnect import DataNormalizationMode
from System import DayOfWeek
import numpy as np
import sys
import os
from priceTracker import PriceTracker
import clr

# Determine the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the correct Launcher/bin/Release directory
release_dir = os.path.join(current_dir, '..', 'Launcher', 'bin', 'Release')

# Normalize the path to remove any redundant separators or up-level references
release_dir = os.path.normpath(release_dir)

print(f"release_dir--------------->{release_dir}")

dll_path = os.path.join(os.getcwd(), 'qcTrader', 'Lean', 'Launcher', 'composer', 'CustomDataProvider.dll')
dll_path = os.path.normpath(dll_path)
if os.path.exists(dll_path):
    clr.AddReference(dll_path)
    print("DLL loaded successfully.")
else:
    print("DLL path does not exist.")


# Add the directory to sys.path if it's not already in sys.path
if release_dir not in sys.path:
    sys.path.append(release_dir)
    sys.path.append(dll_path)
    


from AlgorithmImports import QCAlgorithm, Resolution, Slice, Market, DateRules, TimeRules
from QuantConnect.Configuration import Config
# Import the specific class from your namespace
from CustomDataProvider import CsvDataProvider

class MarketHoursDisplayAlgorithm(QCAlgorithm):
    def Initialize(self):
        # Set up algorithm dates and initial cash
        self.Debugging = True
        self.SetStartDate(2024, 5, 1)
        self.SetEndDate(2024, 5, 15)
        self.SetCash(100000)
        
        # Add MSFT with daily resolution
        self.AddEquity("MSFT", Resolution.Daily)

        # Dynamically determine the base directory for data
        base_dir = os.getcwd()
        data_directory_path = os.path.join(base_dir,'qcTrader', 'Lean', 'Launcher', 'bin', 'Release', 'Data', 'equity', 'usa', 'daily')

        # Use the SetParameters method to set the custom parameter
        # This will pass the base directory path to the configuration used by Lean Engine
        self.SetParameters({"BaseDirectory": data_directory_path})

        # Request historical data directly to see if it returns results
        history = self.History(["MSFT"], 10, Resolution.Daily)
        if history.empty:
            self.Debug("No historical data available for MSFT.")
        else:
            self.Debug(f"Historical data for MSFT loaded: {history.head()}")

    def OnData(self, data):
        # Example to ensure data is being processed
        if "MSFT" in data.Bars:
            msft_data = data["MSFT"]
            self.Debug(f"MSFT data received: {msft_data}")
# class BacktestingAlgorithm(QCAlgorithm):
#     def Initialize(self):
#         try:

#             # Force logging level and handler settings (if applicable)
#             self.Debugging = True
#             self.ClearSubscriptions()
#             self.UniverseManager.Clear()  
#             portfolio_str = self.GetParameter("portfolio")
#             if portfolio_str is None:
#                 raise ValueError("Portfolio parameter is missing.")
#             self.Log(f"Fetched 'portfolio' parameter: {portfolio_str}")

#             portfolio = json.loads(portfolio_str)
#             # Extract assets from the portfolio object
#             self.assets = portfolio.get("assets", [])
#             if not self.assets:
#                 raise ValueError("No assets provided in the portfolio.")

#             self.Log(f"Assets: {self.assets}")
            
#             # Get weighting scheme and rebalancing frequency
#             self.weighting_scheme = self.GetParameter("weighting_scheme")
#             self.rebalancing_frequency = self.GetParameter("rebalancing_frequency")
   
#             # Fetch and parse market caps and volatilities
#             market_caps_str = self.GetParameter("market_caps")
#             volatilities_str = self.GetParameter("volatilities")
#             if market_caps_str is None or volatilities_str is None:
#                 raise ValueError("Market caps or volatilities parameters are missing.")

#             self.market_caps = json.loads(market_caps_str)
#             self.volatilities = json.loads(volatilities_str)

#             # Ensure that all assets have corresponding market_caps and volatilities
#             self.ValidateAssetData()
#             self.security_store = []
#             # Add an example security
#             self.securities["MSFT"] = self.AddEquity("MSFT", Resolution.Daily, dataNormalizationMode=DataNormalizationMode.ADJUSTED)
#             self.AddSecurities()
            
#             # Set the benchmark with a specified resolution
#             self.SetBenchmark(self.AddEquity("MSFT", Resolution.Daily).Symbol)

#             # If using universes, ensure to set the resolution in UniverseSettings
#             self.UniverseSettings.Resolution = Resolution.Daily


#             # Read start and end dates dynamically from parameters
#             start_date_str = self.GetParameter("start_date")
#             end_date_str = self.GetParameter("end_date")

#             # Convert the date strings to datetime objects
#             start_date = self.ParseDate(start_date_str)
#             end_date = self.ParseDate(end_date_str)

#             # Validate the provided dates against available data
#             self.ValidateDateRange(start_date, end_date)

#             # Set the start and end dates for backtesting
#             self.SetStartDate(start_date.year, start_date.month, start_date.day)
#             self.SetEndDate(end_date.year, end_date.month, end_date.day)

#             # Set initial capital from the portfolio parameter, ensure it's correctly parsed
#             initial_capital = portfolio.get("initial_capital", None)
#             if initial_capital is not None:
#                 try:
#                     initial_capital = float(initial_capital)
#                 except ValueError:
#                     raise ValueError("Invalid initial capital value provided.")
#             else:
#                 initial_capital = 100000  # Default to $100,000 if not provided
#             self.SetCash(initial_capital)
#             self.Log(f"Initial capital set to: {initial_capital}")
#             self.tracker = PriceTracker()
#             self.custom_prices = {}
#             self.ScheduleRebalancing()
            

#         except Exception as e:
#             self.Log(f"Unexpected exception during Initialize: {str(e)}")
#     def ScheduleRebalancing(self):
#         """
#         Schedules the rebalancing based on the frequency parameter.
#         """
#         # for symbol in self.security_store:
#         if self.rebalancing_frequency == "Daily":
#             self.Schedule.On(
#                 self.DateRules.EveryDay(self.assets[0]),
#                 self.TimeRules.AfterMarketOpen(self.assets[0], 1),  # 1 minute after market open
#                 self.Rebalance
#             )
#         elif self.rebalancing_frequency == "Weekly":
#             self.Schedule.On(
#                 self.DateRules.WeekStart(self.assets[0], DayOfWeek.Monday),
#                 self.TimeRules.AfterMarketOpen(self.assets[0], 1),  # 1 minute after market open
#                 self.Rebalance
#             )
#         elif self.rebalancing_frequency == "Monthly":
#             self.Schedule.On(
#                 self.DateRules.MonthStart(self.assets[0]),
#                 self.TimeRules.AfterMarketOpen(self.assets[0], 1),  # 1 minute after market open
#                 self.Rebalance
#             )
#         else:
#             self.Debug(f"Unknown rebalancing frequency: {self.rebalancing_frequency}")


    

#     def CheckDataAvailabilityAndGetLastValidPrice(self, symbol):
#         """
#         Checks data availability for a specific symbol.
#         """
#         # Fetch the current data for the symbol
#         security = self.Securities[symbol]
#         history = self.History([symbol], 10, Resolution.Daily)

#         if history.empty:
#             self.Log(f"Historical data for {symbol} is missing or empty.")
#         else:
#             self.Log(f"Recent historical data for {symbol}:\n{history}")
#             if security.Price <= 0:
#                 #self.custom_prices[symbol] = self.RetryCheckPrice(symbol)
#                 self.Log(f"{symbol} price is zero, possible data delay or feed issue.")

#         # Check current price and market status
#         # self.Log(f"Check current price and market status {symbol}: Price = {security.Price}, IsTradable = {security.IsTradable}, "
#         #          f"Next Market Open = {security.Exchange.Hours.GetNextMarketOpen(self.Time)}, "
#         #          f"Next Market Close = {security.Exchange.Hours.GetNextMarketClose(self.Time)}, "
#         #          f"Current Time = {self.Time}")

        
#     def RetryCheckPrice(self, symbol):
#         security = self.Securities[symbol]
#         if security.Price <= 0:
#             self.Log(f"{symbol} price is still zero, manual intervention might be needed.")
#             return self.HandleZeroPrice(symbol, security.Price)
#         else:
#             self.Log(f"Retry successful: {symbol} Price = {security.Price}") 
#             return self.HandleZeroPrice(symbol, security.Price)
                   
#     def HandleZeroPrice(self, symbol, current_price):
#         """
#         Handle scenarios where the price remains zero even after retries.
#         """
#         last_price = self.tracker.get_last_known_price(symbol)

#         if(current_price <= 0):
#             return last_price
#         else:
#            return current_price

  
#     def LogCorporateActions(self):
#         # Fetch recent historical data to observe if prices are correctly adjusted
#         history = self.History(["MSFT"], 15, Resolution.Daily)
#         if history.empty:
#             self.Log("Historical data for MSFT is missing or empty.")
#         else:
#             # Log the historical data to see adjusted prices
#             self.Log(f"Recent historical data for MSFT:\n{history}")

#         # Access the security object for more detailed information
#         security = self.Securities["MSFT"]
#         self.Log(f"Current MSFT Price: {security.Price}, IsTradable: {security.IsTradable}")

#             # Check for corporate actions applied
#         if security.IsTradable and security.Price > 0:
#             next_market_open = security.Exchange.Hours.GetNextMarketOpen(self.Time, extendedMarket=False)
#             next_market_close = security.Exchange.Hours.GetNextMarketClose(self.Time, extendedMarket=False)
#             self.Log(f"MSFT Details - Price: {security.Price}, Next Market Open: {next_market_open}, "
#                     f"Next Market Close: {next_market_close}, Current Time: {self.Time}")
#         else:
#             # Log additional market status details
#             market_is_open = security.Exchange.Hours.MarketIsOpen(self.Time, extendedMarket=False)
#             self.Log(f"MSFT has an invalid price or is not tradable at {self.Time}. "
#                     f"Market Open: {market_is_open}, Next Market Open: {next_market_open if security else 'N/A'}, "
#                     f"Next Market Close: {next_market_close if security else 'N/A'}.")
            
                    
#     def CheckHistoricalDataAvailability(self):
#         for asset in self.assets:
#             history = self.History([asset], 10, Resolution.Daily)
#             if history.empty:
#                 self.Log(f"No historical data available for {asset}.")
#             else:
#                 self.Log(f"Historical data for {asset}: {history.head().to_string(index=True)}")
#     def ClearSubscriptions(self):
#         # Manually clear all subscriptions from the SubscriptionManager
#         subscriptions = list(self.SubscriptionManager.Subscriptions)
#         for subscription in subscriptions:
#             self.SubscriptionManager.RemoveSubscription(subscription)
#         self.Log(f"Cleared {len(subscriptions)} subscriptions.")
#     def MarketCloseAction(self):
#         """Action to be performed just before the market closes."""
#         self.Log("Performing end-of-day actions before market close.")

#     # Additional methods (ParseDate, ValidateDateRange, ValidateAssetData, AddSecurities, etc.) remain the same

#     def ParseDate(self, date_str):
#         """Helper method to parse a date string into a datetime object."""
#         return datetime.strptime(date_str, "%Y-%m-%d")

#     def ValidateDateRange(self, start_date, end_date):
#         """Validate the provided start and end dates against available data for assets."""
#         try:
#             for symbol in self.assets:
#                 # Get the available historical data range for the asset
#                 history = self.History([symbol], 1, Resolution.Daily)
#                 if history.empty:
#                     raise ValueError(f"No historical data available for asset {symbol}.")

#                 available_start_date = history.index.min().date()
#                 available_end_date = history.index.max().date()

#                 # Adjust start and end dates if they are out of the available range
#                 if start_date < available_start_date:
#                     self.Log(f"Start date adjusted for {symbol} from {start_date} to {available_start_date}.")
#                     start_date = available_start_date
#                 if end_date > available_end_date:
#                     self.Log(f"End date adjusted for {symbol} from {end_date} to {available_end_date}.")
#                     end_date = available_end_date

#         except Exception as e:
#             self.Log(f"Unexpected exception during ValidateDateRange: {str(e)}")

#     def ValidateAssetData(self):
#         """Ensure that all assets have market caps and volatilities, removing those that are missing."""
#         try:
#             missing_market_caps = [asset for asset in self.assets if asset not in self.market_caps]
#             missing_volatilities = [asset for asset in self.assets if asset not in self.volatilities]

#             # Log and remove assets with missing market cap data
#             if missing_market_caps:
#                 self.Log(f"Removing assets with missing market cap data: {missing_market_caps}")
#                 self.assets = [asset for asset in self.assets if asset not in missing_market_caps]

#             # Log and remove assets with missing volatility data
#             if missing_volatilities:
#                 self.Log(f"Removing assets with missing volatility data: {missing_volatilities}")
#                 self.assets = [asset for asset in self.assets if asset not in missing_volatilities]

#             # If no assets remain after removal, raise an error
#             if not self.assets:
#                 raise ValueError("No valid assets remain after removing those with missing data.")

#         except Exception as e:
#             self.Log(f"Unexpected exception during ValidateAssetData: {str(e)}")

#     def AddSecurities(self):
#         """Try to add securities to the portfolio, with error handling."""
#         try:
            
#             for symbol in self.assets:
#                 if symbol is not None:
#                     try:
#                         # Add the security to the portfolio
#                         security = self.AddEquity(symbol, Resolution.Daily, dataNormalizationMode=DataNormalizationMode.ADJUSTED)
#                         self.securities[symbol] = security
#                         # self.security_store.append(security.Symbol)
#                         self.Log(f"Security added: {symbol}")

                        
#                         self.VerifySubscriptions() 
#                     except Exception as e:
#                         self.Log(f"Error adding security for {symbol}: {str(e)}")
#                 else:
#                     self.Log("Symbol is None, skipping addition.")

#             # Check if any securities were added successfully
#             if not self.securities:
#                 self.Log("No valid securities were added to the portfolio.")
#                 raise ValueError("Portfolio could not be initialized with the given assets.")

#         except Exception as e:
#             self.Log(f"Unexpected exception during AddSecurities: {str(e)}")

#     def Rebalance(self):
#         """Rebalance the portfolio based on the selected weighting scheme."""
#         try:
#             if not self.securities:
#                 self.Log("No securities to rebalance.")
#                 return
            
#             if self.weighting_scheme == "market_cap":
#                 self.MarketCapWeighting()
#             elif self.weighting_scheme == "risk_parity":
#                 self.RiskParityWeighting()
#             else:
#                 raise ValueError(f"Unknown weighting scheme: {self.weighting_scheme}")

#         except Exception as e:
#             self.Log(f"Unexpected exception during Rebalance: {str(e)}")
#     def MarketCapWeighting(self):
#         """Adjust holdings based on market capitalization weighting."""
#         try:
#             # Ensure we have market caps for all assets
#             valid_assets = [symbol for symbol in self.assets if symbol in self.market_caps]
#             if not valid_assets:
#                 self.Log("No valid assets with market cap data available for rebalancing.")
#                 return

#             # Calculate total market cap
#             total_market_cap = sum(self.market_caps[symbol] for symbol in valid_assets)
#             if total_market_cap == 0:
#                 self.Log("Total market cap is zero, cannot rebalance.")
#                 return

#             # Calculate weights
#             weights = {symbol: self.market_caps[symbol] / total_market_cap for symbol in valid_assets}

#             # Set holdings with detailed checks
#             for symbol, weight in weights.items():
#                 security = self.Securities[symbol]
                
#                    # Fetch next market open and close times
#                 next_market_open = security.Exchange.Hours.GetNextMarketOpen(self.Time, False)
#                 next_market_close = security.Exchange.Hours.GetNextMarketClose(self.Time, False)
                
#                 # Log detailed information about the security
#                 self.Log(f"Processing {symbol}: Price = {security.Price}, IsTradable = {security.IsTradable}, "
#                         f"Next Market Open = {next_market_open}, Next Market Close = {next_market_close}, "
#                         f"Current Time = {self.Time}")


#                 # Check if the market is open and the security is tradable
#                 if security.HasData and security.Price > 0 and security.IsTradable:
#                     if security.Exchange.DateTimeIsOpen(self.Time):
                        
#                         self.SetHoldings(symbol, weight)
#                         # self.tracker.handle_price_update(symbol, security.Price)
#                         self.Log(f"Set holdings for {symbol} to {weight * 100:.2f}% based on market cap weighting.")
#                     else:
#                         self.Log(f"Market is closed for {symbol} at {self.Time}. "
#                              f"Next Open: {next_market_open}, Next Close: {next_market_close}.")    
#                 else:
#                     # Detailed logging to determine the exact issue
#                     if security.Price <= 0:
#                         self.CheckDataAvailabilityAndGetLastValidPrice(symbol)
#                         self.Log(f"{symbol} has an invalid price: {security.Price}. Potential issues could be data feed interruptions, market data provider delays, or delisting.")
#                         self.CheckHistoricalDataAvailability()
#                     if not security.IsTradable:
#                         self.Log(f"{symbol} is not tradable. This could be due to a delisting, suspension, or regulatory issue.")
                    
#                     # Check if the security is properly subscribed
#                     is_subscribed = symbol in [sub.Symbol.Value for sub in self.SubscriptionManager.Subscriptions]
#                     if not is_subscribed:
#                         self.Log(f"{symbol} is not properly subscribed. Check if it was added correctly in Initialize.")
                    
#                     # Log subscription status
#                     subscription_status = "Subscribed" if is_subscribed else "Not Subscribed"
#                     self.Log(f"{symbol} subscription status: {subscription_status}.")
#                     continue

#         except Exception as e:
#             self.Log(f"Unexpected exception during MarketCapWeighting: {str(e)}")

#     def VerifySubscriptions(self):
#         subscribed_symbols = [sub.Symbol.Value for sub in self.SubscriptionManager.Subscriptions]
#         self.Log(f"Currently subscribed symbols: {subscribed_symbols}")

#         # Check for specific symbols
#         for symbol in self.assets:
#             if symbol not in subscribed_symbols:
#                 self.Log(f"{symbol} is not properly subscribed. Check if it was added correctly in Initialize.")        
#     def RiskParityWeighting(self):
#         """Adjust holdings based on risk parity weighting."""
#         try:
#             inv_vols = {symbol: 1 / self.volatilities[symbol] for symbol in self.assets if self.volatilities[symbol] != 0}
#             total_inv_vols = sum(inv_vols.values())
#             weights = {symbol: inv_vol / total_inv_vols for symbol, inv_vol in inv_vols.items()}

#             for symbol, weight in weights.items():
#                 # Ensure we have a valid price before setting holdings
#                 if symbol is not None and symbol in self.Securities and  self.Securities[symbol].HasData and self.Securities[symbol].Price > 0:
#                     self.SetHoldings(symbol, weight)
#                     self.Log(f"Set holdings for {symbol} to {weight * 100:.2f}% based on risk parity weighting")
#                 else:
#                     self.Log(f"Skipping {symbol} as it doesn't have a valid price yet.")
#                     continue

#         except Exception as e:
#             self.Log(f"Unexpected exception during RiskParityWeighting: {str(e)}")

#     def OnData(self, data: Slice):
#         """Process incoming data and handle invalid prices for assets like MSFT."""
#         try:
#             if self.IsWarmingUp:
#                 self.Log("Currently warming up, not processing data.")
#                 return

#             for symbol in self.assets:
#                 if symbol in data.Bars:
#                     bar = data.Bars[symbol]
                    
#                     # Check for valid price
#                     if bar is not None and bar.Close > 0:
#                         self.Log(f"Received valid data for {symbol}: Close Price = {bar.Close}")
#                     else:
#                         self.Log(f"{symbol} has an invalid price: {bar.Close if bar else 'None'}.")

#                         # Further diagnostics for invalid price
#                         security = self.Securities[symbol]
                        
#                         # Log market status and tradability
#                         if not security.IsTradable:
#                             self.Log(f"{symbol} is not tradable. Potential reasons include delisting, suspension, or regulatory issues.")
                        
#                         if not security.Exchange.DateTimeIsOpen(self.Time):
#                             self.Log(f"Market is closed for {symbol} at {self.Time}. "
#                                     f"Next Open: {security.Exchange.Hours.GetNextMarketOpen(self.Time, False)}, "
#                                     f"Next Close: {security.Exchange.Hours.GetNextMarketClose(self.Time, False)}.")

#                         # Check historical data to see if the issue is consistent
#                         history = self.History([symbol], 10, Resolution.Daily)
#                         if history.empty or history['close'].min() <= 0:
#                             self.Log(f"Historical data for {symbol} shows invalid prices or missing data. "
#                                     f"This suggests a persistent data issue or asset delisting.")
                        
#                         # Log subscription and data provider status
#                         subscription_status = "Subscribed" if symbol in [sub.Symbol.Value for sub in self.SubscriptionManager.Subscriptions] else "Not Subscribed"
#                         self.Log(f"{symbol} subscription status: {subscription_status}. Check if the subscription is correctly set in Initialize.")
#                         custom_price = self.custom_prices.get(symbol, 0)
#                         self.Log(f"custom_price----------> {custom_price}")

#                 else:
#                     # Provide detailed logs to understand the absence of data
#                     self.Log(f"{symbol} is not found in data keys at time {self.Time}. Checking further...")

#                     # Check additional security information
#                     if symbol in self.Securities:
#                         security = self.Securities[symbol]
#                         if not security.IsTradable:
#                             self.Log(f"{symbol} is not tradable. Possibly delisted or trading halted.")
#                         if security.Price <= 0:
#                             self.Log(f"{symbol} has an invalid price: {security.Price}")
#                         if not security.Exchange.DateTimeIsOpen(self.Time):
#                             self.Log(f"Market is closed for {symbol}.")
#                     else:
#                         self.Log(f"{symbol} is not found in the securities dictionary. Possible reasons include incorrect initialization or subscription errors.")

#         except Exception as e:
#             self.Log(f"Unexpected exception during OnData: {str(e)}")

