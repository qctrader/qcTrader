Feature: LeanRunner functionality
  This feature tests the various functionalities of the LeanRunner class, including environment detection, configuration file generation, and algorithm execution.

  Scenario: Detect Docker environment
    Given I am running the LeanRunner
    When I check for the Docker environment
    Then it should correctly detect if it's running inside Docker

  Scenario: Generate configuration file
    Given I have a valid algorithm configuration
    When I generate a config file
    Then the config file should be created successfully

  Scenario: Run LeanRunner with valid configuration
    Given I have a valid algorithm and config
    When I run the LeanRunner
    Then the algorithm should execute and return statistics

  Scenario: Handle missing DLL file
    Given I have an invalid LeanRunner setup
    When I run the LeanRunner
    Then it should fail due to missing DLL file

  Scenario: Handle missing config file
    Given I have an invalid config file path
    When I run the LeanRunner
    Then it should fail due to missing config file

