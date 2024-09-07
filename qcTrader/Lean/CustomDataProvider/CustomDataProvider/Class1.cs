using System;
using System.IO;
using QuantConnect.Interfaces;
using System.ComponentModel.Composition;
using QuantConnect.Configuration;
using System.Collections.Generic;
using System.Linq;
using System.IO.Compression;
using QuantConnect.Lean.Engine.DataFeeds;


namespace CustomDataProvider
{
    [Export(typeof(IDataProvider))]
    [Export("CustomDataProvider.CsvDataProvider", typeof(IDataProvider))]
    public class CsvDataProvider : IDataProvider
    {
        public event EventHandler<QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs>? NewDataRequest;
        private readonly ZipDataCacheProvider _zipCacheProvider;
        
        public CsvDataProvider()
        {
            _zipCacheProvider = new ZipDataCacheProvider(new DefaultDataProvider());
            //_downloaderDataProvider = new DownloaderDataProvider();
        }

        
        public Stream? Fetch(string key)
        {
            Console.WriteLine($"The keys fetched found at: {key}");
            bool fetchedSuccessfully = false;

            // Normalize the key path to ensure consistent separators
            string normalizedKey = key.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar);
            string mapFilePath = normalizedKey;

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

            //Trigger event to notify of new data request, even if unsuccessful
           OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(key, fetchedSuccessfully));
            return null;
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
