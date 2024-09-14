## Introduction
This is a wrapper around lean engine, - > Open-Source
Algorithmic Trading Engine.

It simplifies the run of backtesting algorithms in python.

## Features
- Simple Moving Average (SMA) Crossover

## Installation

### Prerequisites
- Python 3.6+
- Dotnet SDK 6.0
- Dotnet runtime 6.0

### Installation Steps
- Install from source : pip install https://github.com/qctrader/qcTrader/releases/download/v1.0-beta.1/qcTrader-1.1.7-py3-none-any.whl
- Install from dockerfile : There is two Dockerfiles in examples directory, simply run that, create the image and run python examples/example_script.py
  pip install setuptools wheel
  python setup.py bdist_wheel
  docker build -f Dockerfile.Local -t my_custom_image .
- Install from repository : 
  git clone -b feature-fixes https://github.com/qctrader/qcTrader.git
  cd qcTrader
  pip install .
  python examples/example_script.py

### Basic usage 
check examples/example_script.py file

### Feature Explanation - Simple Moving Average (SMA) Crossover
- We use this strategy to calculate the portfolio returns based on historical data
- There is a basic configuration in the runner file and the user will give the dynamic configuration from client file.
- This altogether creates a config which is required to run the starategy against historical data and everything else is automated- check the lean_runner.py for more clarity
- If you want to add more historical data then refer the directory Lean/Launcher/bin/Release/Data/equity directory
- You can add the ticker data along with mapfiles there
- The map files should be in csv format along with anychanges to the ticker symbol in history
- You can add data to the daily, hour, minute, second folder and it is in zip format
- Currently it supports daily data history for ticker symbols
- Custom data provider support

### Contributing
`# Clone the repository
git clone https://github.com/your-username/repository-name.git

# Create a new branch for your feature or bugfix
git checkout -b feature/your-feature

# Commit your changes
git commit -am 'Add your feature'

# Push to the branch
git push origin feature/your-feature

# Create a pull request`



  


  


