import os
import platform
import subprocess
import sys
import distro  # To detect the Linux distribution

def is_dotnet_installed():
    """Check if the dotnet command is available."""
    try:
        subprocess.run(['dotnet', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_ubuntu_version():
    """Get the Ubuntu version using the distro module."""
    return distro.version()

import subprocess

def install_dotnet_on_ubuntu():
    """Install both .NET SDK and Runtime on Ubuntu."""
    try:
        ubuntu_version = get_ubuntu_version()
        wget_url = f"https://packages.microsoft.com/config/ubuntu/{ubuntu_version}/packages-microsoft-prod.deb"
        
        print("Updating package list...")
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        
        print("Installing required dependencies...")
        subprocess.run(['sudo', 'apt', 'install', '-y', 'wget', 'apt-transport-https'], check=True)
        
        print(f"Downloading .NET package for Ubuntu {ubuntu_version} from {wget_url}...")
        subprocess.run(['wget', wget_url, '-O', 'packages-microsoft-prod.deb'], check=True)
        
        print("Installing .NET package...")
        subprocess.run(['sudo', 'dpkg', '-i', 'packages-microsoft-prod.deb'], check=True)
        
        print("Updating package list again...")
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        
        # Install .NET SDK
        dotnet_sdk_package = f"dotnet-sdk-6.0"
        print(f"Installing .NET SDK 6.0...")
        subprocess.run(['sudo', 'apt', 'install', '-y', dotnet_sdk_package], check=True)
        
        # Install the specific .NET Runtime version 6.0.33
        dotnet_runtime_package = f"dotnet-runtime-6.0"
        print(f"Installing .NET Runtime 6.0.33...")
        subprocess.run(['sudo', 'apt', 'install', '-y', dotnet_runtime_package], check=True)

        # Ensure the specific patch version 6.0.33 is installed
        print(f"Installing .NET Core Runtime 6.0.33 specifically...")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'dotnet-hostfxr-6.0=6.0.33*'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'aspnetcore-runtime-6.0=6.0.33*'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'dotnet-runtime-6.0=6.0.33*'], check=True)
        
        print(f".NET SDK and Runtime 6.0.33 installed successfully on Ubuntu.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install .NET on Ubuntu: {e}")
        print("Attempting installation via dotnet-install.sh script as fallback.")
        install_dotnet_on_generic_linux()

def install_dotnet_on_generic_linux():
    """Install both .NET SDK and Runtime on non-Ubuntu Linux distributions."""
    try:
        print(f"Downloading dotnet-install.sh script for .NET 6.0...")
        subprocess.run(['wget', 'https://dot.net/v1/dotnet-install.sh', '-O', 'dotnet-install.sh'], check=True)
        
        print("Making dotnet-install.sh executable...")
        subprocess.run(['chmod', '+x', 'dotnet-install.sh'], check=True)
        
        # Install .NET SDK
        print(f"Running dotnet-install.sh script to install .NET SDK 6.0...")
        subprocess.run(['./dotnet-install.sh', '--install-dir', '/usr/share/dotnet', '--version', '6.0.425'], check=True)
        
        # Install the specific .NET Runtime version 6.0.33
        print(f"Running dotnet-install.sh script to install .NET Runtime 6.0.33...")
        subprocess.run(['sudo','./dotnet-install.sh', '--install-dir', '/usr/share/dotnet', '--runtime', 'dotnet', '--version', '6.0.33'], check=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f".NET SDK and Runtime 6.0.33 installed successfully on Linux.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install .NET on Linux: {e}")



def install_dotnet_on_mac():
    """Install .NET SDK and Runtime on macOS if not already installed."""
    try:
        print("Installing .NET SDK on macOS using Homebrew...")
        subprocess.run(['/bin/bash', '-c', 'brew install --cask dotnet-sdk'], check=True)
        
        print(".NET SDK installed successfully on macOS.")
        
        # Install .NET Runtime via Homebrew (runtime is generally included with SDK, but to be explicit)
        print("Installing .NET Runtime on macOS using Homebrew...")
        subprocess.run(['/bin/bash', '-c', 'brew install dotnet-runtime'], check=True)
        
        print(".NET SDK and Runtime installed successfully on macOS.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install .NET on macOS: {e}")
        sys.exit(1)

def install_dotnet_on_windows():
    """Install .NET SDK and Runtime on Windows if not already installed."""
    try:
        print("Downloading .NET SDK installer for Windows...")
        subprocess.run(['powershell', '-Command',
                        'Invoke-WebRequest -Uri https://dotnet.microsoft.com/download/dotnet/thank-you/sdk-6.0.302-windows-x64-installer -OutFile dotnet-installer.exe'],
                       check=True)
        
        print("Running .NET SDK installer on Windows...")
        subprocess.run(['powershell', '-Command', '.\\dotnet-installer.exe', '/quiet', '/norestart'], check=True)
        
        print(".NET SDK installed successfully on Windows.")
        
        # Install .NET Runtime explicitly
        print("Installing .NET Runtime on Windows...")
        subprocess.run(['powershell', '-Command',
                        'Invoke-WebRequest -Uri https://dotnet.microsoft.com/download/dotnet/thank-you/runtime-6.0.302-windows-x64-installer -OutFile dotnet-runtime-installer.exe'],
                       check=True)
        subprocess.run(['powershell', '-Command', '.\\dotnet-runtime-installer.exe', '/quiet', '/norestart'], check=True)
        
        print(".NET SDK and Runtime installed successfully on Windows.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install .NET on Windows: {e}")
        sys.exit(1)

def create_dotnet_symlink():
    """Create a symlink for the .NET host directory if it doesn't exist."""
    target_path = '/usr/lib/dotnet/host'
    link_path = '/usr/share/dotnet/host'

    try:
        if not os.path.exists(link_path):
            print(f"Creating symlink: {link_path} -> {target_path}")
            subprocess.run(['sudo', 'ln', '-s', target_path, link_path], check=True)
            print(f"Symlink created successfully.")
        else:
            print(f"Symlink already exists: {link_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create symlink: {e}")
        raise


def install_dotnet():
    """Detect OS and install .NET SDK and Runtime if necessary."""

    # Set the DOTNET_ROOT environment variable
    # set_dotnet_root()
    if not is_dotnet_installed():
        system = platform.system()
        print(f"{system} detected. Installing .NET SDK and Runtime...")
       
        if system == "Linux":
            distro_name = distro.id().lower()
            if "ubuntu" in distro_name:
                create_dotnet_symlink()
                install_dotnet_on_ubuntu()
            else:
                create_dotnet_symlink()
                install_dotnet_on_generic_linux()
        elif system == "Darwin":
            install_dotnet_on_mac()
        elif system == "Windows":
            install_dotnet_on_windows()
        else:
            print(f"Unsupported platform: {system}")
            sys.exit(1)

    if not is_dotnet_installed():
        print(".NET installation failed.")
        print("Aborting ........................")
        sys.exit(1)

      

