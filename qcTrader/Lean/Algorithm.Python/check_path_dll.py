import os

dll_path = r"qcTrader\\Lean\\Launcher\\composer\\YFinanceDataProvider.dll"
if os.path.isfile(dll_path):
    print("DLL file exists.")
else:
    print("DLL file not found.")
