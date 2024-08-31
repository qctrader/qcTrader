import os
import zipfile
import pandas as pd

# Set the directory path for the daily data
data_path = os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release",  "Data","equity","usa","daily", "msft.zip")

# Check if the zip file exists and inspect its contents
if os.path.exists(data_path):
    with zipfile.ZipFile(data_path, 'r') as zip_file:
        # List all files inside the ZIP archive
        file_list = zip_file.namelist()
        print(f"Files in ZIP: {file_list}")

        # Check if msft.csv is present and correctly formatted
        if 'msft.csv' in file_list:
            with zip_file.open('msft.csv') as csv_file:
                # Read CSV without headers
                df = pd.read_csv(csv_file, header=None)
                print(f"Data preview:\n{df.head()}")
                
                # Assuming date is the first column (index 0)
                date_column = df[0]  # Adjust index if date is in a different column
                print(f"Date range: {date_column.min()} to {date_column.max()}")
        else:
            print("Error: msft.csv not found in the ZIP file.")
else:
    print("Error: msft.zip does not exist in the expected directory.")

