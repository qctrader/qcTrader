import json
import yfinance as yf
import os
import pandas as pd
import zipfile
from datetime import datetime

class QuantConnectDataUpdater:
    def __init__(self, parameters):
        self.parameters = parameters
        self.data_folder = os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release",  "Data",self.parameters["asset_class"],self.parameters["market"],self.parameters["resolution"])
        self.map_files_path = os.path.join(self.data_folder, self.parameters["asset_class"],self.parameters["market"],self.parameters["resolution"], "map_files" )
        self.factor_files_path = os.path.join(self.data_folder, self.parameters["asset_class"],self.parameters["market"],self.parameters["resolution"],"factor_files" )
        
        # Parse the JSON string
        portfolio_dict = json.loads(self.parameters['portfolio'])

        # Extract the assets
        self.assets = portfolio_dict.get("assets", [])


    def _get_zip_file_path(self, symbol):
        """
        Returns the path to the zip file for a given symbol.
        """
        return os.path.join(self.data_folder, f"{symbol.lower()}.zip")
    
    def _is_path_present(self, symbol):
        """
        Checks if the data for the given symbol and date range is present.
        """
        zip_file_path = self._get_zip_file_path(symbol)
        absolute_path = os.path.abspath(zip_file_path)
        directory = os.path.dirname(absolute_path)
        if not os.path.exists(directory):
            print(f"The directory '{directory}' does not exist.")
        else:
            print(f"The directory '{directory}' exists.")

        if os.path.exists(absolute_path):
            if os.path.isfile(absolute_path):
                print(f"'{symbol.lower()}.zip' found at '{absolute_path}'.")
                return absolute_path
            else:
                print(f"'{absolute_path}' exists but is not a file.")
                return ''
        else:
            print(f"'{symbol.lower()}.zip' not found at '{absolute_path}'.")
            return ''
    def parse_date_column(self, date_column):
        """Attempts to parse a date column with different formats."""
        # First try the more specific format '%Y%m%d %H:%M'
        try:
            return pd.to_datetime(date_column, format='%Y%m%d %H:%M', errors='raise')
        except ValueError:
            # If it fails, fall back to '%Y%m%d'
            try:
                return pd.to_datetime(date_column, format='%Y%m%d', errors='raise')
            except ValueError:
                # If it still fails, return NaT
                return pd.to_datetime(date_column, errors='coerce')    
    def check_data_availability(self,  symbol, start_date, end_date):
        """Check if data for a specific asset is available in the Data folder for the given date range."""
         # Check if data is already present
        absolute_path = self._is_path_present(symbol)
        if absolute_path != '':  # Ensure the file exists and path is not empty
            try:
                with zipfile.ZipFile(absolute_path, 'r') as z:
                    # List all CSV files in the ZIP and process them
                    dates = []
                    for f in z.namelist():
                        if f.endswith('.csv'):  # Only process CSV files
                            print(f"Processing file: {f}")
                            with z.open(f) as csvfile:
                                # Read the CSV file without headers
                                df = pd.read_csv(csvfile, header=None)

                                # Assuming the first column contains dates
                                # Strip whitespace from the first column to avoid parsing issues
                                df[0] = df[0].astype(str).str.strip()

                                # Attempt to parse the first column with multiple date formats
                                df[0] = self.parse_date_column(df[0])
                                
                                df = df.dropna(subset=[0])  # Drop rows where the date could not be parsed
                                
                                # Extract the minimum and maximum dates
                                if not df.empty:
                                    min_date = df[0].min().date()
                                    max_date = df[0].max().date()
                                    dates.append((min_date, max_date))
                                    print(f"Found date range in {f}: {min_date} to {max_date}")
                                else:
                                    print(f"Skipping file {f}: No valid dates found.")

                    if dates:
                        # Find the overall minimum and maximum dates available in all CSV files
                        available_start_date = min(date_range[0] for date_range in dates)
                        available_end_date = max(date_range[1] for date_range in dates)
                        print(f"Data for {symbol} is available from {available_start_date} to {available_end_date}.")
                        
                        # Check if the required date range is within the available data range
                        if start_date >= available_start_date and end_date <= available_end_date:
                            print(f"Data for {symbol} is already available for the required date range.")
                            return True
                        else:
                            print(f"Data for {symbol} is not available for the required date range. Update needed.")
                            return False
                    else:
                        print(f"No valid date data available inside {absolute_path}.")
                        return False
            except zipfile.BadZipFile:
                print(f"Error: '{absolute_path}' is not a valid zip file.")
                return False
            except zipfile.LargeZipFile:
                print(f"Error: '{absolute_path}' is too large and requires ZIP64 extension.")
                return False
            except Exception as e:
                print(f"Unexpected error opening zip file '{absolute_path}': {e}")
                return False
        else:
            print(f"Data file for {symbol} not found.")
            return False
    
    def _download_data(self, symbol, start_date, end_date):
        """
        Downloads data for the given symbol and date range using yfinance.
        """
        data = yf.download(symbol, start=start_date, end=end_date)
        if not data.empty:
            data.index = data.index.strftime('%Y%m%d %H:%M')
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            data.columns = ['open', 'high', 'low', 'close', 'volume']
        return data
    
    def _update_zip_file(self, symbol, new_data):
        """
        Updates the existing ZIP file with new data or creates a new one if it doesn't exist.
        """
        zip_file_path = self._get_zip_file_path(symbol)
        csv_file_name = f"{symbol.lower()}.csv"
        
        if os.path.exists(zip_file_path):
            # Update existing CSV inside the ZIP
            with zipfile.ZipFile(zip_file_path, 'a') as zip_file:
                # Read existing data
                with zip_file.open(csv_file_name) as csv_file:
                    existing_data = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                
                # Convert the index to datetime if it's not already
                if not pd.api.types.is_datetime64_any_dtype(existing_data.index):
                    existing_data.index = pd.to_datetime(existing_data.index, format='%Y%m%d %H:%M')
                    
                if not pd.api.types.is_datetime64_any_dtype(new_data.index):
                    new_data.index = pd.to_datetime(new_data.index, format='%Y%m%d %H:%M')

                # Combine and remove duplicates
                combined_data = pd.concat([existing_data, new_data]).drop_duplicates()
                combined_data = combined_data.sort_index()
                
                # Write the combined data back to the CSV file in the ZIP without headers
                with zip_file.open(csv_file_name, 'w') as csv_file:
                    combined_data.to_csv(csv_file, header=False)
        else:
            # Create a new ZIP file with the CSV without headers
            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                with zip_file.open(csv_file_name, 'w') as csv_file:
                    new_data.to_csv(csv_file, header=False)
    
    def update_data(self):
        """
        Main method to check and update data.
        """
        # Ensure dates are in the correct format
        start_date = self.parameters["start_date"]
        end_date = self.parameters["end_date"]
        
        for asset in self.assets:
            data_available = self.check_data_availability(asset, start_date, end_date)
            
            if not data_available:
                # Download missing data
                new_data = self._download_data(asset, start_date, end_date)
                
                if new_data.empty:
                    print(f"No new data available for {asset} between {start_date} and {end_date}.")
                    return
                
                # Update or create ZIP file with new data
                self._update_zip_file(asset, new_data)
                print(f"Data for {asset} from {start_date} to {end_date} has been updated.")
        
        