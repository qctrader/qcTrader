import os
import site
import time
from pytest_bdd import scenarios, given, when, then
from pathlib import Path

feature_file = Path.cwd() / "tests" / "features" / "lean_runner.feature"
print(feature_file)
scenarios(str(feature_file.resolve()))

@given('I am running the LeanRunner')
def i_am_running_the_lean_runner(setup_lean_runner):
    pass    

@when('I check for the Docker environment')
def check_docker_environment(setup_lean_runner):
    setup_lean_runner.is_docker = setup_lean_runner.detect_docker_environment()

@then('it should correctly detect if it\'s running inside Docker')
def verify_docker_detection(setup_lean_runner):
    assert not setup_lean_runner.is_docker

@given('I have a valid algorithm configuration')
def i_have_valid_alogorithm_configuration(configure_algorithm):
    pass     

@when('I generate a config file')
def generate_config_file(setup_lean_runner, configure_algorithm,test_context):

        
    if os.getenv('DOCKER_ENV'):  # Check if running inside Docker
        site_packages_path = site.getsitepackages()[0]
        algorithm_location = os.path.join(site_packages_path, 'qcTrader/Lean/Algorithm.Python')
    else:
        algorithm_location = "qcTrader/Lean/Algorithm.Python"
    algorithm_name, parameters = configure_algorithm
    config_path = setup_lean_runner.generate_config(algorithm_name, parameters)
    test_context['config_file_path'] = config_path

@then('the config file should be created successfully')
def verify_config_file_creation(test_context):
    config_file_path = test_context.get('config_file_path')
    assert config_file_path is not None, "Config file path is not set"
    assert os.path.exists(config_file_path), f"Config file does not exist at: {config_file_path}"

@given('I have a valid algorithm and config')
def i_have_valid_alogorithm_and_config(valid_algorithm_and_config):
    pass  

@when('I run the LeanRunner')
def run_lean_runner(test_context, valid_algorithm_and_config):
    setup_lean_runner, algorithm_name, parameters, config_path = valid_algorithm_and_config
    test_context['result'] = setup_lean_runner.run_algorithm(algorithm_name, parameters, config_file_path=config_path)

#check this
@then('the algorithm should execute and return statistics')
def verify_algorithm_execution(test_context):
    result = test_context.get('result')

    if result is None:
        # Assert the result is None
        assert result is None, "LeanRunner did not return any result."
    else:
        assert result is not None
        # Assert the result is a dictionary
        assert isinstance(result, dict), f"Expected a dictionary, but got {type(result)}."
        
        # Assert the dictionary is not empty
        assert len(result) > 0, "The result dictionary is empty."

        




@given('I have an invalid LeanRunner setup')
def invalid_runner_setup():
    pass
@then('it should fail due to missing DLL file')
def verify_missing_dll_error(invalid_leanrunner_setup):
    result = invalid_leanrunner_setup.run_algorithm("BacktestingAlgorithm.py", {})
    assert result is None

@given('I have an invalid config file path')
def invalid_config_path():
    pass



@then('it should fail due to missing config file')
def verify_missing_config_error(invalid_config_file_path):
    setup_lean_runner, algorithm_name, parameters, config_file_path = invalid_config_file_path
    result = setup_lean_runner.run_algorithm(algorithm_name, parameters, config_file_path=config_file_path)
    assert result is None
