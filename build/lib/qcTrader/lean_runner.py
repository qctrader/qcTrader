import json
import os
import re
import subprocess
import sys

class LeanRunner:
    def __init__(self, lean_path='qcTrader/Lean'):
        self.lean_path = lean_path
        self.base_config = {
            "environment": "backtesting",
            "algorithm-language": "Python",
            "data-folder": os.path.join(lean_path, "Data"),
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
            "results-destination-folder": os.path.join(lean_path, "Results"),
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

        if not os.path.exists(self.lean_path):
            os.makedirs(self.lean_path)
        
        if config_path is None:
            config_path = os.path.join(self.lean_path, f'{algorithm_name}_config.json')
        
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
        if config_file_path is None:
            config_file_path = self.generate_config(algorithm_name, algorithm_location, parameters)
 
        print(f"Config file path: {config_file_path}")  # Debug statement

        # Ensure paths are cross-platform compatible
        dll_path = os.path.join(self.lean_path, 'QuantConnect.Lean.Launcher.dll')
        dll_path = os.path.normpath(dll_path)
        config_file_path = os.path.normpath(config_file_path)

        command = [
            'dotnet', 
            dll_path, 
            '--config', config_file_path
        ]
        try:
            # Run the backtest
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            messages_logs_filtered = []

            # Filter the logs in real-time
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    # Filter out specific error
                    if "System.InvalidOperationException: GIL must always be released" not in output:
                        print(output.strip())  # Print the filtered log
                        messages_logs_filtered.append(output.strip())
                    else:
                        print("Filtered out GIL error during shutdown.")  # Optionally log the filtering
            
            # Ensure to read stderr to avoid deadlocks
            for error in process.stderr:
                if "System.InvalidOperationException: GIL must always be released" not in error:
                    print(error.strip())
                else:
                    print("Filtered out GIL error during shutdown.")  # Optionally log the filtering
            
            result = "\n".join(messages_logs_filtered)
            resDict = self.extract_statistics_dict(result)
            print(f"Algorithm {algorithm_name} run completed successfully.")
            return resDict
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the algorithm {algorithm_name}: {e}")

