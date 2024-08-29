import platform
import re
import shutil
import subprocess
import os
import sys
import time
import zipfile
from datetime import datetime
import json
from dotenv import load_dotenv
import pandas as pd
if platform.system().lower() != 'windows':
    import pexpect
class DataManager:
    def __init__(self, parameters):
        load_dotenv()
        # Initialize any configuration or paths needed
        self.data_folder = os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release",  "Data")
        self.parameters = parameters
        self.lean_config_path = os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release", "lean.json")
        self.map_files_path = os.path.join(self.data_folder, self.parameters["asset_class"],self.parameters["market"],self.parameters["resolution"], "map_files" )
        self.factor_files_path = os.path.join(self.data_folder, self.parameters["asset_class"],self.parameters["market"],self.parameters["resolution"],"factor_files" )
        print(f"self.data_folder-------------->{self.data_folder}")
        
        # Convert JSON strings to Python dictionaries
        self.market_caps = json.loads(self.parameters["market_caps"])
        self.volatilities = json.loads(self.parameters["volatilities"])
        self.portfolio = json.loads(self.parameters["portfolio"])


        # Load API credentials from environment variables or parameters
        self.user_id = os.getenv("QC_USER_ID") or parameters.get('user_id')
        self.api_token = os.getenv("QC_API_TOKEN") or parameters.get('api_token')
        print(f"self.user_id---------------> {self.user_id}")
        # Dynamically determine the lean executable path
        self.lean_path = self.find_lean_executable()


    def update_lean_config(self, algorithm_file_name, algorithm_type_name):
            """Update the Lean configuration file to use the specified algorithm."""
            with open(self.lean_config_path, 'r') as f:
                config = json.load(f)


            config['job-organization-id'] =  self.parameters['job_org_id']
            config['organization-id'] =  self.parameters['org_id']
            # Update algorithm details
            config['data-folder'] =  self.data_folder
            # Update data folder path for map-file-provider and factor-file-provider
            config["environments"]["live"]["map-file-provider"]["parameters"]["data-directory"] = self.map_files_path
            config["environments"]["live"]["factor-file-provider"]["parameters"]["data-directory"] = self.factor_files_path
            config['lean-engine-settings']['algorithm-location'] = algorithm_file_name
            config['lean-engine-settings']['algorithm-type-name'] = algorithm_type_name
            
            # Save the updated configuration back to the file
            with open(self.lean_config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"Updated lean.json to use algorithm: {algorithm_file_name}")


    def update_data(self, asset_class, market, resolution,symbol):
        """Updates data for a specific asset class, market, and resolution using Lean CLI."""
        try:
            # Run the lean data download command for the specified parameters
            result = subprocess.run(
                ['lean', 'data', 'download', '--asset', asset_class, '--market', market, '--resolution', resolution, '--symbol', symbol, '--lean-config', self.lean_config_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # Use text mode for easier output handling
            )
            
            print(f"Data update for {asset_class} - {market} - {resolution} successful.")
            print(result.stdout)  # Print stdout to see any messages from Lean CLI

        except subprocess.CalledProcessError as e:
            print(f"Error updating data: {e.stderr}")  # Directly print stderr if an error occurs
            print(f"Command: {e.cmd}")  # Print the command that caused the error
            print(f"Return Code: {e.returncode}")  # Print the return code for additional context

        except FileNotFoundError as e:
            print(f"Lean CLI is not installed or not found in the system PATH: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
    
    def _read_output(self, process):
        """Read the output of the process asynchronously."""
        try:
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
        except Exception as e:
            print(f"Error reading output: {e}")

    def authenticate(self):
        """Authenticate with QuantConnect using Lean CLI."""
        if not self.user_id or not self.api_token:
            raise ValueError("User ID and API token must be set in the .env file.")

        os_type = platform.system().lower()

        # Use pexpect for macOS and Linux (including Docker)
        if os_type in ['linux', 'darwin']:  # Linux or macOS
            try:
                # Spawn the lean login process using pexpect
                process = pexpect.spawn('lean login')

                # Expect the user ID prompt and send the user ID
                process.expect("User ID:")
                process.sendline(self.user_id)

                # Expect the API token prompt and send the API token
                process.expect("API Access Token:")
                process.sendline(self.api_token)

                # Wait for the process to complete and close
                process.expect(pexpect.EOF)
                process.close()

                if process.exitstatus == 0:
                    print("Authenticated with QuantConnect successfully.")
                else:
                    print(f"Error during lean login: {process.before}")

            except pexpect.exceptions.ExceptionPexpect as e:
                print(f"Exception during lean login: {str(e)}")

        # Use subprocess for Windows
        elif os_type == 'windows':
            self.authenticate_with_subprocess()

    def find_lean_executable(self):
        """Find the path to lean.exe dynamically based on the OS and environment."""
        lean_executable = 'lean.exe'
        
        # Check if lean is available in PATH
        lean_path = shutil.which(lean_executable)
        if lean_path:
            print(f"Lean executable found in PATH: {lean_path}")
            return lean_path
        
        # Detect Python installation directory
        python_install_dir = os.path.dirname(sys.executable)
        python_scripts_dir = os.path.join(python_install_dir, 'Scripts')

        # Add Python-specific paths dynamically based on installation directory
        common_paths = {
            'Windows': [
                os.path.join(python_scripts_dir, lean_executable)  # Python Scripts directory
            ]
        }
        
        os_type = platform.system()
        for path in common_paths.get(os_type, []):
            if os.path.exists(path):
                print(f"Lean executable found in common path: {path}")
                return path
        
        # If not found, raise an exception
        raise FileNotFoundError("Lean executable not found. Please ensure 'lean' is installed and in the system PATH.") 
    


    def authenticate_with_subprocess(self):
        """Authenticate with QuantConnect using Lean CLI via subprocess."""
        if not self.user_id or not self.api_token:
            raise ValueError("User ID and API token must be set in the .env file.")
        
        try:
            print(f"Authenticating using Lean executable at: {self.lean_path}")

            # Check if the executable path exists
            if not os.path.exists(self.lean_path):
                raise FileNotFoundError(f"Lean executable not found at {self.lean_path}.")
            
            # Run the lean login process

            command = [
                self.lean_path, 
                'login',
                f'--user-id={self.user_id}',
                f'--api-token={self.api_token}'
            ]
            try:
                print("Starting subprocess with Popen...")
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,  # Use text mode for easier input handling
                    encoding='utf-8',
                    errors='replace'
                )
                print("Subprocess started successfully.")
            except Exception as e:
                print(f"Error starting subprocess: {e}")
                return
            
            # Wait for the process to complete
            stdout, stderr = process.communicate()

            # Print the output and error (if any)
            print(f"Lean login output:\n{stdout}")
            if stderr:
                print(f"Lean login errors:\n{stderr}")

            if process.returncode == 0:
                print("Authenticated with QuantConnect successfully.")
            else:
                print(f"Error during lean login: Return code {process.returncode}")
                
        except subprocess.CalledProcessError as e:
            print(f"Error during lean login: {e.stderr}")
        except Exception as e:
            print(f"General exception during lean login: {str(e)}")


    def check_zip_file_exists(self, asset_class, market, resolution, symbol):
        # Construct the path to the .zip file
        # f'{symbol.lower()}.zip'
        file_path = os.path.join(self.data_folder, asset_class, market, resolution, f'{symbol.lower()}.zip')

        # Debugging: Print each path component
        print(f"Data Folder: {self.data_folder}")
        print(f"Asset Class: {asset_class}")
        print(f"Market: {market}")
        print(f"Resolution: {resolution}")
        print(f"Symbol Lowercased: {symbol.lower()}")
        print(f"Constructed File Path: {file_path}")

        # Print the absolute path for clarity
        absolute_path = os.path.abspath(file_path)
        print(f"Absolute file path: {absolute_path}")

                # Extra debugging: Check if the directory exists
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

    def check_data_availability(self, asset_class, market, symbol, start_date, end_date, resolution):
        """Check if data for a specific asset is available in the Data folder for the given date range."""
        absolute_path = self.check_zip_file_exists(asset_class, market, resolution, symbol)
        
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

    def update_and_verify_data(self, algorithm_file_name, algorithm_type_name):
        """Run update and verification for all specified assets if needed."""
        # Authenticate once before downloading data
        self.authenticate()
        self.update_lean_config(algorithm_file_name, algorithm_type_name)
        

        # Read assets and other parameters from the provided dictionary
        assets = self.portfolio["assets"]

        # Read asset_class, market, and resolution from parameters
        asset_class = self.parameters['asset_class']
        market = self.parameters['market']
        resolution = self.parameters['resolution']
        
        # Loop through each asset and update data if necessary
        for asset in assets:
            data_available = self.check_data_availability(asset_class, market, asset, self.parameters["start_date"], self.parameters["end_date"], resolution)
            
            if not data_available:
                # Update data if not available
                self.update_data(asset_class, market, resolution,asset)
