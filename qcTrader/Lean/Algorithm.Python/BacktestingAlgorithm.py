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
from CustomDataProvider import CsvDataProvider
from CustomData import CustomDataParser

# class MarketHoursDisplayAlgorithm(QCAlgorithm):
#     def Initialize(self):
#         # Set up algorithm dates and initial cash
#         self.Debugging = True
#         #self.ClearSubscriptions()
#         #self.UniverseManager.Clear()
#         self.UniverseSettings.Resolution = Resolution.Daily
#         self.SetStartDate(2024, 5, 1)
#         self.SetEndDate(2024, 5, 15)
#         self.SetCash(100000)
        
#         portfolio_str = self.GetParameter("portfolio")
#         portfolio = json.loads(portfolio_str)
#         self.assets = portfolio.get("assets", [])

#         for symbol in self.assets:
#                  if symbol is not None:
#                      try:
#                          self.AddEquity(symbol, Resolution.Daily, dataNormalizationMode=DataNormalizationMode.ADJUSTED)
#                      except Exception as e:
#                          self.Log(f"Error adding security for {symbol}: {str(e)}")
#                  else:
#                     self.Log("Symbol is None, skipping addition.")

        

#     def OnData(self, data):
#          # This method is called on each new data point
#         if not data.ContainsKey("MSFT"):
#             self.Debug("No data for MSFT on this bar.")
#             return

#         msft_bar = data["MSFT"]
#         self.Debug(f"MSFT Data - Time: {msft_bar.EndTime}, Price: {msft_bar.Close}")
        
#         # Example: Place a market order to buy 10 shares of MSFT
#         if not self.Portfolio.Invested:
#             self.SetHoldings("MSFT", 0.1)  # Allocate 10% of the portfolio to MSFT



#         # Access historical data for MSFT
#         history = self.History(["MSFT"], 10, Resolution.Daily)
        
#         if history.empty:
#             self.Debug("No historical data available for MSFT.")
#         else:
#             self.Debug(f"Historical data for MSFT loaded: {history.head()}")



#     def OnEndOfAlgorithm(self):
#         # Called at the end of the backtest
#         self.Debug("Algorithm completed.")

