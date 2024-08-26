import os
import platform
import subprocess
import sys
from qcTrader.installers.windows_installer import notify_user_and_exit
from qcTrader.utils.logger import setup_logger 


def is_dotnet_installed():
    """Check if the dotnet command is available."""
    try:
        subprocess.run(['dotnet', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def set_dotnet_root():
    """Set the DOTNET_ROOT environment variable based on the OS and Python installation path."""
    system = platform.system()
    
    # Detect the Python installation path
    python_install_path = os.path.dirname(sys.executable)
    
    # Set the .NET root path based on the Python installation path
    if system == "Windows":
        dotnet_root = os.path.join(python_install_path, "dotnet")
    elif system == "Linux":
        dotnet_root = os.path.join(python_install_path, "dotnet")
    elif system == "Darwin":
        dotnet_root = os.path.join(python_install_path, "dotnet")
    else:
        raise ValueError(f"Unsupported operating system: {system}")
    
    # Verify if the dotnet_root directory exists, if not, fall back to a common location
    if not os.path.isdir(dotnet_root):
        if system == "Windows":
            dotnet_root = r"C:\Program Files\dotnet"
        elif system == "Linux":
            dotnet_root = "/usr/share/dotnet"
        elif system == "Darwin":
            dotnet_root = "/usr/local/share/dotnet"
    
    # Check if the .NET runtime exists
    if not os.path.isdir(dotnet_root):
        raise EnvironmentError(f".NET runtime not found at {dotnet_root}")
    
    # Set DOTNET_ROOT for the current session
    os.environ['DOTNET_ROOT'] = dotnet_root
    print(f"DOTNET_ROOT set temporarily to {dotnet_root}")
    
    # Set DOTNET_ROOT permanently
    if system == "Windows":
        # Permanently set using setx
        subprocess.run(['setx', 'DOTNET_ROOT', dotnet_root], check=True)
        print(f"DOTNET_ROOT permanently set to {dotnet_root}. Restart your terminal to apply changes.")
    else:
        # For Linux/MacOS, add it to the profile files (e.g., ~/.bashrc or ~/.zshrc)
        bashrc_path = os.path.expanduser("~/.bashrc")
        zshrc_path = os.path.expanduser("~/.zshrc")
        if os.path.exists(bashrc_path):
            with open(bashrc_path, "a") as f:
                f.write(f'\nexport DOTNET_ROOT="{dotnet_root}"\n')
            print(f"Added DOTNET_ROOT to {bashrc_path}. Please restart your terminal or run 'source {bashrc_path}' to apply changes.")
        elif os.path.exists(zshrc_path):
            with open(zshrc_path, "a") as f:
                f.write(f'\nexport DOTNET_ROOT="{dotnet_root}"\n')
            print(f"Added DOTNET_ROOT to {zshrc_path}. Please restart your terminal or run 'source {zshrc_path}' to apply changes.")
        else:
            print(f"No suitable shell configuration file found for setting DOTNET_ROOT permanently.")

def install_dotnet():
    """Detect OS and instruct the user to install .NET SDK and Runtime if necessary."""
    logger = setup_logger()

    if is_dotnet_installed():
        logger.info(".NET is already installed.")
        set_dotnet_root()
        return
    else:
        notify_user_and_exit()
    
    