using System;
using System.Collections.Concurrent;
using System.Globalization;
using System.IO;
using System.Threading;
using CsvHelper;
using CsvHelper.Configuration;
using QuantConnect.Data;
using QuantConnect.Interfaces;
using QuantConnect.Lean.Engine.DataFeeds;
using QuantConnect.Packets;
using QuantConnect.Data.Market;
using QuantConnect.Configuration;  // Import for accessing configuration settings

namespace CustomDataFeeds
{
    public class CsvDataFeed : IDataFeed
    {
        private bool _exitTriggered;
        private IAlgorithm _algorithm;
        private BlockingCollection<TradeBar> _dataQueue = new BlockingCollection<TradeBar>();
        private string _dataPath;

        public void Initialize(IAlgorithm algorithm, AlgorithmNodePacket job, IDataProvider dataProvider, IDataCacheProvider dataCacheProvider, IDataChannelProvider dataChannelProvider)
        {
            _algorithm = algorithm;

            // Retrieve the data path from the configuration set by the Python algorithm
            _dataPath = GetDynamicDataPath();

            // Load data from the CSV file specified by the dynamic path
            LoadCsvData(_dataPath);
        }

        public void Run()
        {
            // Main loop to push data to Lean
            while (!_exitTriggered)
            {
                try
                {
                    // Supply data from the queue to Lean
                    if (_dataQueue.TryTake(out var data, 1000))
                    {
                        // Push data into Lean's data stream
                        _algorithm.OnData(new Slice(data.Time, new[] { data }));
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in data feed: {ex.Message}");
                }
            }
        }

        public void Exit()
        {
            // Clean up resources
            _exitTriggered = true;
            _dataQueue.CompleteAdding();
        }

        private void LoadCsvData(string filePath)
        {
            try
            {
                using (var reader = new StreamReader(filePath))
                using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
                {
                    HasHeaderRecord = true, // Adjust if your CSV does not have headers
                }))
                {
                    // Define the CSV mapping or let CsvHelper auto-map based on headers
                    csv.Context.RegisterClassMap<TradeBarMap>(); // Map to TradeBar
                    var records = csv.GetRecords<TradeBar>();

                    foreach (var record in records)
                    {
                        _dataQueue.Add(record); // Add to the queue for Lean to consume
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading CSV data: {ex.Message}");
            }
        }

        private string GetDynamicDataPath()
        {
            // Fetch the path parameter set in the algorithm's configuration
            string dataPath = Config.Get("custom-data-path", "equity/usa/daily/msft.csv"); // Default if not set
            string baseDirectory = AppDomain.CurrentDomain.BaseDirectory; // Base directory of the running application
            return Path.Combine(baseDirectory, dataPath); // Combine to form the full path
        }
    }

    public class TradeBarMap : ClassMap<TradeBar>
    {
        public TradeBarMap()
        {
            Map(m => m.Time).Name("date").TypeConverterOption.Format("yyyyMMdd"); // Adjust based on CSV format
            Map(m => m.Open).Name("open");
            Map(m => m.High).Name("high");
            Map(m => m.Low).Name("low");
            Map(m => m.Close).Name("close");
            Map(m => m.Volume).Name("volume");
            Map(m => m.Symbol).Constant(Symbol.Create("MSFT", SecurityType.Equity, Market.USA)); // Fixed symbol
        }
    }
}

