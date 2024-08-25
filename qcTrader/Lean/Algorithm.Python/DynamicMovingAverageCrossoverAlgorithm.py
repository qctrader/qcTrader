import subprocess
import numpy as np
from AlgorithmImports import *

class DynamicMovingAverageCrossoverAlgorithm(QCAlgorithm):
    def Initialize(self):
        try:
            self.symbol = self.GetParameter("Stock", "SPY")
            self.short_ma_period = int(self.GetParameter("ShortMAPeriod", "10"))
            self.long_ma_period = int(self.GetParameter("LongMAPeriod", "50"))
            self.start_date = self.GetParameter("StartDate", "2020-01-01")
            self.end_date = self.GetParameter("EndDate", "2021-01-01")
            self.cash = float(self.GetParameter("InitialCash", "100000"))

            self.SetStartDate(*map(int, self.start_date.split('-')))
            self.SetEndDate(*map(int, self.end_date.split('-')))
            self.SetCash(self.cash)

            self.symbol = self.AddEquity(self.symbol, Resolution.Daily).Symbol
            self.short_ma = self.SMA(self.symbol, self.short_ma_period, Resolution.Daily)
            self.long_ma = self.SMA(self.symbol, self.long_ma_period, Resolution.Daily)

            self.invested = False
        except Exception as e:
            self.Error(f"Error during Initialize: {e}")

    def OnData(self, data):
        try:
            if not self.short_ma.IsReady or not self.long_ma.IsReady:
                return

            # Call the external script to make the decision
            result = subprocess.run(
                ['python3', 'decision_logic.py', str(self.short_ma.Current.Value), 
                 str(self.long_ma.Current.Value), str(self.invested)],
                capture_output=True, text=True
            )

            # Get the decision from the output
            decision = result.stdout.strip()

            # Act on the decision
            if decision == 'buy':
                self.SetHoldings(self.symbol, 1)  # Invest 100% of the portfolio in the asset
                self.invested = True
                self.Log(f"Purchased {self.symbol} at {self.Time}")
            elif decision == 'sell':
                self.Liquidate(self.symbol)  # Sell all holdings in the asset
                self.invested = False
                self.Log(f"Sold {self.symbol} at {self.Time}")
        except Exception as e:
            self.Error(f"Error during OnData: {e}")


    def OnEndOfAlgorithm(self):
        try:
            # Collect daily returns
            daily_returns = [x.DailyPerformance for x in self.Portfolio.AllHoldings]

            # Call the external script using subprocess
            result = subprocess.run(
                ['python3', 'calculate_statistics.py'] + list(map(str, daily_returns)),
                capture_output=True, text=True
            )

            # Parse the results
            daily_std_dev, sharpe_ratio = map(float, result.stdout.strip().split())

            # Log the results
            self.Log(f"Daily Standard Deviation: {daily_std_dev:.2%}")
            self.Log(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        except Exception as e:
            self.Error(f"Error during OnEndOfAlgorithm: {e}")
