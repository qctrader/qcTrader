import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import zipfile
import os

def download_and_transform_data(symbol, start_date, end_date):
    # Step 1: Download data using yfinance
    data = yf.download(symbol, start=start_date, end=end_date, interval='1d', auto_adjust=True)

    # Check if there are any 0.0 values in the raw downloaded data
    zero_data = data[(data == 0.0).any(axis=1)]
    if not zero_data.empty:
        print("Rows with 0.0 values in downloaded data:")
        print(zero_data)
    else:
        print("No 0.0 values in downloaded data.")

    # Step 2: Reset index and adjust Date column
    data.reset_index(inplace=True)
    data['Date'] = data['Date'].dt.strftime('%Y%m%d')  # Format date as YYYYMMDD
    print("Data after formatting Date:")
    print(data.head())

    # Step 3: Hypothetical Scaling (if needed) - Check scaling accuracy
    # Assuming a scaling factor that may cause issues
    scaling_factor = 10000  # Adjust based on actual needs
    data['Open'] = data['Open'] / scaling_factor
    data['High'] = data['High'] / scaling_factor
    data['Low'] = data['Low'] / scaling_factor
    data['Close'] = data['Close'] / scaling_factor

    # Print details after scaling to inspect potential issues
    print("Data after scaling:")
    print(data.head())

    # Check for 0.0 values after scaling
    zero_data_scaled = data[(data == 0.0).any(axis=1)]
    if not zero_data_scaled.empty:
        print("Rows with 0.0 values after scaling:")
        print(zero_data_scaled)
    else:
        print("No 0.0 values after scaling.")

    # Step 4: Select required columns and reorder them
    data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]  # Ensure correct column order
    print("Data before saving to CSV:")
    print(data.head())

    # Check for 0.0 values in the final transformed data
    zero_data_final = data[(data == 0.0).any(axis=1)]
    if not zero_data_final.empty:
        print("Rows with 0.0 values in final transformed data:")
        print(zero_data_final)
    else:
        print("No 0.0 values in final transformed data.")

    # Define paths for saving
    output_folder = 'custom_folder'
    os.makedirs(output_folder, exist_ok=True)
    csv_filename = f'{symbol.lower()}.csv'
    csv_path = os.path.join(output_folder, csv_filename)
    zip_path = os.path.join(output_folder, f'{symbol.lower()}.zip')

    # Step 5: Save the data as CSV without headers
    data.to_csv(csv_path, index=False, header=False)

    # Check for 0.0 values in the saved CSV (final check)
    df = pd.read_csv(csv_path, header=None)
    zero_data_csv = df[(df == 0.0).any(axis=1)]
    if not zero_data_csv.empty:
        print("Rows with 0.0 values in the saved CSV:")
        print(zero_data_csv)
    else:
        print("No 0.0 values in the saved CSV.")

    # Step 6: Compress the CSV into a ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_path, arcname=csv_filename)

    # Clean up the CSV file if not needed
    os.remove(csv_path)

    print(f"Data for {symbol} formatted and saved to {zip_path}.")

# Run the function with the MSFT symbol
download_and_transform_data('MSFT', datetime(2020, 1, 1) - timedelta(days=10), datetime(2023, 1, 1))
