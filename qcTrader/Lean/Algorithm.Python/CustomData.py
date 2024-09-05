from datetime import datetime
from QuantConnect.Data import BaseData, SubscriptionDataSource
from QuantConnect.Configuration import Config

class CustomDataParser(BaseData):
    def GetSource(self, config, date, isLiveMode):
        # Define the path to your data folder
        data_folder = Config.Get("data-folder")  # Fetch from Lean's config.json
        # Construct the full path to the ZIP file containing the CSV
        source = f"file://{data_folder}/equity/usa/daily/{config.Symbol.Value.lower()}.zip"
        # Create the SubscriptionDataSource without specifying the transport medium
        return SubscriptionDataSource(source)

    def Reader(self, config, stream, date, isLiveMode):
        data = CustomDataParser()
        try:
            # Read the next line from the stream
            line = stream.readline()
            if not line:
                return None  # End of file or empty line
            
            # Split the CSV line by commas and parse fields
            csv = line.strip().split(',')
            data.Symbol = config.Symbol
            # Parse date and time in the format 'YYYYMMDD HH:MM'
            data.Time = datetime.strptime(csv[0], '%Y%m%d %H:%M')
            data.Value = float(csv[4])  # Using 'Close' as the main value
            data["Open"] = float(csv[1])
            data["High"] = float(csv[2])
            data["Low"] = float(csv[3])
            data["Close"] = float(csv[4])
            data["Volume"] = int(csv[5])
        except (ValueError, IndexError) as e:
            # Handle parsing errors and log the issue for debugging
            self.Log(f"Error parsing line: {line}. Error: {e}")
            return None  # Return None if parsing fails
        return data

    def Clone(self):
        # Implement Clone to return a new instance of CustomDataParser
        return CustomDataParser()

    def DefaultResolution(self):
        # Specify the default resolution for this data type
        return Resolution.Daily

    def ToString(self):
        # Optional: Implement a string representation of the data
        return f"{self.Symbol} - {self.Time}: O:{self['Open']} H:{self['High']} L:{self['Low']} C:{self['Close']} V:{self['Volume']}"



