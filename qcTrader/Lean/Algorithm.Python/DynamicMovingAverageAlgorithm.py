from AlgorithmImports import *
from datetime import datetime  # Import datetime module

class DynamicMovingAverageAlgorithm(QCAlgorithm):
    def Initialize(self):
        try:
            self.Log("Initialize: Algorithm initialization started")
            
            # Retrieve critical parameters
            self.short_ma_period = int(self.GetParameter("ShortMAPeriod", "50"))
            self.Log(f"Initialize: Short MA period set to {self.short_ma_period}")
            
            self.long_ma_period = int(self.GetParameter("LongMAPeriod", "200"))
            self.Log(f"Initialize: Long MA period set to {self.long_ma_period}")
            
            custom_start_date_str = self.GetParameter("StartDate", "2020-07-01")
            custom_end_date_str = self.GetParameter("EndDate", "2020-07-31")
            initial_cash = float(self.GetParameter("InitialCash", "100000"))
            self.Log(f"Initialize: Start date set to {custom_start_date_str}, End date set to {custom_end_date_str}, Initial cash set to {initial_cash}")

            # Convert string dates to datetime objects
            custom_start_date = datetime.strptime(custom_start_date_str, "%Y-%m-%d")
            custom_end_date = datetime.strptime(custom_end_date_str, "%Y-%m-%d")

            # Set the start and end dates for the backtest
            self.SetStartDate(custom_start_date)  
            self.Log("Initialize: Start date applied")
            
            self.SetEndDate(custom_end_date)     
            self.Log("Initialize: End date applied")
            
            self.SetCash(initial_cash)    
            self.Log(f"Initialize: Initial cash set to {initial_cash}")

            # Define the stock to trade
            stock_symbol = self.GetParameter("Stock", 'AAPL')
            self.stock = self.AddEquity(stock_symbol, Resolution.Daily)
            self.Log(f"Initialize: Equity added for {stock_symbol} with Resolution.Daily")
            
            # Set a shorter warm-up period initially
            self.SetWarmUp(10, Resolution.Daily)
            self.Log("Initialize: Warm-up period set to 10 days with Resolution.Daily")

            # Set a flag to know when warm-up is complete
            self.warmup_complete = False
            self.Log("Initialize: Warm-up complete flag initialized")

            # Log the completion of the critical initialization phase
            self.Log("Initialize: Critical initialization complete, waiting for warm-up to finish")
        except Exception as e:
            self.Log(f"Initialize: Exception occurred - {str(e)}")

    def OnWarmupFinished(self):
        try:
            # Log that warm-up is complete
            self.Log("OnWarmupFinished: Warm-up complete, setting up moving averages")

            # Setup indicators after warm-up to avoid long initialization times
            self.short_moving_average = self.SMA(self.stock.Symbol, self.short_ma_period, Resolution.Daily)
            self.Log(f"OnWarmupFinished: Short MA set for {self.stock.Symbol} with period {self.short_ma_period}")

            self.long_moving_average = self.SMA(self.stock.Symbol, self.long_ma_period, Resolution.Daily)
            self.Log(f"OnWarmupFinished: Long MA set for {self.stock.Symbol} with period {self.long_ma_period}")

            # Initialize variables for tracking orders
            self.previous_short_ma = None
            self.previous_long_ma = None
            self.Log("OnWarmupFinished: Previous MA values initialized")

            # Mark warm-up as complete
            self.warmup_complete = True
            self.Log("OnWarmupFinished: Warm-up flag set to true, algorithm ready to process data")
        except Exception as e:
            self.Log(f"OnWarmupFinished: Exception occurred - {str(e)}")

    def OnData(self, data):
        try:
            self.Log(f"OnData: Processing data for {self.Time}")

            # Wait until warm-up is complete and indicators are set up
            if not self.warmup_complete:
                self.Log("OnData: Waiting for warm-up to complete")
                return

            if not self.short_moving_average.IsReady or not self.long_moving_average.IsReady:
                self.Log("OnData: Moving averages not ready")
                return
            
            current_short_ma = self.short_moving_average.Current.Value
            current_long_ma = self.long_moving_average.Current.Value
            
            self.Log(f"OnData: Short MA: {current_short_ma}, Long MA: {current_long_ma}")
            
            if self.previous_short_ma is not None and self.previous_long_ma is not None:
                self.Log(f"OnData: Previous Short MA: {self.previous_short_ma}, Previous Long MA: {self.previous_long_ma}")
                if self.previous_short_ma < self.previous_long_ma and current_short_ma > current_long_ma:
                    self.Log("OnData: Buy signal triggered")
                    self.SetHoldings(self.stock.Symbol, 1.0)
                elif self.previous_short_ma > self.previous_long_ma and current_short_ma < current_long_ma:
                    self.Log("OnData: Sell signal triggered")
                    self.SetHoldings(self.stock.Symbol, 0.0)
            else:
                self.Log("OnData: Previous MA values are None, skipping trade decision")
            
            self.previous_short_ma = current_short_ma
            self.previous_long_ma = current_long_ma
            self.Log(f"OnData: MA values updated - Previous Short MA: {self.previous_short_ma}, Previous Long MA: {self.previous_long_ma}")
        except Exception as e:
            self.Log(f"OnData: Exception occurred - {str(e)}")
