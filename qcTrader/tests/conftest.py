import pytest
import os
import pytest
from qcTrader.lean_runner import LeanRunner

@pytest.fixture
def setup_lean_runner():
    return LeanRunner()
@pytest.fixture
def test_context():
    return {}

@pytest.fixture
def configure_algorithm():
    algorithm_name = "BacktestingAlgorithm.py"
    parameters = {
        "weighting_scheme": "market_cap",
        "rebalancing_frequency": "monthly",
        "market_caps": '{"AAPL": 3436202642196, "MSFT": 3144993500241, "GOOGL": 969430108231, "AMZN": 1888840584893, "TSLA": 705919572515, "JNJ": 386313864929, "PG": 400988885176}',
        "volatilities": '{"AAPL": 0.01429610035133022, "MSFT": 0.01250539724436889, "GOOGL": 0.017528420249807768, "AMZN": 0.017790672344677006, "TSLA": 0.034150240896718434, "JNJ": 0.009692984381120687, "PG": 0.00943202747844786}',
        "portfolio": '{"initial_capital": "2000000.00", "assets": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JNJ", "PG"]}'
    }
    return algorithm_name, parameters

@pytest.fixture
def valid_algorithm_and_config(configure_algorithm):
    setup_lean_runner = LeanRunner()
    algorithm_name, parameters = configure_algorithm
    config_path = setup_lean_runner.generate_config(algorithm_name, parameters)
    return setup_lean_runner, algorithm_name, parameters, config_path    


@pytest.fixture
def invalid_leanrunner_setup():
    setup_lean_runner = LeanRunner(lean_path='invalid/path/to/Lean')
    return setup_lean_runner

@pytest.fixture
def invalid_config_file_path(valid_algorithm_and_config):
    setup_lean_runner, algorithm_name, parameters, _ = valid_algorithm_and_config
    return setup_lean_runner, algorithm_name, parameters, 'invalid/config/path'


@pytest.fixture(scope='module', autouse=True)
def cleanup_environment():
    yield
    # Reset environment variables after tests are done
    os.environ.pop('DOTNET_ROOT', None)
    os.environ.pop('PATH', None)