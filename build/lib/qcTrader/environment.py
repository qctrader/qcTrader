import os
import subprocess
import sys
import platform

def find_libpython_so():
    """Dynamically locate the libpython3.X.so shared library on Linux."""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    libpython_name = f"libpython{python_version}.so"

    try:
        # Use the find command to locate libpython3.X.so
        print(f"Searching for {libpython_name}...")
        result = subprocess.run(['sudo', 'find', '/usr', '-name', libpython_name], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        
        # Check if the command found any results
        if result.stdout:
            path = result.stdout.splitlines()[0]  # Use the first found path
            if os.path.exists(path):
                print(f"Found {libpython_name} at: {path}")
                return path
        else:
            print(f"{libpython_name} not found using find command.")
            raise FileNotFoundError(f"{libpython_name} not found on your system.")
    
    except subprocess.TimeoutExpired:
        print(f"Search for {libpython_name} timed out.")
        raise
    except subprocess.CalledProcessError as e:
        print(f"Error running find command: {e}")
        raise

def find_python_dll():
    """Locate the Python DLL or shared library based on the operating system."""
    python_version = f"{sys.version_info.major}{sys.version_info.minor}"
    system = platform.system()

    # Determine the base prefix (Python installation directory or virtual environment)
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        base_prefix = sys.base_prefix
    else:
        # Not in a virtual environment
        base_prefix = sys.prefix

    if system == "Windows":
        # On Windows, the DLL file is named pythonXX.dll (e.g., python311.dll for Python 3.11)
        python_dll_name = f"python{python_version}.dll"
        dll_path = os.path.join(base_prefix, python_dll_name)

    elif system == "Darwin":
        # On macOS, the shared library is typically named libpython3.X.dylib
        python_dll_name = f"libpython{sys.version_info.major}.{sys.version_info.minor}.dylib"
        dll_path = os.path.join(base_prefix, 'lib', python_dll_name)

    elif system == "Linux":
        # On Linux, the shared library is typically named libpython3.X.so
        dll_path = find_libpython_so()

    else:
        raise EnvironmentError(f"Unsupported platform: {system}")

    # Normalize the path to ensure it uses the correct path separators
    dll_path = os.path.normpath(dll_path)
    
    # Verify that the DLL or shared library exists
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"Python shared library not found at {dll_path}")
    
    return dll_path

def set_python_dll_env_var():
    """Set the PYTHONNET_PYDLL environment variable to the correct libpython path."""
    try:
        dll_path = find_python_dll()
        os.environ['PYTHONNET_PYDLL'] = dll_path
        print(f"PYTHONNET_PYDLL set to {dll_path}")
    except (EnvironmentError, FileNotFoundError) as e:
        print(f"Error setting PYTHONNET_PYDLL: {e}")
        sys.exit(1)


