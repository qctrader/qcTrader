# YFinanceDataProvider.py

import sys
import os
import zipfile
from io import BytesIO
import clr

# Determine the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the correct Launcher/bin/Release directory
release_dir = os.path.join(current_dir, '..', 'Launcher', 'bin', 'Release')
# Normalize the path to remove any redundant separators or up-level references
release_dir = os.path.normpath(release_dir)

print(f"release_dir--------------->{release_dir}")

# Add the directory to sys.path if it's not already in sys.path
if release_dir not in sys.path:
    sys.path.append(release_dir)

# Assuming path points to the directory where your DLLs are stored
path = "D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\composer"
# Load QuantConnect assemblies dynamically
for file in os.listdir(path):
    if file.endswith(".dll") and file.startswith("QuantConnect."):
        clr.AddReference(os.path.join(path, file))  # Provide full path

# Import System and other namespaces
from System import *
try:
    from System.Drawing import *  # For .NET Core, this might need to be System.Drawing.Common
except ImportError as e:
    print(f"Failed to import System.Drawing: {e}")

from AlgorithmImports import * 


class YFinanceDataProvider(IDataProvider):
    def Fetch(self, key: str) -> Any:
        # Example key might be "equity/usa/daily/msft.csv", "equity/usa/daily/aapl.csv", etc.
        print(f"Fetching data for key: {key}")  # Debugging to see the key

        # Split the key to extract the ticker symbol (e.g., "msft" from "equity/usa/daily/msft.csv")
        parts = key.split('/')
        if len(parts) >= 4:
            ticker = parts[-1].split('.')[0]  # Extracts the ticker, e.g., "msft"

            # Define the path to your ZIP file based on the ticker
            zip_path = os.path.join("equity/usa/daily", f"{ticker}.zip")

            # Check if the ZIP file exists
            if os.path.exists(zip_path):
                try:
                    with zipfile.ZipFile(zip_path, 'r') as z:
                        # Construct the CSV filename within the ZIP (e.g., "msft.csv")
                        csv_filename = f"{ticker}.csv"
                        if csv_filename in z.namelist():
                            # Read and return the CSV file data as a byte stream
                            file_data = z.read(csv_filename)
                            return BytesIO(file_data)
                except Exception as e:
                    print(f"Error fetching data for {ticker} from ZIP: {e}")

        # Return None if the data can't be found or an error occurs
        return None
