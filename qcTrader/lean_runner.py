import json
import os
import platform
import re
import site
import subprocess
from qcTrader.data_aggregrator import QuantConnectDataUpdater


class LeanRunner:
    def __init__(self, lean_path='qcTrader/Lean/Launcher/bin/Release'):

        # Dynamically capture the working directory
        current_working_directory = os.getcwd()
        self.is_docker = self.detect_is_docker()
      
        if self.is_docker:
                # If running inside Docker, use the site-packages path
                site_packages_path = site.getsitepackages()[0]
                print(f"site_packages_path----------------->{site_packages_path}")
                self.internal_lean_path = os.path.join(site_packages_path, lean_path)
        else:
                # Otherwise, use the default path for non-Docker installations
                self.internal_lean_path = lean_path

        print(f"current_working_directory----------------->{current_working_directory}")
 
        self.base_config = {
            "environment": "backtesting",
            "algorithm-language": "Python",
            "data-folder": os.path.join(self.internal_lean_path, "Data"),
            "debugging": False,
            "debugging-method": "LocalCmdLine",
            "log-handler": "ConsoleLogHandler",
            "messaging-handler": "QuantConnect.Messaging.Messaging",
            "job-queue-handler": "QuantConnect.Queues.JobQueue",
            "api-handler": "QuantConnect.Api.Api",
            "map-file-provider": "QuantConnect.Data.Auxiliary.LocalDiskMapFileProvider",
            "factor-file-provider": "QuantConnect.Data.Auxiliary.LocalDiskFactorFileProvider",
            "data-provider": "QuantConnect.Lean.Engine.DataFeeds.DefaultDataProvider",
            "object-store": "QuantConnect.Lean.Engine.Storage.LocalObjectStore",
            "data-aggregator": "QuantConnect.Lean.Engine.DataFeeds.AggregationManager",
            "symbol-minute-limit": 10000,
            "symbol-second-limit": 10000,
            "symbol-tick-limit": 10000,
            "show-missing-data-logs": True,
            "maximum-warmup-history-days-look-back": 5,
            "maximum-data-points-per-chart-series": 1000000,
            "maximum-chart-series": 30,
            "force-exchange-always-open": False,
            "transaction-log": "",
            "reserved-words-prefix": "@",
            "job-user-id": "0",
            "api-access-token": "",
            "job-organization-id": "",
            "log-level": "trace",
            "debug-mode": True,
            "results-destination-folder": os.path.join(self.internal_lean_path, "Results"),
            "mute-python-library-logging": "False",
            "close-automatically": True,
            "python-additional-paths": [],
            "environments": {
                "backtesting": {
                    "live-mode": False,
                    "setup-handler": "QuantConnect.Lean.Engine.Setup.BacktestingSetupHandler",
                    "result-handler": "QuantConnect.Lean.Engine.Results.BacktestingResultHandler",
                    "data-feed-handler": "QuantConnect.Lean.Engine.DataFeeds.FileSystemDataFeed",
                    "real-time-handler": "QuantConnect.Lean.Engine.RealTime.BacktestingRealTimeHandler",
                    "history-provider": [
                        "QuantConnect.Lean.Engine.HistoricalData.SubscriptionDataReaderHistoryProvider"
                    ],
                    "transaction-handler": "QuantConnect.Lean.Engine.TransactionHandlers.BacktestingTransactionHandler",
                }
            },
        }
    def detect_is_docker(self):
        """Check if the code is running inside a Docker container or WSL environment."""

        # Get the platform type (Windows, Linux, Darwin (macOS))
        os_type = platform.system().lower()
        print(f"os_type --------------------> {os_type }")

        # Check if the OS is Windows; if so, immediately return False
        if os_type == 'windows':
            return False

        # Check if the OS is macOS; if so, immediately return False
        if os_type == 'darwin':
            return False

        # If it's a plain Linux environment, check if it's WSL first
        if os_type == 'linux':
            # Detect if running under WSL (Windows Subsystem for Linux)
            if 'microsoft' in platform.uname().release.lower():
                print("Running in WSL, not Docker.")
                return False  # It's WSL, not Docker

            # Now check for Docker-specific files
            docker_env_path = '/.dockerenv'
            cgroup_path = '/proc/self/cgroup'
            
            # Check for the existence of .dockerenv file
            if os.path.exists(docker_env_path):
                return True
            
            # Check for 'docker' in /proc/self/cgroup
            if os.path.isfile(cgroup_path):
                with open(cgroup_path) as f:
                    if any('docker' in line for line in f):
                        return True

        # If none of the above conditions are met, return False
        return False
            
    def set_algorithm_config(self, algorithm_location, algorithm_name, parameters):
      
        config = self.base_config.copy()
        config.update({
            "algorithm-type-name": algorithm_name,
            "algorithm-location": algorithm_location,
            "parameters": parameters,
        })
        return config

    def generate_config(self,algorithm_location,  algorithm_name, parameters, config_path=None):
        config = self.set_algorithm_config(algorithm_location, algorithm_name, parameters)

        if not os.path.exists(self.internal_lean_path):
            os.makedirs(self.internal_lean_path)
        
        if config_path is None:
            config_path = os.path.join(self.internal_lean_path, f'{algorithm_name}_config.json')
        
        try:
            print(f"Attempting to create config file at: {config_path}")
            with open(config_path, 'w') as config_file:
                json.dump(config, config_file, indent=4)
            print(f"Config file generated for {algorithm_name} at: {config_path}")
        except Exception as e:
            print(f"An error occurred while generating the config file: {e}")
        
        return os.path.abspath(config_path)

    def extract_statistics_dict(self, data_list):
        statistics = {}
        if data_list:
            log_lines = data_list.split('\n')
            for line in log_lines:
                print(f"log_lines------------------------>{line}")
                if line.startswith("STATISTICS::"):
                    match = re.search(r'STATISTICS::\s*(.*)', line)
                    if match:
                        stat_line = match.group(1).strip()
                        if ' ' in stat_line:
                            stat_name, stat_value = stat_line.rsplit(' ', 1)
                            stat_name = stat_name.strip()
                            stat_value = stat_value.strip()
                            statistics[stat_name] = stat_value

        return statistics
 
    def run_algorithm(self, algorithm_name, algorithm_type_name, parameters, config_file_path=None):
        # Initialize the DataManager
        data_manager = QuantConnectDataUpdater(parameters)


        data_manager.update_data()
                # Create a datetime.date object
        date_obj_start_date = parameters["start_date"]
        date_obj_end_date = parameters["end_date"]
        # Convert to string in "YYYY-MM-DD" format
        date_str_start = date_obj_start_date.strftime("%Y-%m-%d")
        date_str_end = date_obj_end_date.strftime("%Y-%m-%d")
        parameters["start_date"] = date_str_start
        parameters["end_date"] = date_str_end
        print(f"Inside run_algorithm with algorithm_name: {algorithm_name} and parameters: {parameters}")
        print("Starting run_algorithm...")  # Debug statement
       
        print(f"Algorithm Name: {algorithm_name}")
        print(f"Parameters: {parameters}")
        print(f"Config File Path: {config_file_path}")
    
        algorithm_location= f""

        if self.is_docker:
                # If running inside Docker, use the site-packages path
                site_packages_path = site.getsitepackages()[0]
                print(f"site_packages_path----------------->{site_packages_path}")
                algorithm_location = os.path.join(site_packages_path, 'qcTrader/Lean/Algorithm.Python' , algorithm_name)
        else:
                algorithm_location = os.path.join('qcTrader', 'Lean', 'Algorithm.Python', algorithm_name)
                # Normalize the path to ensure it works on both Windows and macOS/Linux
                algorithm_location = os.path.normpath(algorithm_location)



        

        # Generate the configuration file if none is provided
        if config_file_path is None:
            config_file_path = self.generate_config(algorithm_location, algorithm_name, parameters)

        print(f"Config file path: {config_file_path}")  # Debug statement

        # Ensure paths are cross-platform compatible
        dll_path = os.path.join(self.internal_lean_path, 'QuantConnect.Lean.Launcher.dll')
        dll_path = os.path.normpath(dll_path)
        config_file_path = os.path.normpath(config_file_path)

        # Verify DLL and config file existence
        if not os.path.exists(dll_path):
            print(f"Error: DLL not found at {dll_path}")
            return None
        if not os.path.exists(config_file_path):
            print(f"Error: Config file not found at {config_file_path}")
            return None

        print(f"DLL found: {dll_path}")
        print(f"Config file found: {config_file_path}")

        # Construct the command to run the backtest
        command = [
            'dotnet', 
            dll_path, 
            '--config', config_file_path
        ]
        try:
            print(f"Running command: {command}")

            # Run the backtest using subprocess with communicate()
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # Ensure the encoding is set
                errors='replace'   # Handle encoding errors gracefully
            )
            
            stdout, stderr = process.communicate()

            # Process stdout
            messages_logs_filtered = []
            for line in stdout.splitlines():
                if "System.InvalidOperationException: GIL must always be released" not in line:
                    print(line.strip())
                    messages_logs_filtered.append(line.strip())
                else:
                    print("Filtered out GIL error during shutdown.")

            # Process stderr
            if stderr:
                for error in stderr.splitlines():
                    if "System.InvalidOperationException: GIL must always be released" not in error:
                        print(error.strip())
                    else:
                        print("Filtered out GIL error during shutdown.")

            # Combine the filtered logs and extract statistics
            result = "\n".join(messages_logs_filtered)
            resDict = self.extract_statistics_dict(result)
            print(f"Algorithm {algorithm_name} run completed successfully.")
            return resDict

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the algorithm {algorithm_name}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


   
