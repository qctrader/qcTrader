import json
from datetime import timedelta, datetime
from QuantConnect import DataNormalizationMode
import numpy as np
import sys
import os

# Determine the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the correct Launcher/bin/Release directory
release_dir = os.path.join(current_dir, '..', 'Launcher', 'bin', 'Release')

# Normalize the path to remove any redundant separators or up-level references
release_dir = os.path.normpath(release_dir)

print(f"release_dir--------------->{release_dir}")

# Add the directory to sys.path if it's not already in sys.path
if release_dir not in sys.path:
    sys.path.append(release_dir)

from AlgorithmImports import QCAlgorithm, Resolution, Slice, Market, DateRules, TimeRules


class BacktestingAlgorithm(QCAlgorithm):
    def Initialize(self):
        try:

            # Force logging level and handler settings (if applicable)
            self.Debugging = True
            self.ClearSubscriptions()
            self.UniverseManager.Clear()  # Clears all universes if any
  
            
            # Fetch and parse the portfolio JSON string
            portfolio_str = self.GetParameter("portfolio")
            if portfolio_str is None:
                raise ValueError("Portfolio parameter is missing.")
            self.Log(f"Fetched 'portfolio' parameter: {portfolio_str}")

            portfolio = json.loads(portfolio_str)
            # Extract assets from the portfolio object
            self.assets = portfolio.get("assets", [])
            if not self.assets:
                raise ValueError("No assets provided in the portfolio.")

            self.Log(f"Assets: {self.assets}")
            
            # Get weighting scheme and rebalancing frequency
            self.weighting_scheme = self.GetParameter("weighting_scheme")
            self.rebalancing_frequency = self.GetParameter("rebalancing_frequency")

            # Fetch and parse market caps and volatilities
            market_caps_str = self.GetParameter("market_caps")
            volatilities_str = self.GetParameter("volatilities")
            if market_caps_str is None or volatilities_str is None:
                raise ValueError("Market caps or volatilities parameters are missing.")

            self.market_caps = json.loads(market_caps_str)
            self.volatilities = json.loads(volatilities_str)

            # Ensure that all assets have corresponding market_caps and volatilities
            self.ValidateAssetData()
            # Add an example security
            self.securities["AAPL"] = self.AddEquity("AAPL", Resolution.Daily, dataNormalizationMode=DataNormalizationMode.Adjusted)
            self.AddSecurities()

            # Set the benchmark with a specified resolution
            self.SetBenchmark(self.AddEquity("SPY", Resolution.Daily).Symbol)

            # If using universes, ensure to set the resolution in UniverseSettings
            self.UniverseSettings.Resolution = Resolution.Daily


            # Read start and end dates dynamically from parameters
            start_date_str = self.GetParameter("start_date")
            end_date_str = self.GetParameter("end_date")

            # Convert the date strings to datetime objects
            start_date = self.ParseDate(start_date_str)
            end_date = self.ParseDate(end_date_str)

            # Validate the provided dates against available data
            self.ValidateDateRange(start_date, end_date)

            # Set the start and end dates for backtesting
            self.SetStartDate(start_date.year, start_date.month, start_date.day)
            self.SetEndDate(end_date.year, end_date.month, end_date.day)

            # Set initial capital from the portfolio parameter, ensure it's correctly parsed
            initial_capital = portfolio.get("initial_capital", None)
            if initial_capital is not None:
                try:
                    initial_capital = float(initial_capital)
                except ValueError:
                    raise ValueError("Invalid initial capital value provided.")
            else:
                initial_capital = 100000  # Default to $100,000 if not provided
            self.SetCash(initial_capital)
            self.Log(f"Initial capital set to: {initial_capital}")

            # Schedule rebalancing at market open
            self.Schedule.On(
                self.DateRules.EveryDay(self.assets[0]),
                self.TimeRules.AfterMarketOpen(self.assets[0], 1),  # 1 minute after market open
                self.Rebalance
            )

            # Schedule a daily action at market close for additional tasks or logging
            self.Schedule.On(
                self.DateRules.EveryDay(self.assets[0]),
                self.TimeRules.BeforeMarketClose(self.assets[0], 1),  # 1 minute before market close
                self.MarketCloseAction
            )

        except Exception as e:
            self.Log(f"Unexpected exception during Initialize: {str(e)}")
            
    def ClearSubscriptions(self):
        # Manually clear all subscriptions from the SubscriptionManager
        subscriptions = list(self.SubscriptionManager.Subscriptions)
        for subscription in subscriptions:
            self.SubscriptionManager.RemoveSubscription(subscription)
        self.Log(f"Cleared {len(subscriptions)} subscriptions.")
    def MarketCloseAction(self):
        """Action to be performed just before the market closes."""
        self.Log("Performing end-of-day actions before market close.")

    # Additional methods (ParseDate, ValidateDateRange, ValidateAssetData, AddSecurities, etc.) remain the same

    def ParseDate(self, date_str):
        """Helper method to parse a date string into a datetime object."""
        return datetime.strptime(date_str, "%Y-%m-%d")

    def ValidateDateRange(self, start_date, end_date):
        """Validate the provided start and end dates against available data for assets."""
        try:
            for symbol in self.assets:
                # Get the available historical data range for the asset
                history = self.History([symbol], 1, Resolution.Daily)
                if history.empty:
                    raise ValueError(f"No historical data available for asset {symbol}.")

                available_start_date = history.index.min().date()
                available_end_date = history.index.max().date()

                # Adjust start and end dates if they are out of the available range
                if start_date < available_start_date:
                    self.Log(f"Start date adjusted for {symbol} from {start_date} to {available_start_date}.")
                    start_date = available_start_date
                if end_date > available_end_date:
                    self.Log(f"End date adjusted for {symbol} from {end_date} to {available_end_date}.")
                    end_date = available_end_date

        except Exception as e:
            self.Log(f"Unexpected exception during ValidateDateRange: {str(e)}")

    def ValidateAssetData(self):
        """Ensure that all assets have market caps and volatilities, removing those that are missing."""
        try:
            missing_market_caps = [asset for asset in self.assets if asset not in self.market_caps]
            missing_volatilities = [asset for asset in self.assets if asset not in self.volatilities]

            # Log and remove assets with missing market cap data
            if missing_market_caps:
                self.Log(f"Removing assets with missing market cap data: {missing_market_caps}")
                self.assets = [asset for asset in self.assets if asset not in missing_market_caps]

            # Log and remove assets with missing volatility data
            if missing_volatilities:
                self.Log(f"Removing assets with missing volatility data: {missing_volatilities}")
                self.assets = [asset for asset in self.assets if asset not in missing_volatilities]

            # If no assets remain after removal, raise an error
            if not self.assets:
                raise ValueError("No valid assets remain after removing those with missing data.")

        except Exception as e:
            self.Log(f"Unexpected exception during ValidateAssetData: {str(e)}")

    def AddSecurities(self):
        """Try to add securities to the portfolio, with error handling."""
        try:
            for symbol in self.assets:
                if symbol is not None:
                    try:
                        # Add the security to the portfolio
                        security = self.AddEquity(symbol, Resolution.Daily, dataNormalizationMode=DataNormalizationMode.Adjusted)
                        self.securities[symbol] = security
                        self.Log(f"Security added: {symbol}")

                        # Check availability of historical data for the added security
                        history = self.History([symbol], 1, Resolution.Daily)
                        if not history.empty:
                            self.Log(f"Historical data for {symbol} available from {history.index.min()} to {history.index.max()}.")
                        else:
                            self.Log(f"No historical data available for {symbol}.")
                            
                    except Exception as e:
                        self.Log(f"Error adding security for {symbol}: {str(e)}")
                else:
                    self.Log("Symbol is None, skipping addition.")

            # Check if any securities were added successfully
            if not self.securities:
                self.Log("No valid securities were added to the portfolio.")
                raise ValueError("Portfolio could not be initialized with the given assets.")

        except Exception as e:
            self.Log(f"Unexpected exception during AddSecurities: {str(e)}")

    def Rebalance(self):
        """Rebalance the portfolio based on the selected weighting scheme."""
        try:
            if not self.securities:
                self.Log("No securities to rebalance.")
                return
            
            if self.weighting_scheme == "market_cap":
                self.MarketCapWeighting()
            elif self.weighting_scheme == "risk_parity":
                self.RiskParityWeighting()
            else:
                raise ValueError(f"Unknown weighting scheme: {self.weighting_scheme}")

        except Exception as e:
            self.Log(f"Unexpected exception during Rebalance: {str(e)}")

    def MarketCapWeighting(self):
        """Adjust holdings based on market capitalization weighting."""
        try:
            # Ensure we have market caps for all assets
            valid_assets = [symbol for symbol in self.assets if symbol in self.market_caps]
            if not valid_assets:
                self.Log("No valid assets with market cap data available for rebalancing.")
                return

            # Calculate total market cap
            total_market_cap = sum(self.market_caps[symbol] for symbol in valid_assets)
            if total_market_cap == 0:
                self.Log("Total market cap is zero, cannot rebalance.")
                return

            # Calculate weights
            weights = {symbol: self.market_caps[symbol] / total_market_cap for symbol in valid_assets}

            # Set holdings with detailed checks
            for symbol, weight in weights.items():
                security = self.Securities[symbol]
                if security.Price > 0 and security.IsTradable:
                    self.SetHoldings(symbol, weight)
                    self.Log(f"Set holdings for {symbol} to {weight * 100:.2f}% based on market cap weighting")
                else:
                    # Detailed logging to determine the exact issue
                    if security.Price <= 0:
                        self.Log(f"{symbol} has an invalid price: {security.Price}")
                    if not security.IsTradable:
                        self.Log(f"{symbol} is not tradable.")
                    if not security.Exchange.Hours.IsOpen(self.Time):
                        self.Log(f"Market is closed for {symbol} at {self.Time}.")

        except Exception as e:
            self.Log(f"Unexpected exception during MarketCapWeighting: {str(e)}")

    def RiskParityWeighting(self):
        """Adjust holdings based on risk parity weighting."""
        try:
            inv_vols = {symbol: 1 / self.volatilities[symbol] for symbol in self.assets if self.volatilities[symbol] != 0}
            total_inv_vols = sum(inv_vols.values())
            weights = {symbol: inv_vol / total_inv_vols for symbol, inv_vol in inv_vols.items()}

            for symbol, weight in weights.items():
                # Ensure we have a valid price before setting holdings
                if symbol is not None and symbol in self.Securities and self.Securities[symbol].Price > 0:
                    self.SetHoldings(symbol, weight)
                    self.Log(f"Set holdings for {symbol} to {weight * 100:.2f}% based on risk parity weighting")
                else:
                    self.Log(f"Skipping {symbol} as it doesn't have a valid price yet.")

        except Exception as e:
            self.Log(f"Unexpected exception during RiskParityWeighting: {str(e)}")

    def OnData(self, data: Slice):
        """Process incoming data."""
        try:
            if self.IsWarmingUp:
                self.Log("Currently warming up, not processing data for MSFT.")
                return

            for symbol in self.assets:
                if symbol in data.Bars:
                    bar = data.Bars[symbol]
                    if bar is not None and bar.Close > 0:
                        price = bar.Close
                        self.Log(f"Received data for {symbol}: Close Price = {price}")
                    else:
                        self.Log(f"{symbol} has an invalid price or bar data is None.")
                else:
                    # Provide detailed logs to understand the absence of data
                    self.Log(f"{symbol} is not found in data keys.")

                    # Check additional security information
                    if symbol in self.Securities:
                        security = self.Securities[symbol]
                        if not security.IsTradable:
                            self.Log(f"{symbol} is not tradable.")
                        if security.Price <= 0:
                            self.Log(f"{symbol} has an invalid price: {security.Price}")
                        # Check if the market is open
                        if not security.Exchange.Hours.IsOpen(self.Time):
                            self.Log(f"Market is closed for {symbol}.")
                    else:
                        self.Log(f"{symbol} is not found in securities.")

        except Exception as e:
            self.Log(f"Unexpected exception during OnData: {str(e)}")
