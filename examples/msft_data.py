import pandas as pd

# Load the saved CSV to verify its content
csv_path = "/Lean/Data/equity/usa/daily/msft.csv"
df = pd.read_csv(csv_path, header=None)

# Check for 0.0 values after saving
zero_data = df[(df == 0.0).any(axis=1)]
print("Rows with 0.0 values in the saved CSV:")
print(zero_data)