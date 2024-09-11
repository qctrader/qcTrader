using System;
using System.IO;
using QuantConnect.Interfaces;
using System.ComponentModel.Composition;
using QuantConnect.Configuration;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.IO.Compression;
using QuantConnect.Data;
using QuantConnect.Data.Custom;
using QuantConnect.Util;
using QuantConnect.Lean.Engine.DataFeeds;
using QuantConnect.Data.Market;
using QuantConnect;
using QuantConnect.Storage;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using System.Text.Json;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Ionic.Zip;



namespace CustomDataProvider
{
    [Export(typeof(DefaultDataProvider))]
    [Export("CustomDataProvider.CsvDataProvider", typeof(DefaultDataProvider))]
    public class CsvDataProvider : DefaultDataProvider
    {
        public event EventHandler<QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs>? NewDataRequest;
        private readonly HashSet<string> _fetchInProgressKeys = new HashSet<string>();

       // private readonly IDataProvider _defaultDataProvider = new DefaultDataProvider();

       // public CsvDataProvider(IDataProvider _defaultDataProvider)
       //: base(_defaultDataProvider)
       // {
       // }



        public override Stream Fetch(string key)
        {
            //string normalizedPath = key.Replace('\\', Path.DirectorySeparatorChar)
            //                      .Replace('/', Path.DirectorySeparatorChar);
            //string normalizedKey = Path.GetFullPath(normalizedPath);
            //Console.WriteLine($"normalizedPath: {normalizedPath}");

            string normalizedKey = Path.GetFullPath(key.Replace('/', Path.DirectorySeparatorChar));
            Console.WriteLine($"Full Path: {normalizedKey}");

            Console.WriteLine($"Current Working Directory: {Environment.CurrentDirectory}");


            Console.WriteLine($"Fetching data for normalized key: {normalizedKey}");
            lock (_fetchInProgressKeys)
            {
                if (_fetchInProgressKeys.Contains(normalizedKey))
                {
                    Console.WriteLine($"Recursive fetch detected for key: {normalizedKey}. Aborting fetch to avoid recursion.");

                    return null; // Prevent recursion
                }

                _fetchInProgressKeys.Add(normalizedKey);
            }

            bool fetchedSuccessfully = false;
            Stream? dataStream = null;

            try
            {
                if (File.Exists(normalizedKey))
                {
                    Console.WriteLine($"File exists at: {normalizedKey}");
                    // Check file extension and handle accordingly
                    if (normalizedKey.EndsWith(".zip", StringComparison.OrdinalIgnoreCase))
                    {
                        try
                        {
                            //dataStream =  new FileStream(FileExtension.ToNormalizedPath(normalizedKey), FileMode.Open, FileAccess.Read, FileShare.Read);
                            //dataStream = _dataCacheProvider.Fetch(normalizedKey);
                            //zipEntries = _dataCacheProvider.GetZipEntries(normalizedKey, null);

                            string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(key);
                            string keyCsv = fileNameWithoutExtension + ".csv";
                            string keyToFetch = normalizedKey + "#" + keyCsv;
                            Console.WriteLine($"File to send: {keyToFetch}");
                            // You can call the base method if you want to reuse the original logic:
                            dataStream = base.Fetch(key);

                            // Add custom behavior here, for example:
                            if (dataStream != null)
                            {
                                Console.WriteLine("CustomDataProvider: Successfully fetched stream from base class.");
                                // You can manipulate the stream here, if needed.
                                fetchedSuccessfully = true;
                            }
                            else
                            {
                                Console.WriteLine("CustomDataProvider: Base class fetch returned null, handling this case in CustomDataProvider.");
                                // Handle the case where the base class returned null, or provide alternative logic.
                            }

                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error fetching ZIP file for key: {normalizedKey}: {ex.Message}");
                        }
                    }
                    //else if (normalizedKey.EndsWith(".csv", StringComparison.OrdinalIgnoreCase))
                    //{
                    //    // Handle CSV files (if needed)
                    //    fetchedSuccessfully = false;
                    //    Console.WriteLine($"Attempting to fetch CSV file for key: {normalizedKey}");
                    //    dataStream = new FileStream(normalizedKey, FileMode.Open, FileAccess.Read);
                    //}
                    //else
                    //{
                    //    Console.WriteLine($"Unsupported file type for key: {normalizedKey}");
                    //    fetchedSuccessfully = false;
                    //    return null;
                    //}

                    //if (dataStream != null)
                    //{
                    //    fetchedSuccessfully = true;
                    //    Console.WriteLine($"Successfully fetched data for key: {normalizedKey}");
                    //    return dataStream;
                    //}
                    //else
                    //{
                    //    Console.WriteLine($"Failed to fetch stream from ZipDataCacheProvider for key: {normalizedKey}");
                    //}
                }
                else
                {
                    Console.WriteLine($"File not found: {normalizedKey}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error fetching data for key: {normalizedKey}: {ex.Message}");
            }
            finally
            {
                // Defer removal of the key to ensure it is only removed once fully processed
                if (fetchedSuccessfully)
                {
                    lock (_fetchInProgressKeys)
                    {
                        Console.WriteLine($"Removing key from in-progress list: {normalizedKey}");
                        _fetchInProgressKeys.Remove(normalizedKey);
                    }
                }

                // Log the fetch status regardless of success or failure
                if (!fetchedSuccessfully)
                {
                    Console.WriteLine($"Failed to fetch data for key: {normalizedKey}");
                }

                // Trigger an event to notify of new data request
                OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(normalizedKey, fetchedSuccessfully));
            }

            return dataStream;

        }
        public void OnNewDataRequest(QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs e)
        {
            // Guard against recursive calls from within event handlers
            if (_fetchInProgressKeys.Contains(e.Path))
            {
                Console.WriteLine($"Prevented recursive fetch call in OnNewDataRequest for {e.Path}");
                return;
            }

            NewDataRequest?.Invoke(this, e);
        }
    }
}
