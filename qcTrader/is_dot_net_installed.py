import os
import platform
import subprocess
import sys
from qcTrader.installers.windows_installer import notify_user_and_exit
# from installers.linux_installer import install_dotnet_linux
# from installers.mac_installer import install_dotnet_mac
from qcTrader.utils.logger import setup_logger 


def is_dotnet_installed():
    """Check if the dotnet command is available."""
    try:
        subprocess.run(['dotnet', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def set_dotnet_root():
    """Set the DOTNET_ROOT environment variable based on the OS."""
    system = platform.system()
    
    if system == "Windows":
        dotnet_root = r"C:\Program Files\dotnet"
    elif system == "Linux":
        dotnet_root = "/usr/share/dotnet"
    elif system == "Darwin":
        dotnet_root = "/usr/local/share/dotnet"
    else:
        raise ValueError(f"Unsupported operating system: {system}")

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
        with open(bashrc_path, "a") as f:
            f.write(f'\nexport DOTNET_ROOT="{dotnet_root}"\n')
        print(f"Added DOTNET_ROOT to {bashrc_path}. Please restart your terminal or run 'source {bashrc_path}' to apply changes.")

def install_dotnet():
    """Detect OS and instruct the user to install .NET SDK and Runtime if necessary."""
    logger = setup_logger()

    if is_dotnet_installed():
        logger.info(".NET is already installed.")
        set_dotnet_root()
        return
    
    system = platform.system()
    
    if system == "Windows":
        notify_user_and_exit()
    elif system == "Linux":
        # Uncomment the following line when ready to support Linux
        # install_dotnet_linux()
        logger.info("Linux detected. .NET installation logic for Linux is currently not implemented.")
    elif system == "Darwin":
        # Uncomment the following line when ready to support macOS
        # install_dotnet_mac()
        logger.info("macOS detected. .NET installation logic for macOS is currently not implemented.")
    else:
        logger.error(f"Unsupported operating system: {system}")
        sys.exit(1)