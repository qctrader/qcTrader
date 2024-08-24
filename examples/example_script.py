import os
from qcTrader.lean_runner import LeanRunner
from qcTrader.environment import set_python_dll_env_var


set_python_dll_env_var()
# Initialize the LeanRunner
runner = LeanRunner()

# # Define the path components
# lean_base = 'qcTrader/Lean'
# algorithm_folder = 'Algorithm.Python'
algorithm_file = 'BacktestingAlgorithm.py'

# Join the components to form the full path
algorithm_location = os.path.join('qcTrader', 'Lean', 'Algorithm.Python', 'BacktestingAlgorithm.py')
# Normalize the path to ensure it works on both Windows and macOS/Linux
algorithm_location = os.path.normpath(algorithm_location)

print(f"Algorithm Location: {algorithm_location}")
parameters = {
    "weighting_scheme": "market_cap",
    "rebalancing_frequency": "monthly",
    "market_caps": '{"AAPL": 3436202642196, "MSFT": 3144993500241, "GOOGL": 969430108231, "AMZN": 1888840584893, "TSLA": 705919572515, "JNJ": 386313864929, "PG": 400988885176}',
    "volatilities": '{"AAPL": 0.01429610035133022, "MSFT": 0.01250539724436889, "GOOGL": 0.017528420249807768, "AMZN": 0.017790672344677006, "TSLA": 0.034150240896718434, "JNJ": 0.009692984381120687, "PG": 0.00943202747844786}',
    "portfolio": '{"initial_capital": "2000000.00", "assets": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JNJ", "PG"]}'
}
print(os.getcwd())

# Run the first algorithm

result = runner.run_algorithm(algorithm_file, algorithm_location, parameters)


# Process the result
if result:
    print("Backtest completed with the following statistics:")
    for stat_name, stat_value in result.items():
        print(f"{stat_name}: {stat_value}")
else:
    print("Backtest failed or no statistics were returned.")

# # Example configuration for a second algorithm
# algorithm_name = "AnotherAlgorithm"
# algorithm_location = "/Lean/Algorithm.Python/AnotherAlgorithm.py"
# parameters = {
#     "weighting_scheme": "market_cap_weighting",
#     "rebalancing_frequency": "quarterly",
#     "market_caps": "mid_cap",
#     "volatilities": "high_volatility",
#     "portfolio": '{"initial_capital": "200000", "assets": ["TSLA", "NFLX", "AMZN"]}'
# }

# # Run the second algorithm
# runner.run_algorithm(algorithm_name, algorithm_location, parameters)
