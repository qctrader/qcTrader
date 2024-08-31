from datetime import datetime
import os
from qcTrader.lean_runner import LeanRunner
from qcTrader.environment import set_python_dll_env_var
from dotenv import load_dotenv 

load_dotenv()
algorithm_name = 'BacktestingAlgorithm.py'
algorithm_type_name = 'BacktestingAlgorithm'

data_config_paramters= {
    "asset_class": "equity",  
    "market": "usa",          
    "resolution": "daily" ,    
    "user_id":os.getenv("USERID"),
    "api_token":os.getenv("TOKEN"),
    "job_org_id":os.getenv("ORGID"),
    "org_id":os.getenv("ORGID")
}

parameters = {
        "start_date": datetime(2020, 1, 1).date(),
        "end_date" : datetime(2024, 8, 30).date(),
        "weighting_scheme": "market_cap",
        "rebalancing_frequency": "monthly",
        "market_caps": '{"AAPL": 3436202642196, "GOOGL": 969430108231, "IBM": 131850000000, "MSFT": 3144993500241}',
        "volatilities": '{"AAPL": 0.0143, "GOOGL": 0.0175, "IBM": 0.0120, "MSFT": 0.0125}',
        "portfolio": '{"initial_capital": "2000000.00", "assets": ["AAPL", "GOOGL", "IBM", "MSFT"]}'
}

set_python_dll_env_var()

lean_runner = LeanRunner()
print(lean_runner)
print(hasattr(lean_runner, 'run_algorithm'))
# Run the first algorithm
print(f"Calling run_algorithm with algorithm_name: {algorithm_name} and parameters: {parameters}")
result = lean_runner.run_algorithm(
    algorithm_name=algorithm_name, 
    algorithm_type_name=algorithm_type_name, 
    parameters=parameters,
    data_config_paramters=data_config_paramters,
    config_file_path=None)
print(result)

# Process the result
if result:
    print("Backtest completed with the following statistics:")
    for stat_name, stat_value in result.items():
        print(f"{stat_name}: {stat_value}")
else:
    print("Backtest failed or no statistics were returned.")


