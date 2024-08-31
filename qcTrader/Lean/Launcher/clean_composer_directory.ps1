# Define paths
$sourceDir = "D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\bin\Release"  # Update this to your actual build output directory
$targetDir = "D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\composer"  # Update this to your target composer-dll-directory

# Clear the target directory
Remove-Item "$targetDir\*" -Recurse -Force  # Remove all files in the target directory

# Copy DLL files, JSON configurations, and DLL config files
Copy-Item "$sourceDir\*.dll" "$targetDir"  # Copy all DLL files
Copy-Item "$sourceDir\*.json" "$targetDir"  # Copy necessary JSON files
Copy-Item "$sourceDir\*.dll.config" "$targetDir"  # Copy DLL config files

# Clear DLL, JSON, and DLL config files from the source directory
Remove-Item "$sourceDir\*.dll" -Force  # Remove DLL files from the source directory
Remove-Item "$sourceDir\*.json" -Force  # Remove JSON files from the source directory
Remove-Item "$sourceDir\*.dll.config" -Force  # Remove DLL config files from the source directory

# Optional: Verify contents
Write-Host "Files in composer-dll-directory:"
Get-ChildItem -Path $targetDir