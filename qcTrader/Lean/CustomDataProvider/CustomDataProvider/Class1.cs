using System;
using System.IO;
using QuantConnect.Interfaces;
using System.ComponentModel.Composition;
using QuantConnect.Configuration;
using System.Collections.Generic;
using System.Linq;
using System.IO.Compression;


namespace CustomDataProvider
{
    [Export(typeof(IDataProvider))]
    [Export("CustomDataProvider.CsvDataProvider", typeof(IDataProvider))]
    public class CsvDataProvider : IDataProvider
    {
        public event EventHandler<QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs>? NewDataRequest;

        private readonly string _baseDirectory;

        public CsvDataProvider()
        {
            // This constructor is invoked during Lean engine initialization
            _baseDirectory = Config.Get("custom-data-provider-parameters.data_path");
            Console.WriteLine($"Dynamic Data Path: {_baseDirectory}");
        }

        //[ImportingConstructor]
        //public CsvDataProvider([Import("BaseDirectory")] string baseDirectory)
        //{
        //    _baseDirectory = baseDirectory;
        //}

        public Stream? Fetch(string key)
        {
            bool fetchedSuccessfully = false;

            // Normalize the key path to ensure consistent separators
            string normalizedKey = key.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar);
            string mapFilePath = normalizedKey;

            // Determine the zip file path from the map file or factor file key
            string zipFilePath = GetZipFilePath(mapFilePath);

            if (string.IsNullOrEmpty(zipFilePath))
            {
                Console.WriteLine("Could not determine zip file path.");
                return null;
            }

            Console.WriteLine($"Attempting to open zip file at: {zipFilePath}");

            try
            {
                // Add logging to confirm the zip file existence check
                if (File.Exists(zipFilePath))
                {
                    Console.WriteLine($"Zip file exists: {zipFilePath}");
                    try
                    {
                        using (ZipArchive archive = ZipFile.OpenRead(zipFilePath))
                        {
                            Console.WriteLine($"Successfully opened zip file: {zipFilePath}");
                            var csvEntry = archive.Entries.FirstOrDefault(entry => entry.Name.EndsWith(".csv", StringComparison.OrdinalIgnoreCase));
                            if (csvEntry != null)
                            {
                                Console.WriteLine($"CSV file found in zip: {csvEntry.Name}");
                                using (Stream csvStream = csvEntry.Open())
                                {
                                    // Reading and parsing the CSV
                                    using (StreamReader reader = new StreamReader(csvStream))
                                    {
                                        var data = ParseCsv(reader);
                                        if (!string.IsNullOrEmpty(data))
                                        {
                                            fetchedSuccessfully = true;
                                            Console.WriteLine("Data successfully read from CSV.");
                                            return new MemoryStream(System.Text.Encoding.UTF8.GetBytes(data));
                                        }
                                        else
                                        {
                                            Console.WriteLine("CSV file was read but contained no usable data.");
                                        }
                                    }
                                }
                            }
                            else
                            {
                                Console.WriteLine("CSV file not found in the zip archive.");
                            }
                        }
                    }
                    catch (InvalidDataException ex)
                    {
                        Console.WriteLine($"Corrupted zip file: {zipFilePath}. Error: {ex.Message}");
                    }
                }
                else
                {
                    Console.WriteLine("Zip file not found at expected location.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred while opening or reading the zip file: {ex.Message}");
                Console.WriteLine($"Stack Trace: {ex.StackTrace}");
            }
            finally
            {
                Console.WriteLine("Entering finally block.");
                OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(zipFilePath, fetchedSuccessfully));
            }

            return null;
        }


        private string GetZipFilePath(string mapFilePath)
        {
            // Normalize path separators and replace "map_files" with "daily"
            string normalizedPath = mapFilePath.Replace('\\', Path.DirectorySeparatorChar)
                                               .Replace('/', Path.DirectorySeparatorChar);

            // Replace "map_files" with "daily" to point to the correct directory
            string directory = Path.GetDirectoryName(normalizedPath) ?? string.Empty;
            directory = directory.Replace("map_files", "daily");

            // Construct the zip file name using the map file name
            string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(normalizedPath);
            string zipFileName = fileNameWithoutExtension + ".zip";

            // Combine the modified directory with the zip file name
            string zipFilePath = Path.Combine(directory, zipFileName);

            // Log the constructed zip path and verify its existence
            Console.WriteLine($"Constructed Zip Path: {zipFilePath}");
            if (File.Exists(zipFilePath))
            {
                Console.WriteLine($"Zip file found at: {zipFilePath}");
                return zipFilePath;
            }
            else
            {
                Console.WriteLine($"Zip file not found at: {zipFilePath}");
                return string.Empty;
            }
        }
        private string ParseCsv(StreamReader reader)
        {
            var result = new List<string>();

            string? line;

            // Assuming the CSV follows a consistent order and the columns are:
            // 0: Open, 1: High, 2: Low, 3: Close, 4: Volume
            // Adjust indices if the order is different
            int openIndex = 0;
            int highIndex = 1;
            int lowIndex = 2;
            int closeIndex = 3;
            int volumeIndex = 4;

            while ((line = reader.ReadLine()) != null)
            {
                var columns = line.Split(',');

                // Ensure there are enough columns in the line
                if (columns.Length > Math.Max(Math.Max(closeIndex, highIndex), Math.Max(lowIndex, Math.Max(openIndex, volumeIndex))))
                {
                    // Extract the required values by position
                    var open = columns[openIndex];
                    var high = columns[highIndex];
                    var low = columns[lowIndex];
                    var close = columns[closeIndex];
                    var volume = columns[volumeIndex];

                    result.Add($"{close},{high},{low},{open},{volume}");
                }
                else
                {
                    Console.WriteLine("Incomplete row encountered in CSV.");
                }
            }

            // Join all rows into a single string
            return string.Join(Environment.NewLine, result);
        }

        protected virtual void OnNewDataRequest(QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs e)
        {
            NewDataRequest?.Invoke(this, e);
        }
    }
}
