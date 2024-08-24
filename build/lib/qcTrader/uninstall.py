import os
import shutil
import sys

def uninstall_lean_runner():
    # Define user-specific paths
    user_paths_to_remove = [
        os.path.expanduser("~/qcTrader"),  # User-specific data
        os.path.expanduser("~/.qcTrader")  # Hidden user-specific configuration or data
    ]

    # Define system-wide paths, only if they exist on the current OS
    if sys.platform.startswith("linux") or sys.platform == "darwin":  # Linux or macOS
        system_paths_to_remove = [
            "/usr/local/qcTrader",  # System-wide directory
            "/etc/qcTrader"         # System-wide configuration directory
        ]
    elif sys.platform == "win32":  # Windows
        system_paths_to_remove = [
            os.path.join(os.getenv('ProgramFiles', 'C:\\Program Files'), 'qcTrader'),  # System-wide directory in Program Files
        ]



    # Combine all paths to remove
    paths_to_remove = user_paths_to_remove + system_paths_to_remove

    # Remove the specified directories
    for path in paths_to_remove:
        if os.path.exists(path):
            print(f"Removing directory: {path}")
            shutil.rmtree(path)
        else:
            print(f"Directory not found: {path}")

    print("Uninstall completed. All related files have been removed.")


