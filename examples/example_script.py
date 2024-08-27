from qcTrader.lean_runner import LeanRunner
from qcTrader.environment import set_python_dll_env_var



algorithm_name = 'BacktestingAlgorithm.py'
parameters = {
    "weighting_scheme": "market_cap",
    "rebalancing_frequency": "monthly",
    "market_caps": '{"AAPL": 3436202642196, "MSFT": 3144993500241, "GOOGL": 969430108231, "AMZN": 1888840584893, "TSLA": 705919572515, "JNJ": 386313864929, "PG": 400988885176}',
    "volatilities": '{"AAPL": 0.01429610035133022, "MSFT": 0.01250539724436889, "GOOGL": 0.017528420249807768, "AMZN": 0.017790672344677006, "TSLA": 0.034150240896718434, "JNJ": 0.009692984381120687, "PG": 0.00943202747844786}',
    "portfolio": '{"initial_capital": "2000000.00", "assets": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JNJ", "PG"]}'
}

set_python_dll_env_var()

lean_runner = LeanRunner()
print(lean_runner)
print(hasattr(lean_runner, 'run_algorithm'))
# Run the first algorithm
print(f"Calling run_algorithm with algorithm_name: {algorithm_name} and parameters: {parameters}")
result = lean_runner.run_algorithm(algorithm_name=algorithm_name, parameters=parameters, config_file_path=None)
print(result)

# Process the result
if result:
    print("Backtest completed with the following statistics:")
    for stat_name, stat_value in result.items():
        print(f"{stat_name}: {stat_value}")
else:
    print("Backtest failed or no statistics were returned.")


