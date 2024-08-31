import yfinance as yf
import pandas as pd
from zipfile import ZipFile
import os

def download_corporate_actions(symbol, start_date, end_date):
    """
    Downloads splits and dividends for the given symbol and date range using yfinance.
    """
    ticker = yf.Ticker(symbol)

    # Download splits and dividends with date range filtering
    splits = ticker.splits.loc[start_date:end_date]  # Filter splits within the date range
    dividends = ticker.dividends.loc[start_date:end_date]  # Filter dividends within the date range

    # Format splits data
    if not splits.empty:
        splits_df = splits.reset_index()
        splits_df['EventType'] = 'Split'
        splits_df['Date'] = splits_df['Date'].dt.strftime('%Y%m%d')
        splits_df = splits_df.rename(columns={splits.name: 'Value'})  # Renaming the column to 'Value'
        splits_df = splits_df[['EventType', 'Date', 'Value']]
    else:
        splits_df = pd.DataFrame(columns=['EventType', 'Date', 'Value'])

    # Format dividends data
    if not dividends.empty:
        dividends_df = dividends.reset_index()
        dividends_df['EventType'] = 'Dividend'
        dividends_df['Date'] = dividends_df['Date'].dt.strftime('%Y%m%d')
        dividends_df = dividends_df.rename(columns={dividends.name: 'Value'})  # Renaming the column to 'Value'
        dividends_df = dividends_df[['EventType', 'Date', 'Value']]
    else:
        dividends_df = pd.DataFrame(columns=['EventType', 'Date', 'Value'])

    # Combine splits and dividends
    corporate_actions = pd.concat([splits_df, dividends_df]).sort_values(by='Date')

    return corporate_actions

def save_factor_file(symbol, corporate_actions):
    """
    Generates and saves a factor file for Lean using splits data.
    """
    directory = 'qcTrader/Lean/Launcher/bin/Release/Data/equity/usa/factor_files'
    filename = f"{symbol.lower()}.csv"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)

    # Calculate cumulative adjustment factors
    if not corporate_actions.empty:
        # Include both splits and dividends in the factor calculations
        factors = []
        cumulative_factor = 1.0
        
        for _, row in corporate_actions.iterrows():
            date = row['Date']
            if row['EventType'] == 'Split':
                # Calculate split adjustment factor
                factor = 1 / row['Value']
                cumulative_factor *= factor
                factors.append([date, cumulative_factor])
            elif row['EventType'] == 'Dividend':
                # Include dividend adjustments if applicable
                factor = 1.0  # Dividend handling would depend on the exact dividend policy
                factors.append([date, cumulative_factor])

        # Save factors if any adjustments exist
        if factors:
            factors_df = pd.DataFrame(factors, columns=['Date', 'Factor'])
            factors_df.to_csv(file_path, index=False, header=False)
            print(f"Saved factor file for {symbol} to {file_path}")
        else:
            # Create a default factor file with factor of 1 if no actions exist
            print(f"No split or significant dividend data for {symbol}. Creating default factor file.")
            pd.DataFrame([[f"20200101,1.0"]]).to_csv(file_path, index=False, header=False)
    else:
        # Create a default factor file with factor of 1
        print(f"No corporate actions data to create factor file for {symbol}. Creating default factor file.")
        pd.DataFrame([[f"20200101,1.0"]]).to_csv(file_path, index=False, header=False)

def save_corporate_actions_to_lean_format(data, symbol):
    """
    Saves corporate actions data to Lean's expected format and location.
    """
    # Define Lean's expected directory and filename
    directory = 'qcTrader/Lean/Launcher/bin/Release/Data/equity/usa/corporateactions'
    filename = f"{symbol.lower()}.zip"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)

    # Save data to a CSV within a ZIP file
    csv_filename = f"{symbol.lower()}.csv"
    data.to_csv(csv_filename, index=False)

    with ZipFile(file_path, 'w') as zipf:
        zipf.write(csv_filename, arcname=csv_filename)

    # Remove the temporary CSV file
    os.remove(csv_filename)

    print(f"Saved corporate actions for {symbol} to {file_path}")

# Example Usage
if __name__ == "__main__":
    symbol = 'MSFT'
    start_date = '2020-01-01'
    end_date = '2024-08-30'

    # Download and validate corporate actions data
    corporate_actions = download_corporate_actions(symbol, start_date, end_date)
    if not corporate_actions.empty:
        print(f"Downloaded corporate actions for {symbol}:\n", corporate_actions.head())
        save_corporate_actions_to_lean_format(corporate_actions, symbol)
        save_factor_file(symbol, corporate_actions)
    else:
        print(f"No corporate actions data available for {symbol} from {start_date} to {end_date}.")





