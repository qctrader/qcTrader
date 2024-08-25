import sys
import numpy as np

def calculate_statistics(daily_returns):
    daily_std_dev = np.std(daily_returns)
    annualized_return = (1 + sum(daily_returns)) ** (252 / len(daily_returns)) - 1
    sharpe_ratio = annualized_return / (daily_std_dev * np.sqrt(252)) if daily_std_dev != 0 else 0
    return daily_std_dev, sharpe_ratio

if __name__ == "__main__":
    # Expecting daily returns as input
    daily_returns = list(map(float, sys.argv[1:]))
    daily_std_dev, sharpe_ratio = calculate_statistics(daily_returns)
    print(daily_std_dev, sharpe_ratio)
