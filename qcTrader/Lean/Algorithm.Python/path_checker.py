import os

# Assuming current_dir is where your script or the running process is located
current_dir = os.path.dirname(os.path.abspath(__file__))
print(os.getcwd())
print(f"current_dir----------->{current_dir}")
# Construct the path to the DLL
dll_path = os.path.join(current_dir, '..', '..','Lean', 'Launcher', 'composer', 'CustomDataProvider.dll')

# Normalize and print the path to ensure correctness
dll_path = os.path.normpath(dll_path)
print(f"DLL Path: {dll_path}")

# Check if the file exists
if os.path.exists(dll_path):
    print("DLL path is correct and the file exists.")
else:
    print("DLL path is incorrect or the file does not exist.")