class BacktestingAlgorithm(QCAlgorithm):
    def Initialize(self):
        try:

            # force logging level and handler settings (if applicable)
            self.debugging = True
            # self.clearsubscriptions()
            # self.universemanager.clear()  
            portfolio_str = self.GetParameter("portfolio")
            if portfolio_str is None:
                raise ValueError("portfolio parameter is missing.")
            self.log(f"fetched 'portfolio' parameter: {portfolio_str}")

            portfolio = json.loads(portfolio_str)
            # extract assets from the portfolio object
            self.assets = portfolio.get("assets", [])
            if not self.assets:
                raise ValueError("no assets provided in the portfolio.")

            self.log(f"assets: {self.assets}")
            
            # get weighting scheme and rebalancing frequency
            self.weighting_scheme = self.GetParameter("weighting_scheme")
            self.rebalancing_frequency = self.GetParameter("rebalancing_frequency")
   
            # fetch and parse market caps and volatilities
            market_caps_str = self.GetParameter("market_caps")
            volatilities_str = self.GetParameter("volatilities")
            if market_caps_str is None or volatilities_str is None:
                raise ValueError("market caps or volatilities parameters are missing.")

            self.market_caps = json.loads(market_caps_str)
            self.volatilities = json.loads(volatilities_str)

            # ensure that all assets have corresponding market_caps and volatilities
            self.validateassetdata()
            self.security_store = []
            # add an example security
            self.Securities["msft"] = self.AddEquity("msft", Resolution.Daily, datanormalizationmode=DataNormalizationMode.ADJUSTED)
            self.addsecurities()
            
            # set the benchmark with a specified resolution
            self.SetBenchmark(self.AddEquity("msft", Resolution.Daily).symbol)

            # if using universes, ensure to set the resolution in universesettings
            self.UniverseSettings.Resolution = Resolution.Daily


            # read start and end dates dynamically from parameters
            start_date_str = self.GetParameter("start_date")
            end_date_str = self.GetParameter("end_date")

            # convert the date strings to datetime objects
            start_date = self.parsedate(start_date_str)
            end_date = self.parsedate(end_date_str)

            # validate the provided dates against available data
            self.validatedaterange(start_date, end_date)

            # set the start and end dates for backtesting
            self.SetStartDate(start_date.year, start_date.month, start_date.day)
            self.SetEndDate(end_date.year, end_date.month, end_date.day)

            # set initial capital from the portfolio parameter, ensure it's correctly parsed
            initial_capital = portfolio.get("initial_capital", None)
            if initial_capital is not None:
                try:
                    initial_capital = float(initial_capital)
                except ValueError:
                    raise ValueError("invalid initial capital value provided.")
            else:
                initial_capital = 100000  # default to $100,000 if not provided
            self.SetCash(initial_capital)
            self.log(f"initial capital set to: {initial_capital}")
            self.tracker = PriceTracker()
            self.custom_prices = {}
            self.schedulerebalancing()
            

        except Exception as e:
            self.log(f"unexpected exception during initialize: {str(e)}")
    def schedulerebalancing(self):
        """
        schedules the rebalancing based on the frequency parameter.
        """
        # for symbol in self.security_store:
        if self.rebalancing_frequency == "Daily":
            self.schedule.on(
                self.DateRules.EveryDay(self.assets[0]),
                self.TimeRules.AfterMarketOpen(self.assets[0], 1),  # 1 minute after market open
                self.Rebalance
            )
        elif self.rebalancing_frequency == "weekly":
            self.schedule.on(
                self.DateRules.WeekStart(self.assets[0], DayOfWeek.monday),
                self.TimeRules.AfterMarketOpen(self.assets[0], 1),  # 1 minute after market open
                self.Rebalance
            )
        elif self.rebalancing_frequency == "monthly":
            self.schedule.on(
                self.DateRules.MonthStart(self.assets[0]),
                self.TimeRules.AfterMarketOpen(self.assets[0], 1),  # 1 minute after market open
                self.Rebalance
            )
        else:
            self.debug(f"unknown rebalancing frequency: {self.rebalancing_frequency}")


    

    def checkdataavailabilityandgetlastvalidprice(self, symbol):
        """
        checks data availability for a specific symbol.
        """
        # fetch the current data for the symbol
        security = self.Securities[symbol]
        history = self.History([symbol], 10, Resolution.Daily)

        if history.empty:
            self.log(f"historical data for {symbol} is missing or empty.")
        else:
            self.log(f"recent historical data for {symbol}:\n{history}")
            if security.price <= 0:
                #self.custom_prices[symbol] = self.retrycheckprice(symbol)
                self.log(f"{symbol} price is zero, possible data delay or feed issue.")

        # check current price and market status
        # self.log(f"check current price and market status {symbol}: price = {security.price}, istradable = {security.istradable}, "
        #          f"next market open = {security.exchange.hours.getnextmarketopen(self.time)}, "
        #          f"next market close = {security.exchange.hours.getnextmarketclose(self.time)}, "
        #          f"current time = {self.time}")

        
    def retrycheckprice(self, symbol):
        security = self.Securities[symbol]
        if security.Price <= 0:
            self.log(f"{symbol} price is still zero, manual intervention might be needed.")
            return self.handlezeroprice(symbol, security.Price)
        else:
            self.log(f"retry successful: {symbol} price = {security.Price}") 
            return self.handlezeroprice(symbol, security.Price)
                   
    def handlezeroprice(self, symbol, current_price):
        """
        handle scenarios where the price remains zero even after retries.
        """
        last_price = self.tracker.get_last_known_price(symbol)

        if(current_price <= 0):
            return last_price
        else:
           return current_price

  
    def logcorporateactions(self):
        # fetch recent historical data to observe if prices are correctly adjusted
        history = self.History(["msft"], 15, Resolution.Daily)
        if history.empty:
            self.log("historical data for msft is missing or empty.")
        else:
            # log the historical data to see adjusted prices
            self.log(f"recent historical data for msft:\n{history}")

        # access the security object for more detailed information
        security = self.Securities["msft"]
        self.log(f"current msft price: {security.price}, istradable: {security.istradable}")

            # check for corporate actions applied
        if security.IsTradable and security.Price > 0:
            next_market_open = security.Exchange.Hours.GetNextMarketOpen(self.Time, extendedMarket=False)
            next_market_close = security.Exchange.Hours.GetNextMarketClose(self.Time, extendedMarket=False)
            self.log(f"msft details - price: {security.Price}, next market open: {next_market_open}, "
                    f"next market close: {next_market_close}, current time: {self.Time}")
        else:
            # log additional market status details
            market_is_open = security.Exchange.Hours.GetNextMarketOpen(self.Time, extendedMarket=False)
            self.log(f"msft has an invalid price or is not tradable at {self.Time}. "
                    f"market open: {market_is_open}, next market open: {next_market_open if security else 'n/a'}, "
                    f"next market close: {next_market_close if security else 'n/a'}.")
            
                    
    def checkhistoricaldataavailability(self):
        for asset in self.assets:
            history = self.History([asset], 10, Resolution.Daily)
            if history.empty:
                self.log(f"no historical data available for {asset}.")
            else:
                self.log(f"historical data for {asset}: {history.head().to_string(index=True)}")
    def clearsubscriptions(self):
        # manually clear all subscriptions from the subscriptionmanager
        subscriptions = list(self.SubscriptionManager.Subscriptions)
        for subscription in subscriptions:
            self.SubscriptionManager.RemoveSubscription(subscription)
        self.log(f"cleared {len(subscriptions)} subscriptions.")
    def marketcloseaction(self):
        """action to be performed just before the market closes."""
        self.log("performing end-of-day actions before market close.")

    # additional methods (parsedate, validatedaterange, validateassetdata, addsecurities, etc.) remain the same

    def parsedate(self, date_str):
        """helper method to parse a date string into a datetime object."""
        return datetime.strptime(date_str, "%y-%m-%d")

    def validatedaterange(self, start_date, end_date):
        """validate the provided start and end dates against available data for assets."""
        try:
            for symbol in self.assets:
                # get the available historical data range for the asset
                history = self.History([symbol], 1, Resolution.Daily)
                if history.empty:
                    raise ValueError(f"no historical data available for asset {symbol}.")

                available_start_date = history.index.min().date()
                available_end_date = history.index.max().date()

                # adjust start and end dates if they are out of the available range
                if start_date < available_start_date:
                    self.log(f"start date adjusted for {symbol} from {start_date} to {available_start_date}.")
                    start_date = available_start_date
                if end_date > available_end_date:
                    self.log(f"end date adjusted for {symbol} from {end_date} to {available_end_date}.")
                    end_date = available_end_date

        except Exception as e:
            self.log(f"unexpected exception during validatedaterange: {str(e)}")

    def validateassetdata(self):
        """ensure that all assets have market caps and volatilities, removing those that are missing."""
        try:
            missing_market_caps = [asset for asset in self.assets if asset not in self.market_caps]
            missing_volatilities = [asset for asset in self.assets if asset not in self.volatilities]

            # log and remove assets with missing market cap data
            if missing_market_caps:
                self.log(f"removing assets with missing market cap data: {missing_market_caps}")
                self.assets = [asset for asset in self.assets if asset not in missing_market_caps]

            # log and remove assets with missing volatility data
            if missing_volatilities:
                self.log(f"removing assets with missing volatility data: {missing_volatilities}")
                self.assets = [asset for asset in self.assets if asset not in missing_volatilities]

            # if no assets remain after removal, raise an error
            if not self.assets:
                raise ValueError("no valid assets remain after removing those with missing data.")

        except Exception as e:
            self.log(f"unexpected exception during validateassetdata: {str(e)}")

    def addsecurities(self):
        """try to add securities to the portfolio, with error handling."""
        try:
            
            for symbol in self.assets:
                if symbol is not None:
                    try:
                        # add the security to the portfolio
                        security = self.AddEquity(symbol, Resolution.Daily, datanormalizationmode=DataNormalizationMode.ADJUSTED)
                        self.Securities[symbol] = security
                        # self.security_store.append(security.symbol)
                        self.log(f"security added: {symbol}")

                        
                        self.verifysubscriptions() 
                    except Exception as e:
                        self.log(f"error adding security for {symbol}: {str(e)}")
                else:
                    self.log("symbol is none, skipping addition.")

            # check if any securities were added successfully
            if not self.Securities:
                self.log("no valid securities were added to the portfolio.")
                raise ValueError("portfolio could not be initialized with the given assets.")

        except Exception as e:
            self.log(f"unexpected exception during addsecurities: {str(e)}")

    def Rebalance(self):
        """rebalance the portfolio based on the selected weighting scheme."""
        try:
            if not self.Securities:
                self.log("no securities to rebalance.")
                return
            
            if self.weighting_scheme == "market_cap":
                self.marketcapweighting()
            elif self.weighting_scheme == "risk_parity":
                self.riskparityweighting()
            else:
                raise ValueError(f"unknown weighting scheme: {self.weighting_scheme}")

        except Exception as e:
            self.log(f"unexpected exception during rebalance: {str(e)}")
    def marketcapweighting(self):
        """adjust holdings based on market capitalization weighting."""
        try:
            # ensure we have market caps for all assets
            valid_assets = [symbol for symbol in self.assets if symbol in self.market_caps]
            if not valid_assets:
                self.log("no valid assets with market cap data available for rebalancing.")
                return

            # calculate total market cap
            total_market_cap = sum(self.market_caps[symbol] for symbol in valid_assets)
            if total_market_cap == 0:
                self.log("total market cap is zero, cannot rebalance.")
                return

            # calculate weights
            weights = {symbol: self.market_caps[symbol] / total_market_cap for symbol in valid_assets}

            # set holdings with detailed checks
            for symbol, weight in weights.items():
                security = self.Securities[symbol]
                
                   # fetch next market open and close times
                next_market_open = security.Exchange.Hours.GetNextMarketOpen(self.Time, False)
                next_market_close = security.Exchange.Hours.GetNextMarketClose(self.Time, False)
                
                # log detailed information about the security
                self.log(f"processing {symbol}: price = {security.Price}, istradable = {security.istradable}, "
                        f"next market open = {next_market_open}, next market close = {next_market_close}, "
                        f"current time = {self.Time}")


                # check if the market is open and the security is tradable
                if security.HasData  and security.Price > 0 and security.IsTradable:
                    if security.exchange.datetimeisopen(self.time):
                        
                        self.SetHoldings(symbol, weight)
                        # self.tracker.handle_price_update(symbol, security.price)
                        self.log(f"set holdings for {symbol} to {weight * 100:.2f}% based on market cap weighting.")
                    else:
                        self.log(f"market is closed for {symbol} at {self.Time}. "
                             f"next open: {next_market_open}, next close: {next_market_close}.")    
                else:
                    # detailed logging to determine the exact issue
                    if security.Price <= 0:
                        self.checkdataavailabilityandgetlastvalidprice(symbol)
                        self.log(f"{symbol} has an invalid price: {security.price}. potential issues could be data feed interruptions, market data provider delays, or delisting.")
                        self.checkhistoricaldataavailability()
                    if not security.IsTradable:
                        self.log(f"{symbol} is not tradable. this could be due to a delisting, suspension, or regulatory issue.")
                    
                    # check if the security is properly subscribed
                    is_subscribed = symbol in [sub.Symbol.Value for sub in self.SubscriptionManager.Subscriptions]
                    if not is_subscribed:
                        self.log(f"{symbol} is not properly subscribed. check if it was added correctly in initialize.")
                    
                    # log subscription status
                    subscription_status = "subscribed" if is_subscribed else "not subscribed"
                    self.log(f"{symbol} subscription status: {subscription_status}.")
                    continue

        except Exception as e:
            self.log(f"unexpected exception during marketcapweighting: {str(e)}")

    def verifysubscriptions(self):
        subscribed_symbols = [sub.Symbol.Value for sub in self.SubscriptionManager.Subscriptions]
        self.log(f"currently subscribed symbols: {subscribed_symbols}")

        # check for specific symbols
        for symbol in self.assets:
            if symbol not in subscribed_symbols:
                self.log(f"{symbol} is not properly subscribed. check if it was added correctly in initialize.")        
    def riskparityweighting(self):
        """adjust holdings based on risk parity weighting."""
        try:
            inv_vols = {symbol: 1 / self.volatilities[symbol] for symbol in self.assets if self.volatilities[symbol] != 0}
            total_inv_vols = sum(inv_vols.values())
            weights = {symbol: inv_vol / total_inv_vols for symbol, inv_vol in inv_vols.items()}

            for symbol, weight in weights.items():
                # ensure we have a valid price before setting holdings
                if symbol is not None and symbol in self.Securities and  self.Securities[symbol].HasData and self.Securities[symbol].Price > 0:
                    self.SetHoldings(symbol, weight)
                    self.log(f"set holdings for {symbol} to {weight * 100:.2f}% based on risk parity weighting")
                else:
                    self.log(f"skipping {symbol} as it doesn't have a valid price yet.")
                    continue

        except Exception as e:
            self.log(f"unexpected exception during riskparityweighting: {str(e)}")

    def ondata(self, data: slice):
        """process incoming data and handle invalid prices for assets like msft."""
        try:
            if self.IsWarmingUp:
                self.log("currently warming up, not processing data.")
                return

            for symbol in self.assets:
                if symbol in data.Bars:
                    bar = data.Bars[symbol]
                    
                    # check for valid price
                    if bar is not None and bar.Close > 0:
                        self.log(f"received valid data for {symbol}: close price = {bar.close}")
                    else:
                        self.log(f"{symbol} has an invalid price: {bar.close if bar else 'none'}.")

                        # further diagnostics for invalid price
                        security = self.Securities[symbol]
                        
                        # log market status and tradability
                        if not security.IsTradable:
                            self.log(f"{symbol} is not tradable. potential reasons include delisting, suspension, or regulatory issues.")
                        
                        if not security.Exchange.DateTimeIsOpen(self.Time):
                            self.log(f"market is closed for {symbol} at {self.Time}. "
                                    f"next open: {security.Exchange.Hours.GetNextMarketOpen(self.Time, False)}, "
                                    f"next close: {security.Exchange.Hours.GetNextMarketClose(self.Time, False)}.")

                        # check historical data to see if the issue is consistent
                        history = self.History([symbol], 10, Resolution.Daily)
                        if history.empty or history['close'].min() <= 0:
                            self.log(f"historical data for {symbol} shows invalid prices or missing data. "
                                    f"this suggests a persistent data issue or asset delisting.")
                        
                        # log subscription and data provider status
                        subscription_status = "subscribed" if symbol in [sub.symbol.value for sub in self.self.SubscriptionManager.Subscription] else "not subscribed"
                        self.log(f"{symbol} subscription status: {subscription_status}. check if the subscription is correctly set in initialize.")
                        custom_price = self.custom_prices.get(symbol, 0)
                        self.log(f"custom_price----------> {custom_price}")

                else:
                    # provide detailed logs to understand the absence of data
                    self.log(f"{symbol} is not found in data keys at Time {self.Time}. checking further...")

                    # check additional security information
                    if symbol in self.Securities:
                        security = self.Securities[symbol]
                        if not security.IsTradable:
                            self.log(f"{symbol} is not tradable. possibly delisted or trading halted.")
                        if security.price <= 0:
                            self.log(f"{symbol} has an invalid price: {security.price}")
                        if not security.Exchange.DateTimeIsOpen(self.Time):
                            self.log(f"market is closed for {symbol}.")
                    else:
                        self.log(f"{symbol} is not found in the Securities dictionary. possible reasons include incorrect initialization or subscription errors.")

        except Exception as e:
            self.log(f"unexpected exception during ondata: {str(e)}")

