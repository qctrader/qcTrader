# Determine the directory of the current script
import os
import sys

from QuantConnect import DataNormalizationMode


current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the correct Launcher/bin/Release directory
release_dir = os.path.join(current_dir, '..', 'Launcher', 'bin', 'Release')

# Normalize the path to remove any redundant separators or up-level references
release_dir = os.path.normpath(release_dir)

print(f"release_dir--------------->{release_dir}")

# Add the directory to sys.path if it's not already in sys.path
if release_dir not in sys.path:
    sys.path.append(release_dir)

from AlgorithmImports import QCAlgorithm, Resolution, Slice


class MSFTDataTestAlgorithm(QCAlgorithm):
    def Initialize(self):

        self.Debugging = True
        self.SetTimeZone("America/New_York")
        self.SetStartDate(2020, 1, 1)   # Adjust to match the start date of your data
        self.SetEndDate(2024, 8, 30)    # Adjust to match the end date of your data
        self.SetCash(100000)            # Initial cash

        # Enable detailed logging
        self.Debug("Initializing MSFT Data Test Algorithm")

        # Add MSFT with daily resolution and adjusted normalization mode
        self.msft = self.AddEquity("MSFT", Resolution.Daily, dataNormalizationMode=DataNormalizationMode.Adjusted).Symbol
        # Set the benchmark with a specified resolution
        self.SetBenchmark(self.AddEquity("MSFT", Resolution.Daily).Symbol)
        self.Debug(f"Added MSFT with adjusted data. Symbol: {self.msft}")

        security = self.Securities[self.msft]
        if not security.Exchange.DateTimeIsOpen(self.Time):
            self.Error(f"Market is closed for MSFT at {self.Time}. Check data and market hours.")

    def OnData(self, data: Slice):
        self.Debug(f"Current algorithm time: {self.Time}, Data slice time: {data.Time}")
        # Ensure that OnData is being called
        self.Debug("OnData called")  # Ensure this log is always visible
        if not data.Bars:
              self.Error("No Bars found in this OnData call.")

        # Check if MSFT data is present
        if self.msft in data.Bars:
            bar = data.Bars[self.msft]
            if bar and bar.Close > 0:
                self.Debug(f"Received MSFT data: Close Price = {bar.Close}, Volume = {bar.Volume}")
            else:
                self.Error("Invalid MSFT price data: Data is present but invalid or price is zero.")
        else:
            self.Error("MSFT data is not found in this slice.")

    def OnEndOfAlgorithm(self):
        self.Debug("Algorithm finished running.")

