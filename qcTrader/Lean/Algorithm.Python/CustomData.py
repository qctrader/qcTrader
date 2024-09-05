from datetime import datetime
from QuantConnect.Data.Custom import PythonData
from QuantConnect.Configuration import Config
from QuantConnect.Data import SubscriptionDataSource, SubscriptionTransportMedium, FileFormat

class CustomData(PythonData):
    def GetSource(self, config, date, isLiveMode):
        data_folder = Config.Get("data-folder")
        source = f"file://{data_folder}/equity/usa/daily/{config.Symbol.Value.lower()}.zip"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.LocalFile, FileFormat.Zip)

    def Reader(self, config, line, date, isLiveMode):
        data = CustomData()
        try:
            # Split the CSV line by commas and parse fields
            csv = line.split(',')
            data.Symbol = config.Symbol
            data.Time = datetime.strptime(csv[0], '%Y%m%d %H:%M')  # Assuming date in YYYYMMDD format
            data.Value = float(csv[4])  # Using 'Close' as the main value
            data["Open"] = float(csv[1])
            data["High"] = float(csv[2])
            data["Low"] = float(csv[3])
            data["Close"] = float(csv[4])
            data["Volume"] = int(csv[5])
        except ValueError:
            # Handle parsing errors
            return None
        return data


