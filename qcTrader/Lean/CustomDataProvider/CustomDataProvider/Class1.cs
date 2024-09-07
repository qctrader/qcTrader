using System;
using System.IO;
using QuantConnect.Interfaces;
using System.ComponentModel.Composition;
using QuantConnect.Configuration;
using System.Collections.Generic;
using System.Linq;
using System.IO.Compression;
using QuantConnect.Lean.Engine.DataFeeds;
using QuantConnect.Data;
using QuantConnect.Data.Custom;
using QuantConnect.Util;
using QuantConnect.Data.Market;
using QuantConnect;
using QuantConnect.Storage;
using QuantConnect.Lean.Engine.Storage;

namespace CustomDataProvider
{
    [Export(typeof(IDataProvider))]
    [Export("CustomDataProvider.CsvDataProvider", typeof(IDataProvider))]
    public class CsvDataProvider : IDataProvider
    {
        public event EventHandler<QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs>? NewDataRequest;
        private readonly ZipDataCacheProvider _zipCacheProvider;
        private readonly IDataProvider _dataProvider;
        private readonly IDataCacheProvider _dataCacheProvider;
        private readonly IObjectStore _objectStore;


        public CsvDataProvider()
        {
            _zipCacheProvider = new ZipDataCacheProvider(new DefaultDataProvider());
            _dataProvider = new DefaultDataProvider();
            _dataCacheProvider = new SingleEntryDataCacheProvider(_dataProvider);
            _objectStore = new LocalObjectStore();

        }

        
        public Stream? Fetch(string key)
        {
            Console.WriteLine($"The keys fetched found at: {key}");
            bool fetchedSuccessfully = false;

            // Normalize the key path to ensure consistent separators
            string normalizedKey = key.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar);
            string mapFilePath = normalizedKey;

            // Check if the key indicates interest rate data
            if (mapFilePath.Contains("interest-rate", StringComparison.OrdinalIgnoreCase))
            {
                // Initialize a variable to hold the first interest rate value
                decimal firstInterestRate;

                // Use the static InterestRateProvider method to fetch the interest rate data
                Dictionary<DateTime, decimal> interestRates = InterestRateProvider.FromCsvFile(mapFilePath, out firstInterestRate);

                if (interestRates != null && interestRates.Count > 0)
                {
                    fetchedSuccessfully = true;
                    Console.WriteLine($"Interest rate data successfully fetched. First rate: {firstInterestRate}");

                    // Handle the interestRates dictionary as needed
                    // For demonstration, you might convert it to a Stream, log it, or process it directly.
                    OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(mapFilePath, fetchedSuccessfully));

                    // If needed, serialize the dictionary to a stream or handle according to your application's needs
                    // Example: Returning null since it's not directly convertable to a Stream
                    return null;
                }
                else
                {
                    Console.WriteLine("Failed to fetch interest rate data or data is empty.");
                }
            }

            // Determine the zip file path from the map file or factor file key
            string zipFilePath = GetZipFilePath(mapFilePath, "daily");

