import json
import yfinance as yf
import os
import pandas as pd
import zipfile
import csv
import pandas as pd
from io import BytesIO, TextIOWrapper
from datetime import timedelta
import yfinance as yf
from zipfile import ZipFile
from datetime import datetime, timedelta
from pytz import timezone, utc
import tempfile
import shutil
from filelock import FileLock

class AddOnFileManager:
    def __init__(self, symbols, start_date, end_date, corporate_actions_path, factor_file_path, map_file_path):
        """
        Initializes the FileManager with the given symbols and date range.
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.corporate_actions_path = corporate_actions_path
        self.factor_file_path = factor_file_path
        self.map_file_path = map_file_path


    def download_corporate_actions(self, symbol):
        """
        Downloads splits, dividends, and previous close prices for the given symbol and date range using yfinance.
        """
        ticker = yf.Ticker(symbol)

        # Download splits and dividends with date range filtering
        splits = ticker.splits.loc[self.start_date:self.end_date]
        dividends = ticker.dividends.loc[self.start_date:self.end_date]

        # Download historical data to get adjusted close prices for previous close
        historical_data = ticker.history(start=self.start_date, end=self.end_date)

        # Ensure 'Date' is a column for merging purposes
        historical_data = historical_data.reset_index()
        historical_data['Date'] = historical_data['Date'].dt.strftime('%Y%m%d')

        # Format splits data
        if not splits.empty:
            splits_df = splits.reset_index()
            splits_df['EventType'] = 'Split'
            splits_df['Date'] = splits_df['Date'].dt.strftime('%Y%m%d')
            splits_df = splits_df.rename(columns={splits.name: 'Value'})
            splits_df = splits_df[['EventType', 'Date', 'Value']]
        else:
            splits_df = pd.DataFrame(columns=['EventType', 'Date', 'Value'])

        # Format dividends data
        if not dividends.empty:
            dividends_df = dividends.reset_index()
            dividends_df['EventType'] = 'Dividend'
            dividends_df['Date'] = dividends_df['Date'].dt.strftime('%Y%m%d')
            dividends_df = dividends_df.rename(columns={dividends.name: 'Value'})
            dividends_df = dividends_df[['EventType', 'Date', 'Value']]
        else:
            dividends_df = pd.DataFrame(columns=['EventType', 'Date', 'Value'])

        # Combine splits and dividends
        corporate_actions = pd.concat([splits_df, dividends_df]).sort_values(by='Date')

        # Merge with historical data to get the 'PreviousClose' price
        if not corporate_actions.empty and not historical_data.empty:
            # Add the previous close price for each action based on the date
            corporate_actions = pd.merge(
                corporate_actions, 
                historical_data[['Date', 'Close']], 
                on='Date', 
                how='left'
            )
            corporate_actions = corporate_actions.rename(columns={'Close': 'PreviousClose'})
        else:
            corporate_actions['PreviousClose'] = 0  # If no data, set as None

        return corporate_actions


    def save_corporate_actions_to_lean_format(self, data, symbol):
        """
        Saves corporate actions data to Lean's expected format and location.
        """
        directory = self.corporate_actions_path
        filename = f"{symbol.lower()}.zip"
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)

        # Save data to a CSV within a ZIP file
        csv_filename = f"{symbol.lower()}.csv"
        data.to_csv(csv_filename, index=False)

        with ZipFile(file_path, 'w') as zipf:
            zipf.write(csv_filename, arcname=csv_filename)

        os.remove(csv_filename)

        print(f"Saved corporate actions for {symbol} to {file_path}")

    def save_factor_file(self, symbol, corporate_actions):
        """
        Generates and saves a factor file for Lean using splits and dividends data.
        The factor file will have four columns: Date, Split Factor, Price Factor, and Reference Price.
        """
        directory = self.factor_file_path
        filename = f"{symbol.lower()}.csv"
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)

        if not corporate_actions.empty:
            corporate_actions['Date'] = pd.to_datetime(corporate_actions['Date'])
            factors = []
            cumulative_split_factor = 1.0
            cumulative_price_factor = 1.0

            for _, row in corporate_actions.iterrows():
                date = row['Date'].strftime('%Y%m%d')  # Format the date as YYYYMMDD
                if row['EventType'] == 'Split':
                    # Calculate split adjustment factor
                    split_factor = 1 / row['Value']  # Assuming 'Value' holds the split ratio
                    cumulative_split_factor *= split_factor
                    factors.append([date, cumulative_split_factor, cumulative_price_factor, 1])  # Placeholder for reference price
                elif row['EventType'] == 'Dividend':
                    # Placeholder for dividend handling logic
                    # Adjust the price factor to account for dividends if applicable
                    price_adjustment = 1 - (row['Value'] / row['PreviousClose'])  # Adjust based on dividend value
                    cumulative_price_factor *= price_adjustment
                    factors.append([date, cumulative_split_factor, cumulative_price_factor, row['Value']])  # Reference price as dividend value

            # Ensure factors are sorted by date to maintain chronological order
            factors.sort(key=lambda x: x[0])

            if factors:
                # Convert the list to a DataFrame with the appropriate columns
                factors_df = pd.DataFrame(factors, columns=['Date', 'Split Factor', 'Price Factor', 'Reference Price'])
                factors_df.to_csv(file_path, index=False, header=False)
                print(f"Saved factor file for {symbol} to {file_path}")
            else:
                # Creating a default factor file if no valid corporate actions are found
                print(f"No valid split or dividend data for {symbol}. Creating default factor file.")
                pd.DataFrame([["20200101", 1, 1, 1]]).to_csv(file_path, index=False, header=False)
        else:
            # Creating a default factor file when corporate actions data is empty
            print(f"No corporate actions data to create factor file for {symbol}. Creating default factor file.")
            pd.DataFrame([["20200101", 1, 1, 1]]).to_csv(file_path, index=False, header=False)

    def save_map_file(self, symbol):
        """
        Generates and saves a map file for Lean. Assumes no ticker changes for simplicity.
        """
        directory = self.map_file_path
        filename = f"{symbol.lower()}.csv"
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)

        stock = yf.Ticker(symbol)
        data = stock.history(period="max")

        with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Assuming no ticker changes for simplicity
                for index, row in data.iterrows():
                    date = index.strftime('%Y%m%d')
                    writer.writerow([date, symbol, symbol])
        print(f"Saved map file for {symbol} to {file_path}")

    def create_files_for_all_symbols(self):
        """
        Creates corporate actions, factor files, and map files for all symbols in the array.
        """
        for symbol in self.symbols:
            print(f"Processing {symbol}...")

            # Download and validate corporate actions data
            corporate_actions = self.download_corporate_actions(symbol)
            if not corporate_actions.empty:
                print(f"Downloaded corporate actions for {symbol}:\n", corporate_actions.head())
                self.save_corporate_actions_to_lean_format(corporate_actions, symbol)
                self.save_factor_file(symbol, corporate_actions)
            else:
                print(f"No corporate actions data available for {symbol} from {self.start_date} to {self.end_date}.")
                self.save_factor_file(symbol, corporate_actions)  # Create a default factor file

            # Save map file
            self.save_map_file(symbol)



class QuantConnectDataUpdater:
    def __init__(self, data_config_paramters, parameters):
        self.parameters = parameters
        self.data_config_paramters = data_config_paramters
        self.base_path_data = self.data_folder = os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release",  "Data",self.data_config_paramters["asset_class"],self.data_config_paramters["market"])
        self.data_folder = os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release",  "Data",self.data_config_paramters["asset_class"],self.data_config_paramters["market"],self.data_config_paramters["resolution"])
        self.map_files_path = os.path.join(self.base_path_data, "map_files" )
        self.factor_files_path = os.path.join(self.base_path_data,"factor_files" )
        self.corporate_actions_path = os.path.join(self.base_path_data,"corporate_actions" )
        self.interest_rate_file_path = os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release",  "Data" , "alternative", "interest-rate", self.data_config_paramters["market"], "interest-rate.csv")
        # Parse the JSON string
        portfolio_dict = json.loads(self.parameters['portfolio'])

        # Extract the assets
        self.assets = portfolio_dict.get("assets", [])




    def update_interest_rate_data(self,file_path):
        """
        Updates the interest rate data using yFinance by removing the existing file and fetching the latest data.
        """
        # Define the ticker for U.S. 10-Year Treasury Yield
        ticker = "^TNX"  # CBOE 10-Year Treasury Note Yield Index

        # Remove the existing interest rate CSV file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed existing interest rate data file: {file_path}")

        # Fetch the latest interest rate data from Yahoo Finance
        start_date = '2000-01-01'  
        new_data = yf.download(ticker, start=start_date, end=pd.Timestamp.today().strftime('%Y-%m-%d'))

        if not new_data.empty:
            # Extract the relevant data (closing price as the interest rate value)
            new_data = new_data.reset_index()[['Date', 'Close']]
            new_data.rename(columns={'Close': 'Value'}, inplace=True)

            # Save the new data to the CSV file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the directory exists
            new_data.to_csv(file_path, index=False)

            print(f"Interest rate data updated successfully and saved to {file_path}.")
        else:
            print("No new interest rate data available to update.")


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
    

    def get_exchange_timezone(self,symbol, exchange_timezones):
        """
        Dynamically fetches the exchange and time zone information for a symbol using yfinance.
        If the exchange is not found in the mapping, it attempts to add it dynamically.
        """
        try:
            # Fetch ticker information using yfinance
            ticker = yf.Ticker(symbol)
            
            # Extract the time zone directly from ticker info if available
            tz_name = ticker.info.get('timezone')
            if tz_name:
                print(f"Retrieved time zone for {symbol}: {tz_name}")
                return timezone(tz_name)

            # Extract the exchange name
            exchange = ticker.info.get('exchange', '').upper()

            # Check if the exchange is already in the mapping
            if exchange not in exchange_timezones:
                # If the exchange is not in the mapping, try to dynamically add it
                new_time_zone = self.fetch_timezone_from_external_source(exchange)
                if new_time_zone:
                    exchange_timezones[exchange] = new_time_zone
                    print(f"Added new exchange: {exchange} with time zone: {new_time_zone}")
                else:
                    print(f"Time zone for {exchange} not found, defaulting to UTC.")
                    exchange_timezones[exchange] = 'UTC'

            # Retrieve the time zone for the given exchange
            time_zone = exchange_timezones.get(exchange, 'UTC')
            print(f"Using exchange-based time zone for {symbol}: {time_zone}")
            return timezone(time_zone)

        except Exception as e:
            print(f"Error fetching exchange data for {symbol}: {str(e)}")
            return utc  # Default to UTC in case of an error
            
    def fetch_timezone_from_external_source(self,exchange):
        """
        Fetches time zone information for an exchange dynamically using yfinance.
        This function looks for a symbol commonly traded on the given exchange to infer its time zone.
        """
        # Example symbols commonly associated with specific exchanges
        common_symbols = {
            'TSE': '7203.T',   # Tokyo Stock Exchange
            'HKG': '0001.HK',  # Hong Kong Stock Exchange
            'NMS': 'AAPL',     # NASDAQ
            'NYQ': 'MSFT',     # NYSE
            'LSE': 'AZN.L',    # London Stock Exchange
            'ASX': 'BHP.AX',   # Australian Securities Exchange
            # Additional symbols for Apple, Microsoft, and Google
            'NASDAQ': 'AAPL',  # NASDAQ - Apple
            'NYSE': 'MSFT',    # NYSE - Microsoft
            'GOOGL': 'GOOGL',  # NASDAQ - Google
            'NMS': 'GOOGL',    # NASDAQ - Google
        }
        
        # Attempt to find a symbol associated with the exchange
        example_symbol = common_symbols.get(exchange)
        
        if example_symbol:
            try:
                # Use yfinance to fetch ticker info for the example symbol
                ticker = yf.Ticker(example_symbol)
                tz_name = ticker.info.get('timezone')
                if tz_name:
                    print(f"Fetched time zone {tz_name} for exchange {exchange} using symbol {example_symbol}")
                    return tz_name
            except Exception as e:
                print(f"Error fetching time zone for exchange {exchange} using {example_symbol}: {str(e)}")
        
        print(f"No specific time zone found for exchange {exchange}, defaulting to UTC.")
        return 'UTC'  # Fallback to UTC if the exchange's time zone cannot be determined   
    

    def _download_data(self, symbol, start_date, end_date, exchange_timezones):
        """
        Downloads data for the given symbol and date range using yfinance.
        """
        data = yf.download(symbol, start=start_date - timedelta(days=10), end=end_date + timedelta(days=10), interval='1d', auto_adjust=False)
        
        if not data.empty:
            # Select only the required columns and rename them to match the format expected by Lean
            formatted_data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            formatted_data.columns = ['open', 'high', 'low', 'close', 'volume']

            # Get the local time zone for the exchange
            local_time_zone = self.get_exchange_timezone(symbol, exchange_timezones)

            # Localize the index to the local time zone of the exchange
            formatted_data.index = pd.to_datetime(formatted_data.index).tz_localize(local_time_zone)

            # Convert the localized time to UTC
            formatted_data.index = formatted_data.index.tz_convert('UTC')

            # Format the datetime index as 'YYYYMMDD HH:MM' in UTC
            formatted_data.index = formatted_data.index.strftime('%Y%m%d %H:%M')

            # Check and ensure there are no duplicate indices (dates)
            formatted_data = formatted_data[~formatted_data.index.duplicated(keep='first')]

            # Reorder the columns if necessary
            formatted_data = formatted_data[['close', 'high', 'low', 'open', 'volume']]
        else:
            # Return an empty DataFrame with the correct structure if no data was downloaded
            formatted_data = pd.DataFrame(columns=['close', 'high', 'low', 'open', 'volume'])
            
        return formatted_data

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
        temp_zip_file_path = tempfile.mktemp(suffix='.zip')
        lock_path = f"{zip_file_path}.lock"
        lock = FileLock(lock_path)
        try:
            with lock:
                # Open the ZIP file in write mode to replace any existing files
                with zipfile.ZipFile(temp_zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
                    # Write the new data to the ZIP file, replacing any existing CSV file
                    with zip_file.open(csv_file_name, 'w') as csv_file:
                        with TextIOWrapper(csv_file, encoding='utf-8') as text_file:
                            # Write DataFrame directly to the text file
                            new_data.to_csv(text_file, header=False)
                        # Use a buffer to write the DataFrame into the ZIP
                        #buffer = BytesIO()
                        # Write only the new data with the formatted dates, excluding headers
                        #new_data.to_csv(buffer, header=False, encoding='utf-8')
                        #buffer.flush()  # Ensure all data is written to the buffer
                        #buffer.seek(0)
                        #csv_file.write(buffer.read())

                print(f"Successfully replaced the data in the ZIP file for {symbol}.")

                # Validate the ZIP file signature
                with open(temp_zip_file_path, 'rb') as file:
                    signature = file.read(4)
                    if signature == b'PK\x03\x04':
                       print(f"Valid ZIP file created for {symbol}.")
                    else:
                       raise ValueError(f"Invalid ZIP file signature for {symbol}: {signature}")

                shutil.move(temp_zip_file_path, zip_file_path)
                print(f"ZIP file {zip_file_path} updated successfully.")

        except Exception as e:
            # Handle any errors and ensure no partial files are left
            print(f"Error updating ZIP file: {e}")
            if os.path.exists(temp_zip_file_path):
                os.remove(temp_zip_file_path)




    def update_data(self):
        """
        Main method to check and update data.
        """
        # Ensure dates are in the correct format
        start_date = self.parameters["start_date"]
        end_date = self.parameters["end_date"]
        for asset in self.assets:
                # Download missing data

                exchange_timezones = {
                    'NMS': 'America/New_York',  # NASDAQ
                    'NYQ': 'America/New_York',  # NYSE
                }
                new_data = self._download_data(asset, start_date, end_date, exchange_timezones)
              
                
                if new_data.empty:
                    print(f"No new data available for {asset} between {start_date} and {end_date}.")
                    return
                
                # Update or create ZIP file with new data
                self._update_zip_file(asset, new_data)
                print(f"Data for {asset} from {start_date} to {end_date} has been updated.")

         # # Create a date object
        start_date_obj = start_date

        # # Convert the date object to a string in the format 'YYYY-MM-DD'
        start_date_str = start_date_obj.strftime('%Y-%m-%d')


        #         # Create a date object
        end_date_obj = end_date

        # # Convert the date object to a string in the format 'YYYY-MM-DD'
        end_date_str = end_date_obj.strftime('%Y-%m-%d')

        
        file_manager = AddOnFileManager(self.assets, start_date_str, end_date_str, self.corporate_actions_path, self.factor_files_path, self.map_files_path)
        file_manager.create_files_for_all_symbols()
        self.update_interest_rate_data(self.interest_rate_file_path)




                
              
        
        