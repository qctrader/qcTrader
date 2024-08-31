import os
import zipfile

def test_access(zip_path, csv_name):
    print(os.getcwd())
    print(f"Does the path exist? {os.path.exists(zip_path)}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            with zip_file.open(csv_name) as csv_file:
                content = csv_file.read()
                print("Successfully accessed the file.")
                print(f"First 100 bytes: {content[:100]}")
    except Exception as e:
        print(f"Error accessing the file: {e}")

test_access(os.path.join(os.getcwd(), "qcTrader", "Lean", "Launcher", "bin", "Release",  "Data","equity","usa","daily", "msft.zip"), "msft.csv")
