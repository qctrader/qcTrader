import os
import subprocess
import sys

from qcTrader.utils.logger import setup_logger
def set_environment_variables(dotnet_root):
    dotnet_root = dotnet_root.rstrip("\\/")
    sdk_path = os.path.join(dotnet_root, 'sdk')

    # Set DOTNET_ROOT environment variable permanently for the user
    subprocess.run(['setx', 'DOTNET_ROOT', dotnet_root, '/M'], check=True)

    # Update the PATH environment variable permanently for the user
    current_path = os.environ['PATH']
    new_path = f"{dotnet_root};{sdk_path};" + current_path
    subprocess.run(['setx', 'PATH', new_path, '/M'], check=True)

    # Set COREHOST_TRACE environment variable permanently
    subprocess.run(['setx', 'COREHOST_TRACE', '1', '/M'], check=True)

    # Update the PATH, DOTNET_ROOT, and COREHOST_TRACE for the current process to take effect immediately
    os.environ['DOTNET_ROOT'] = dotnet_root
    os.environ['PATH'] = new_path
    os.environ['COREHOST_TRACE'] = '1'
