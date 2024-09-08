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
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace CustomDataProvider
{
    [Export(typeof(IDataProvider))]
    [Export("CustomDataProvider.CsvDataProvider", typeof(IDataProvider))]
    public class CsvDataProvider : IDataProvider
    {
        public event EventHandler<QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs>? NewDataRequest;
        private readonly IDataCacheProvider _dataCacheProvider;
        //private readonly IObjectStore _objectStore;
        private readonly HashSet<string> _fetchInProgressKeys = new HashSet<string>();


        public CsvDataProvider()
        {
            _dataCacheProvider = new ZipDataCacheProvider(this);
            //_objectStore = new LocalObjectStore();


        }


        //public Stream? Fetch(string key)
        //{
        //    Console.WriteLine($"Fetching data for key: {key}");
        //    bool fetchedSuccessfully = false;
        //    List<Stream> streamsToCombine = new List<Stream>();

        //    string normalizedKey = key.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar);
        //    string mapFilePath = normalizedKey;
        //    string symbolName = ExtractSymbolFromKey(mapFilePath);
        //    Symbol symbol = Symbol.Create(symbolName, SecurityType.Equity, Market.USA);


        //    string zipFilePath = GetZipFilePath(mapFilePath, "daily");

        //    if (!string.IsNullOrEmpty(zipFilePath) && File.Exists(zipFilePath))
        //    {
        //        try
        //        {
        //            Console.WriteLine($"Start processing ZIP file: {zipFilePath} at {DateTime.UtcNow}");

        //            var dataSource = new SubscriptionDataSource(
        //                zipFilePath,
        //                SubscriptionTransportMedium.LocalFile,
        //                FileFormat.ZipEntryName
        //            );

        //            var config = new SubscriptionDataConfig(
        //                typeof(TradeBar),
        //                symbol, 
        //                Resolution.Daily,
        //                TimeZones.NewYork,
        //                TimeZones.NewYork,
        //                false,
        //                false,
        //                false
        //            );

        //            var date = DateTime.UtcNow.Date;
        //            var factory = new TradeBar();

        //            // Setup a timeout cancellation token
        //            using (var cts = new CancellationTokenSource(TimeSpan.FromMinutes(4))) // Slightly less than 5 mins
        //            {
        //                var reader = SubscriptionDataSourceReader.ForSource(
        //                    dataSource,
        //                    _dataCacheProvider,
        //                    config,
        //                    date,
        //                    isLiveMode: false,
        //                    factory,
        //                    this,
        //                    _objectStore
        //                );

        //                // Start reading in a task with a timeout
        //                var task = Task.Run(() => reader.Read(dataSource).ToList(), cts.Token);

        //                // Await the task and check if it completes within the timeout
        //                if (task.Wait(TimeSpan.FromMinutes(4)))
        //                {
        //                    var dataPoints = task.Result;
        //                    Console.WriteLine($"Processed {dataPoints.Count} data points from the source.");
        //                    fetchedSuccessfully = true;

        //                    return ConvertDataPointsToStream(dataPoints);
        //                }
        //                else
        //                {
        //                    Console.WriteLine($"Data processing took too long and was cancelled: {zipFilePath}");
        //                    cts.Cancel(); // Explicitly cancel if timeout
        //                }
        //            }
        //        }
        //        catch (Exception ex)
        //        {
        //            Console.WriteLine($"Error processing data from ZIP: {ex.Message}");
        //            fetchedSuccessfully = false;
        //        }
        //    }
        //    else
        //    {
        //        Console.WriteLine("Invalid file path or file does not exist.");
        //    }

        //    if (!fetchedSuccessfully)
        //    {
        //        Console.WriteLine($"Failed to fetch data for key: {key}");
        //    }

        //    OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(key, fetchedSuccessfully));
        //    return null;
        //}


        //private Stream? ConvertDataPointsToStream(List<BaseData> dataPoints)
        //{
        //    // Example logic to convert data points to a stream if necessary
        //    // This could involve serializing the data points to JSON, CSV, or another format
        //    var memoryStream = new MemoryStream();
        //    using (var writer = new StreamWriter(memoryStream, leaveOpen: true))
        //    {
        //        foreach (var dataPoint in dataPoints)
        //        {
        //            writer.WriteLine(dataPoint.ToString());  // Adjust formatting as needed
        //        }
        //        writer.Flush();
        //        memoryStream.Position = 0;  // Reset stream position to start
        //    }
        //    return memoryStream;
        //}



        public Stream? Fetch(string key)
        {
            Console.WriteLine($"Fetching data for key: {key}");

            // Normalize the key path to ensure consistent separators
            string normalizedKey = key.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar);
            string mapFilePath = normalizedKey;

            // Check if the fetch call is recursive or already in progress
            if (_fetchInProgressKeys.Contains(mapFilePath))
            {
                Console.WriteLine($"Recursive fetch detected for key: {key}. Aborting fetch to avoid recursion.");
                return null; // Prevent recursion
            }

            // Add the key to the set of ongoing fetch operations
            _fetchInProgressKeys.Add(mapFilePath);
            bool fetchedSuccessfully = false;

            try
            {
                

                // Determine the zip file path from the map file or factor file key
                //string zipFilePath = GetZipFilePath(mapFilePath, "daily");

                // Check if the daily zip file exists and try fetching it using ZipDataCacheProvider
                if (!string.IsNullOrEmpty(mapFilePath) && File.Exists(mapFilePath))
                {
                    try
                    {
                        Console.WriteLine($"Opening ZIP file: {mapFilePath} for key: {key}");

                        // Open the ZIP file as a FileStream
                        using (var fileStream = new FileStream(mapFilePath, FileMode.Open, FileAccess.Read, FileShare.Read))
                        {
                            // Fetch the stream from ZipDataCacheProvider
                            Stream? dataStream = _dataCacheProvider.Fetch(mapFilePath); // Assuming ZipDataCacheProvider fetches from path directly

                            // Ensure the stream is properly managed (not disposed) if returned
                            if (dataStream != null)
                            {
                                fetchedSuccessfully = true;
                                return dataStream;  // Return the stream directly
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error processing ZIP file {mapFilePath}: {ex.Message}");
                    }
                }
                else
                {
                    Console.WriteLine($"Invalid file path or file does not exist for key: {key}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error fetching data for key: {key}: {ex.Message}");
            }
            finally
            {
                // Remove the key from the set of ongoing fetch operations
                _fetchInProgressKeys.Remove(mapFilePath);
            }

            // If fetching was not successful, log and notify
            if (!fetchedSuccessfully)
            {
                Console.WriteLine($"Failed to fetch data for key: {mapFilePath}");
            }

            // Trigger event to notify of new data request, even if unsuccessful
            OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(mapFilePath, fetchedSuccessfully));
            return null;
        }


        //public Stream? Fetch(string key)
        //{
        //    Console.WriteLine($"The keys fetched found at: {key}");
        //    bool fetchedSuccessfully = false;
        //    List<Stream> streamsToCombine = new List<Stream>();

        //    // Normalize the key path to ensure consistent separators
        //    string normalizedKey = key.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar);
        //    string mapFilePath = normalizedKey;

        //    // Check if the key indicates interest rate data
        //    if (mapFilePath.Contains("interest-rate", StringComparison.OrdinalIgnoreCase))
        //    {
        //        try
        //        {
        //            string csvFilePath = Path.Combine("qcTrader", "Lean", "Launcher", "bin", "Release", "Data", "alternative", "interest-rate", "usa", "interest-rate.csv");

        //            // Check if the file exists
        //            if (!File.Exists(csvFilePath))
        //            {
        //                Console.WriteLine($"Interest rate file not found: {csvFilePath}");
        //                return null;
        //            }

        //            // Validate the CSV file format before loading data
        //            bool isValid = ValidateCsvFile(csvFilePath);
        //            if (!isValid)
        //            {
        //                Console.WriteLine("CSV file format is invalid. Aborting data fetch.");
        //                return null;
        //            }

        //            // Initialize a variable to hold the first interest rate value
        //            decimal firstInterestRate;

        //            // Use the static InterestRateProvider method to fetch the interest rate data
        //            Dictionary<DateTime, decimal> interestRates = InterestRateProvider.FromCsvFile(mapFilePath, out firstInterestRate);

        //            if (interestRates == null || interestRates.Count == 0)
        //            {
        //                Console.WriteLine("No interest rate data found or data is incomplete.");
        //                return null;
        //            }



        //            fetchedSuccessfully = true;
        //            Console.WriteLine($"Interest rate data successfully fetched. First rate: {firstInterestRate}");

        //            // Handle the interestRates dictionary as needed
        //            // For demonstration, you might convert it to a Stream, log it, or process it directly.
        //            OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(csvFilePath, fetchedSuccessfully));
        //            Stream? interestDataStream = _zipCacheProvider.Fetch(csvFilePath);
        //            streamsToCombine.Add(interestDataStream);

        //        }
        //        catch (Exception ex)
        //        {
        //            Console.WriteLine($"Error loading interest rates from CSV: {ex.Message}");
        //            return null;
        //        }
        //    }

        //    // Determine the zip file path from the map file or factor file key
        //    string zipFilePath = GetZipFilePath(mapFilePath, "daily");

        //    // Check if the daily zip file exists and try fetching it using ZipDataCacheProvider
        //    if (!string.IsNullOrEmpty(zipFilePath) && File.Exists(zipFilePath))
        //    {
        //        Stream? dataStream = _zipCacheProvider.Fetch(zipFilePath);

        //        if (dataStream != null && dataStream.CanRead)
        //        {
        //            // Check if the stream can seek; if not, wrap it in a BufferedStream
        //            if (!dataStream.CanSeek)
        //            {
        //                dataStream = new BufferedStream(dataStream);
        //            }

        //            // Ensure the stream is positioned at the start
        //            if (dataStream.CanSeek)
        //            {
        //                try
        //                {
        //                    dataStream.Position = 0;  // Reset the stream position to the beginning
        //                }
        //                catch (Exception ex)
        //                {
        //                    Console.WriteLine($"Failed to reset stream position: {ex.Message}");
        //                    dataStream.Dispose();  // Safely dispose the stream if it can't be reset
        //                    return null;
        //                }
        //            }

        //            // Confirm the stream is still open and not disposed
        //            try
        //            {
        //                int testByte = dataStream.ReadByte();  // Test read
        //                if (testByte == -1)
        //                {
        //                    Console.WriteLine("Stream is at the end or cannot be read.");
        //                    dataStream.Dispose();
        //                    return null;
        //                }
        //                // Reset again after the test read if necessary
        //                if (dataStream.CanSeek)
        //                {
        //                    dataStream.Position = 0;
        //                }
        //            }
        //            catch (ObjectDisposedException)
        //            {
        //                Console.WriteLine("Stream was disposed before reading could occur.");
        //                return null;
        //            }
        //            catch (IOException ioEx)
        //            {
        //                Console.WriteLine($"IOException occurred: {ioEx.Message}");
        //                return null;
        //            }
        //            //fetchedSuccessfully = true;
        //            Console.WriteLine("Data successfully fetched from ZipCacheProvider for daily frequency.");
        //            OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(zipFilePath, fetchedSuccessfully));
        //            //streamsToCombine.Add(dataStream);

        //            // Process the fetched data using SubscriptionDataSourceReader
        //            var dataSource = new SubscriptionDataSource(zipFilePath, SubscriptionTransportMedium.LocalFile, FileFormat.Csv);
        //            var config = new SubscriptionDataConfig(
        //                typeof(TradeBar),
        //                Symbol.Create(ExtractSymbolFromKey(mapFilePath), SecurityType.Equity, Market.USA),
        //                Resolution.Daily,
        //                TimeZones.NewYork,
        //                TimeZones.NewYork,
        //                false, false, false);

        //            var date = DateTime.UtcNow.Date;
        //            var factory = new TradeBar();  // Adjust the factory as per your data type

        //            var reader = SubscriptionDataSourceReader.ForSource(
        //                dataSource,
        //                _dataCacheProvider,
        //                config,
        //                date,
        //                isLiveMode: false,
        //                factory,
        //                _dataProvider,
        //                _objectStore
        //            );

        //            var dataPoints = reader.Read(dataSource).ToList(); // Process the data
        //            Console.WriteLine($"Processed {dataPoints.Count} data points from the source.");
        //            streamsToCombine.Add(dataStream);
        //        }
        //        else
        //        {
        //            Console.WriteLine("Failed to fetch data stream or the stream cannot be read.");
        //        }
        //    }




        //    // If there are streams to combine, merge them into a single stream
        //    if (streamsToCombine.Count > 0)
        //    {
        //        // Combine all streams into a single MemoryStream
        //        var combinedStream = new MemoryStream();
        //        foreach (var stream in streamsToCombine)
        //        {
        //            stream.CopyTo(combinedStream);
        //            stream.Dispose(); // Dispose individual streams to free resources
        //        }
        //        combinedStream.Position = 0; // Reset the position to the beginning for reading
        //        return combinedStream;
        //    }

        //    if (!fetchedSuccessfully)
        //    {
        //        Console.WriteLine($"Failed to fetch data for key: {key}");
        //    }



        //    //Trigger event to notify of new data request, even if unsuccessful
        //    OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(key, fetchedSuccessfully));
        //    return null;
        //}

        private bool ValidateCsvFile(string filePath)
        {
            int lineNumber = 0;
            foreach (var line in File.ReadLines(filePath))
            {
                lineNumber++;
                if (lineNumber == 1) continue; // Skip header

                // Check if the line is empty or contains only whitespace
                if (string.IsNullOrWhiteSpace(line))
                {
                    Console.WriteLine($"Skipped empty or whitespace-only line at {lineNumber}.");
                    continue; // Skip empty lines
                }

                // Split the line by comma
                var values = line.Split(',');

                // Check if the line has exactly two values (date and rate)
                if (values.Length != 2)
                {
                    Console.WriteLine($"Invalid format at line {lineNumber}: {line}. Expected exactly 2 columns but found {values.Length}.");
                    return false; // Invalid format
                }

                // Validate date format
                if (!DateTime.TryParseExact(values[0], "dd-MM-yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None, out _))
                {
                    Console.WriteLine($"Invalid date format at line {lineNumber}: {values[0]}. Expected format 'dd-MM-yyyy'.");
                    return false; // Invalid date format
                }

                // Validate interest rate format
                if (!decimal.TryParse(values[1], NumberStyles.Any, CultureInfo.InvariantCulture, out _))
                {
                    Console.WriteLine($"Invalid interest rate format at line {lineNumber}: {values[1]}. Expected a valid decimal number.");
                    return false; // Invalid rate format
                }
            }
            Console.WriteLine("CSV file validated successfully.");
            return true;
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
