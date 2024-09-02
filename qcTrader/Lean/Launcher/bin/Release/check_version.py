import clr
import os

def test_pythonnet():
    
    try:
       # Update this path to where your DLL is located
        dll_path = r'D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\composer\YFinanceDataProvider.dll'

        if os.path.exists(dll_path):
            clr.AddReference(dll_path)
            print("DLL loaded successfully.")
        else:
            print("DLL path does not exist.")

            # Access a class from the assembly
        from YFinanceDataProvider import PythonRunner
        print("Class loaded successfully.")
        
        # Create an instance of the class
        instance = PythonRunner()
        print("Instance created successfully.")    

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pythonnet()
