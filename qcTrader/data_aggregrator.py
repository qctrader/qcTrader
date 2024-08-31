import json
import yfinance as yf
import os
import pandas as pd
import zipfile
import pandas as pd
from io import BytesIO
class QuantConnectDataUpdater:
    def __init__(self, data_config_paramters, parameters):
        self.parameters = parameters
        self.data_config_paramters = data_config_paramters
        self.data_folder = os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release",  "Data",self.data_config_paramters["asset_class"],self.data_config_paramters["market"],self.data_config_paramters["resolution"])
        self.map_files_path = os.path.join(self.data_folder, "map_files" )
        self.factor_files_path = os.path.join(self.data_folder,"factor_files" )
        
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
    
    def _update_zip_file_factor_file(self,symbol, formatted_data):
        # Define the path for the ZIP file
        zip_file_path = self.factor_files_path
        csv_file_name = f"{symbol.lower()}.csv"

        # Remove existing ZIP file if it exists
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)
            print(f"Removed existing ZIP file: {zip_file_path}")

        # Create a new ZIP file and add the formatted data as a CSV
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            with zip_file.open(csv_file_name, 'w') as csv_file:
                # Convert formatted data to bytes and write to the CSV in the ZIP
                buffer = BytesIO()
                buffer.write('\n'.join(formatted_data).encode('utf-8'))
                buffer.seek(0)
                csv_file.write(buffer.read())
            print(f"Created new ZIP file with updated factor data: {zip_file_path}")

    def _update_zip_file(self, symbol, new_data):
        """
        Replaces the existing CSV data in the ZIP file with new data or creates a new ZIP if it doesn't exist.
        """
        zip_file_path = self._get_zip_file_path(symbol)
        csv_file_name = f"{symbol.lower()}.csv"

        # Ensure the index is in datetime format and in UTC
        if not pd.api.types.is_datetime64_any_dtype(new_data.index):
            new_data.index = pd.to_datetime(new_data.index)

        # Set the index to UTC
        new_data.index = new_data.index.tz_convert('UTC') if new_data.index.tz else new_data.index.tz_localize('UTC')

        # Format the index to the desired format 'YYYYMMDD HH:MM'
        new_data.index = new_data.index.strftime('%Y%m%d %H:%M')

        # Log the new data for debugging
        print(f"New data shape for {symbol}: {new_data.shape}")

        # Open the ZIP file in write mode to replace any existing files
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            # Write the new data to the ZIP file, replacing any existing CSV file
            with zip_file.open(csv_file_name, 'w') as csv_file:
                # Use a buffer to write the DataFrame into the ZIP
                buffer = BytesIO()
                # Write only the new data with the formatted dates, excluding headers
                new_data.to_csv(buffer, header=False, encoding='utf-8')
                buffer.seek(0)
                csv_file.write(buffer.read())

        print(f"Successfully replaced the data in the ZIP file for {symbol}.")
    def _download_factor_file_with_close(self, symbol, start_date, end_date):
        # Fetch the ticker data using yfinance
        ticker = yf.Ticker(symbol)

        # Download historical data (including Close prices) within the specified date range
        hist = ticker.history(start=start_date, end=end_date)

        # Fetch dividends and splits data
        dividends = ticker.dividends
        splits = ticker.splits

        # Convert indices to timezone-naive to match the start and end dates
        dividends.index = dividends.index.tz_localize(None)
        splits.index = splits.index.tz_localize(None)

        # Filter dividends and splits within the specified date range
        dividends = dividends[(dividends.index >= pd.to_datetime(start_date)) & (dividends.index <= pd.to_datetime(end_date))]
        splits = splits[(splits.index >= pd.to_datetime(start_date)) & (splits.index <= pd.to_datetime(end_date))]

        # Calculate price factors using cumulative product (considering dividends)
        price_factors = (1 - dividends / hist['Close']).fillna(1).cumprod().rename('price_factor')

        # Create split factors (cumulative product of splits, replace 0 with 1)
        split_factors = splits.cumprod().replace(0, 1).rename('split_factor')

        # Merge factors with the historical data
        factor_data = pd.DataFrame({
            'date': hist.index,
            'close_price': hist['Close']
        })
        
        # Combine price factors and split factors into the data
        factor_data = factor_data.join(price_factors, on='date').join(split_factors, on='date')
        factor_data[['price_factor', 'split_factor']] = factor_data[['price_factor', 'split_factor']].fillna(method='ffill').fillna(1)

        # Format date to YYYYMMDD
        factor_data['date'] = factor_data['date'].dt.strftime('%Y%m%d')

        # Rearrange and format the data as requested
        factor_data = factor_data[['date', 'price_factor', 'split_factor', 'close_price']]

        # Convert to the required format: YYYYMMDD, Price Factor, Split Factor, Close Price
        factor_data = factor_data.apply(lambda row: f"{row['date']},{row['price_factor']:.7f},{row['split_factor']:.1f},{row['close_price']:.2f}", axis=1)

        # Return as a list of formatted strings
        return factor_data.tolist()

    def update_data(self):
        """
        Main method to check and update data.
        """
        # Ensure dates are in the correct format
        start_date = self.parameters["start_date"]
        end_date = self.parameters["end_date"]
        
        for asset in self.assets:
                # Download missing data
                new_data = self._download_data(asset, start_date, end_date)
                
                if new_data.empty:
                    print(f"No new data available for {asset} between {start_date} and {end_date}.")
                    return
                
                # Update or create ZIP file with new data
                self._update_zip_file(asset, new_data)
                print(f"Data for {asset} from {start_date} to {end_date} has been updated.")

                # new_data_factor_files = self._download_factor_file_with_close(asset, start_date, end_date)

                # if new_data_factor_files.empty:
                #     print(f"No new data available for {asset} between {start_date} and {end_date}.")
                #     return
                # self._update_zip_file_factor_file(asset, new_data_factor_files)

              
        
        