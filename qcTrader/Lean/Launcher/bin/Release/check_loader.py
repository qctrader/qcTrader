import ctypes
import os

def is_dll_loaded(dll_path):
    """
    Check if the specified DLL is loaded.
    
    :param dll_path: Path to the DLL file.
    :return: True if the DLL is loaded, False otherwise.
    """
    try:
        # Load the DLL
        ctypes.cdll.LoadLibrary(dll_path)
        return True
    except OSError as e:
        # DLL could not be loaded
        print(f"Failed to load DLL: {e}")
        return False

def main():
    # Replace with the path to your DLL
    dll_path = 'D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\composer\YFinanceDataProvider.dll'
    
    if is_dll_loaded(dll_path):
        print(f"The DLL at {dll_path} is loaded.")
    else:
        print(f"The DLL at {dll_path} is not loaded.")

if __name__ == "__main__":
    main()
