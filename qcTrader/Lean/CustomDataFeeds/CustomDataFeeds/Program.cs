using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using CsvHelper;
using CsvHelper.Configuration;
using QuantConnect.Data;
using QuantConnect.Data.Market;
using QuantConnect.Interfaces;
using QuantConnect.Lean.Engine.DataFeeds;
using QuantConnect.Packets;
using QuantConnect.Configuration;
using QuantConnect.Util;
using QuantConnect.Data.UniverseSelection;
using QuantConnect.Lean.Engine.Results;
using QuantConnect;
using QuantConnect.Lean.Engine.DataFeeds.Enumerators;


namespace CustomDataFeeds
{
    public class CsvDataFeed : IDataFeed
    {
        private bool _exitTriggered;
        private IAlgorithm _algorithm;
        private BlockingCollection<TradeBar> _dataQueue = new BlockingCollection<TradeBar>();
        private string _dataPath;
        private IDataProvider _dataProvider;

        public void Initialize(
            IAlgorithm algorithm,
            AlgorithmNodePacket job,
            IResultHandler resultHandler,
            IMapFileProvider mapFileProvider,
            IFactorFileProvider factorFileProvider,
            IDataProvider dataProvider,
            IDataFeedSubscriptionManager subscriptionManager,
            IDataFeedTimeProvider dataFeedTimeProvider,
            IDataChannelProvider dataChannelProvider)
        {
            _algorithm = algorithm;
            _dataProvider = dataProvider;
            _dataPath = GetDynamicDataPath();
        }

        public void Run()
        {
            // Main loop to push data to Lean
            while (!_exitTriggered)
            {
                try
                {
                    // Supply data from the queue to Lean
                    if (_dataQueue.TryTake(out var tradeBar, 1000))
                    {
                        // Create a dictionary of TradeBars with the correct symbol
                        var tradeBars = new TradeBars
                        {
                            { tradeBar.Symbol, tradeBar }
                        };

                        var utcTime = tradeBar.EndTime.ConvertToUtc(_algorithm.TimeZone);

                        // Create a Slice object with the TradeBars
                        var slice = new Slice(tradeBar.EndTime, (IEnumerable<BaseData>)tradeBars, utcTime);

                        // Pass the Slice to the algorithm's OnData method
                        _algorithm.OnData(slice);
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
            _exitTriggered = true;
            _dataQueue.CompleteAdding();
        }

        private string GetDynamicDataPath()
        {
            string dataPath = Config.Get("custom-data-path", "Data/equity/usa/daily/msft.csv");
            string baseDirectory = AppDomain.CurrentDomain.BaseDirectory;
            return Path.Combine(baseDirectory, dataPath);
        }

        public Subscription CreateSubscription(SubscriptionRequest request)
        {
            var config = request.Configuration;
            var enumerator = GetCsvEnumerator(_dataPath, config);

            var timeProvider = new ManualTimeProvider(_algorithm.UtcTime);
            timeProvider.SetCurrentTime(_algorithm.UtcTime); // Initialize with current UTC time

            // Use EnumeratorFactory to create a synchronized enumerator
            var synchronizedEnumerator = ISubscriptionEnumeratorFactory.Synchronize(timeProvider, enumerator);

            // Create the subscription object
            var subscription = new Subscription(request, synchronizedEnumerator, request.Security, request.EndTimeUtc);
            return subscription;
        }

        private IEnumerator<BaseData> GetCsvEnumerator(string filePath, SubscriptionDataConfig config)
        {
            using (var reader = new StreamReader(filePath))
            using (var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true, // Adjust if your CSV does not have headers
            }))
            {
                csv.Context.RegisterClassMap<TradeBarMap>();

                while (csv.Read())
                {
                    var record = csv.GetRecord<TradeBar>();
                    record.Symbol = config.Symbol; // Set the symbol for each TradeBar
                    yield return record;
                }
            }
        }

        public void RemoveSubscription(Subscription subscription)
        {
            Console.WriteLine($"Removing subscription for: {subscription.Configuration.Symbol}");
        }

        public bool IsActive
        {
            get { return !_exitTriggered; }
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
            Map(m => m.Symbol).Constant(Symbol.Create("MSFT", SecurityType.Equity, Market.USA)); // Set symbol explicitly
        }
    }
}
