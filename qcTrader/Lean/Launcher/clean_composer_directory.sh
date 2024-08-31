#!/bin/bash

# Define paths
SOURCE_DIR="D:/qcTrader-par1/qcTrader/Lean/Launcher/bin/Release"  # Update this to your actual build output directory
TARGET_DIR="D:/qcTrader-par1/qcTrader/Lean/Launcher/composer"  # Update this to your target composer-dll-directory

# Clear the target directory
rm -rf "$TARGET_DIR/*"  # Remove all files in the target directory

# Copy DLL files, JSON configurations, and DLL config files
find "$SOURCE_DIR" -name "*.dll" -exec cp {} "$TARGET_DIR" \;  # Copy all DLL files
find "$SOURCE_DIR" -name "*.json" -exec cp {} "$TARGET_DIR" \;  # Copy necessary JSON files
find "$SOURCE_DIR" -name "*.dll.config" -exec cp {} "$TARGET_DIR" \;  # Copy DLL config files

# Clear DLL, JSON, and DLL config files from the source directory
find "$SOURCE_DIR" -name "*.dll" -exec rm {} \;  # Remove DLL files from the source directory
find "$SOURCE_DIR" -name "*.json" -exec rm {} \;  # Remove JSON files from the source directory
find "$SOURCE_DIR" -name "*.dll.config" -exec rm {} \;  # Remove DLL config files from the source directory

# Optional: Verify contents
echo "Files in composer-dll-directory:"
ls "$TARGET_DIR"
