import subprocess
import sys
from qcTrader.utils.logger import setup_logger
import ctypes
logger = setup_logger()

def is_dotnet_installed():
    """Check if .NET is already installed."""
    try:
        result = subprocess.run(['dotnet', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f".NET version installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info(".NET is not installed.")
        return False

def check_admin_privileges():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logger.error(f"Failed to check admin privileges: {e}")
        return False

def notify_user_and_exit():
    """Notify the user to install .NET SDK and Runtime, then exit the script."""
    message = (
        "The .NET SDK and Runtime are required to run this package.\n"
        "Please install .NET manually by following these steps:\n"
        "1. Visit the .NET download page: https://dotnet.microsoft.com/download\n"
        "2. Download and install the latest .NET SDK and Runtime for your operating system.\n"
        "3. After installation, run this package again.\n"
    )
    logger.error(message)
    sys.exit(1)