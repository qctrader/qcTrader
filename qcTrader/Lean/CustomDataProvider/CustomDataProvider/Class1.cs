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

        public Stream? Fetch(string key)
        {
            string normalizedPath = key.Replace('\\', Path.DirectorySeparatorChar)
                                  .Replace('/', Path.DirectorySeparatorChar);
            string normalizedKey = Path.GetFullPath(normalizedPath);

            Console.WriteLine($"Original Key: {key}");
            Console.WriteLine($"Normalized Path: {normalizedKey}");
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
                        // Handle ZIP files
                        dataStream = _dataCacheProvider.Fetch(normalizedKey);
                    }
                    else if (normalizedKey.EndsWith(".csv", StringComparison.OrdinalIgnoreCase))
                    {
                        // Handle CSV files (if needed)
                        dataStream = new FileStream(normalizedKey, FileMode.Open, FileAccess.Read);
                    }
                    else
                    {
                        Console.WriteLine($"Unsupported file type for key: {normalizedKey}");
                        fetchedSuccessfully = false;
                        return null;
                    }

                    if (dataStream != null)
                    {
                        fetchedSuccessfully = true;
                        Console.WriteLine($"Successfully fetched data for key: {normalizedKey}");
                        return dataStream;
                    }
                    else
                    {
                        Console.WriteLine($"Failed to fetch stream from ZipDataCacheProvider for key: {normalizedKey}");
                    }
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
                lock (_fetchInProgressKeys)
                {
                    _fetchInProgressKeys.Remove(normalizedKey);
                }
            }

            if (!fetchedSuccessfully)
            {
                Console.WriteLine($"Failed to fetch data for key: {normalizedKey}");
            }

            OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(normalizedKey, fetchedSuccessfully));
            return dataStream;
        }
        protected virtual void OnNewDataRequest(QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs e)
        {
            NewDataRequest?.Invoke(this, e);
        }
    }
}
