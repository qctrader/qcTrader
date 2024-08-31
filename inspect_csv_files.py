import pandas as pd
from zipfile import ZipFile

def inspect_csv_from_zip(zip_path, csv_name):
    """
    Extracts and inspects a CSV file from a ZIP archive.
    """
    with ZipFile(zip_path, 'r') as zipf:
        with zipf.open(csv_name) as file:
            # Read the CSV without headers and assign expected column names
            df = pd.read_csv(file, header=None)
            
            # Expected columns: ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            print(f"Inspecting {csv_name} from {zip_path}:")
            print(df.head())
            print("Columns:", df.columns.tolist())
            print("Date Format Check:", df['date'].head())

# Inspect known good AlgoSeek data
inspect_csv_from_zip('qcTrader/Lean/Launcher/bin/Release/Data/equity/usa/daily/aapl.zip', 'aapl.csv')

# Inspect your manually downloaded data
inspect_csv_from_zip('qcTrader/Lean/Launcher/bin/Release/Data/equity/usa/daily/msft.zip', 'msft.csv')
