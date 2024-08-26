import json
import os
import re
import subprocess


class LeanRunner:
    def __init__(self, lean_path='qcTrader/Lean/Launcher/bin/Release'):

        # Dynamically capture the working directory
        current_working_directory = os.getcwd()

        # Store relative path for internal use
        self.internal_lean_path = lean_path

        print(f"current_working_directory----------------->{current_working_directory}")
 

        # # Store absolute path for external use if needed
        # self.lean_path = os.path.join(current_working_directory, lean_path)
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

    def set_algorithm_config(self, algorithm_name, algorithm_location, parameters):
        config = self.base_config.copy()
        config.update({
            "algorithm-type-name": algorithm_name,
            "algorithm-location": algorithm_location,
            "parameters": parameters,
        })
        return config

    def generate_config(self, algorithm_name, algorithm_location, parameters, config_path=None):
        config = self.set_algorithm_config(algorithm_name, algorithm_location, parameters)

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
 
    def run_algorithm(self, algorithm_name, algorithm_location, parameters, config_file_path=None):
        print("Starting run_algorithm...")  # Debug statement

        # Generate the configuration file if none is provided
        if config_file_path is None:
            config_file_path = self.generate_config(algorithm_name, algorithm_location, parameters)

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


   
    #    # Adjust the path if running in Docker
    #     # Dynamically capture the working directory
    #     current_working_directory = os.getcwd()

    #     # Adjust the path based on the working directory
    #     lean_path = os.path.join(current_working_directory, lean_path)