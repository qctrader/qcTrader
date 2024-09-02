import clr

def load_dll(dll_path):
    try:
        # Load the .NET assembly
        clr.AddReference(dll_path)
        print("DLL loaded successfully.")
    except Exception as e:
        print(f"Error loading DLL: {e}")

def access_class(dll_path, class_name):
    try:
        # Load the assembly
        load_dll(dll_path)
        
        # Access the class
        namespace_and_class = class_name.split('.')
        module = __import__(namespace_and_class[0])
        for part in namespace_and_class[1:]:
            module = getattr(module, part)
        
        print(f"Successfully accessed class {class_name}.")
        return module
    except Exception as e:
        print(f"Error accessing class: {e}")

def main():
    dll_path = r'D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\composer\YFinanceDataProvider.dll'
    class_name = 'YFinanceDataProvider.PythonRunner'
    
    access_class(dll_path, class_name)

if __name__ == "__main__":
    main()