            // Check if the daily zip file exists and try fetching it using ZipDataCacheProvider
            if (!string.IsNullOrEmpty(zipFilePath) && File.Exists(zipFilePath))
            {
                Stream? dataStream = _zipCacheProvider.Fetch(zipFilePath);

                if (dataStream != null)
                {
                    fetchedSuccessfully = true;
                    Console.WriteLine("Data successfully fetched from ZipCacheProvider for daily frequency.");
                    OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(zipFilePath, fetchedSuccessfully));
                    return dataStream;
                }
            }

            //string symbol = ExtractSymbolFromKey(mapFilePath);
            //if (string.IsNullOrEmpty(symbol))
            //{
            //    Console.WriteLine($"Unable to extract symbol from key: {key}");
            //    return null;
            //}

            //string csvFileName = $"{symbol.ToLower()}.csv";

            //// Create the SubscriptionDataSource pointing to the zip file with CSV format
            //var dataSource = new SubscriptionDataSource(
            //    zipFilePath,
            //    SubscriptionTransportMedium.LocalFile,
            //    FileFormat.Csv
            //);

            //// Configure the SubscriptionDataConfig for the current symbol
            //var config = new SubscriptionDataConfig(
            //    typeof(TradeBar),             // Adjust based on your data type
            //    Symbol.Create(symbol, SecurityType.Equity, Market.USA),  // Create symbol dynamically
            //    Resolution.Daily,              // Adjust the resolution as needed
            //    TimeZones.NewYork,            // Data time zone
            //    TimeZones.NewYork,            // Exchange time zone
            //    false,                        // Is fill forward?
            //    false,                        // Is extended market hours?
            //    false                         // Is trade bar?
            //);

            //var date = DateTime.UtcNow.Date;

            //// Use the ForSource method to get the appropriate ISubscriptionDataSourceReader
            //try
            //{
            //    var factory = new TradeBar();  // Replace with appropriate BaseData type if different
            //    var reader = SubscriptionDataSourceReader.ForSource(dataSource, _dataCacheProvider, config, date, false, factory, _dataProvider, _objectStore);

            //    // Use the reader to read data
            //    var dataPoints = reader.Read(dataSource).ToList();

            //    // If data points are successfully read, handle as needed
            //    if (dataPoints.Any())
            //    {
            //        fetchedSuccessfully = true;
            //        Stream? dataStream_2 = _zipCacheProvider.Fetch(zipFilePath);
            //        Console.WriteLine($"Data successfully fetched using SubscriptionDataSourceReader for {symbol} in {zipFilePath}.");
            //        OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(zipFilePath, fetchedSuccessfully));

            //        // Convert data points to a stream if necessary
            //        // Example: Returning null since it's not directly convertible to a Stream
            //        return dataStream_2;  // Replace with stream handling if needed
            //    }
            //}
            //catch (Exception ex)
            //{
            //    Console.WriteLine($"Error reading data source using SubscriptionDataSourceReader for symbol {symbol}: {ex.Message}");
                
            //}


            //Trigger event to notify of new data request, even if unsuccessful
            OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(key, fetchedSuccessfully));
            return null;
        }


        private string ExtractSymbolFromKey(string key)
        {
            // Extract the file name from the key and remove the extension to get the symbol
            string fileName = Path.GetFileNameWithoutExtension(key);
            if (string.IsNullOrWhiteSpace(fileName))
            {
                return string.Empty;
            }

            // The symbol is directly the file name (e.g., "msft" from "msft.csv")
            return fileName.ToUpper(); // Convert to uppercase to maintain consistency
        }

        public string GetZipFilePath(string key, string frequency = "daily")
        {
            // Normalize path separators to ensure consistency across platforms
            string normalizedKey = key.Replace('\\', Path.DirectorySeparatorChar)
                                      .Replace('/', Path.DirectorySeparatorChar);

            // Determine the directory based on the content type
            string directory = Path.GetDirectoryName(normalizedKey) ?? string.Empty;

            // Initialize the file name and extension
            string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(normalizedKey);
            string fileName = string.Empty;
            string fileExtension = ".zip";  // Default to .zip for price data

            // Check if the key corresponds to map files or factor files
            if (directory.Contains("map_files", StringComparison.OrdinalIgnoreCase))
            {
                // Map files are CSV format
                directory = directory.Replace("map_files", "map_files");
                fileExtension = ".csv";  // Use .csv extension for map files
            }
            else if (directory.Contains("factor_files", StringComparison.OrdinalIgnoreCase))
            {
                // Factor files are also in CSV format
                directory = directory.Replace("factor_files", "factor_files");
                fileExtension = ".csv";  // Use .csv extension for factor files
            }
            else if (directory.Contains("alternative", StringComparison.OrdinalIgnoreCase))
            {
                // Handling for alternative data like interest rates
                fileExtension = ".csv";  // Set to .csv for alternative data
            }
            else
            {
                // Default replacement for other frequency-based needs (e.g., daily price data)
                directory = directory.Replace("map_files", frequency);
            }

            // Construct the full file name with the appropriate extension
            fileName = fileNameWithoutExtension + fileExtension;

            // Combine the modified directory with the constructed file name
            string filePath = Path.Combine(directory, fileName);

            // Log the constructed path for verification
            Console.WriteLine($"Constructed File Path: {filePath}");

            // Check the existence of the constructed file path
            if (File.Exists(filePath))
            {
                Console.WriteLine($"File found at: {filePath}");
                return filePath;
            }
            else
            {
                Console.WriteLine($"File not found at: {filePath}");
                return string.Empty;
            }
        }
        protected virtual void OnNewDataRequest(QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs e)
        {
            NewDataRequest?.Invoke(this, e);
        }
    }
}
