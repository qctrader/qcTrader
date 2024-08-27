{
    "environment": "backtesting",
    "algorithm-language": "Python",
    "data-folder": "qcTrader/Lean/Launcher/bin/Release\\Data",
    "debugging": false,
    "debugging-method": "LocalCmdLine",
    "log-handler": "ConsoleLogHandler",
    "messaging-handler": "QuantConnect.Messaging.Messaging",
    "job-queue-handler": "QuantConnect.Queues.JobQueue",
    "api-handler": "QuantConnect.Api.Api",
    "map-file-provider": "QuantConnect.Data.Auxiliary.LocalDiskMapFileProvider",
    "factor-file-provider": "QuantConnect.Data.Auxiliary.LocalDiskFactorFileProvider",
    "data-provider": "QuantConnect.Lean.Engine.DataFeeds.DefaultDataProvider",
    "object-store": "QuantConnect.Lean.Engine.Storage.LocalObjectStore",
    "data-aggregator": "QuantConnect.Lean.Engine.DataFeeds.AggregationManager",
    "symbol-minute-limit": 10000,
    "symbol-second-limit": 10000,
    "symbol-tick-limit": 10000,
    "show-missing-data-logs": true,
    "maximum-warmup-history-days-look-back": 5,
    "maximum-data-points-per-chart-series": 1000000,
    "maximum-chart-series": 30,
    "force-exchange-always-open": false,
    "transaction-log": "",
    "reserved-words-prefix": "@",
    "job-user-id": "0",
    "api-access-token": "",
    "job-organization-id": "",
    "log-level": "trace",
    "debug-mode": true,
    "results-destination-folder": "qcTrader/Lean/Launcher/bin/Release\\Results",
    "mute-python-library-logging": "False",
    "close-automatically": true,
    "python-additional-paths": [],
    "environments": {
        "backtesting": {
            "live-mode": false,
            "setup-handler": "QuantConnect.Lean.Engine.Setup.BacktestingSetupHandler",
            "result-handler": "QuantConnect.Lean.Engine.Results.BacktestingResultHandler",
            "data-feed-handler": "QuantConnect.Lean.Engine.DataFeeds.FileSystemDataFeed",
            "real-time-handler": "QuantConnect.Lean.Engine.RealTime.BacktestingRealTimeHandler",
            "history-provider": [
                "QuantConnect.Lean.Engine.HistoricalData.SubscriptionDataReaderHistoryProvider"
            ],
            "transaction-handler": "QuantConnect.Lean.Engine.TransactionHandlers.BacktestingTransactionHandler"
        }
    },
    "algorithm-type-name": "BacktestingAlgorithm.py",
    "algorithm-location": "qcTrader/Lean/Algorithm.Python",
    "parameters": {
        "weighting_scheme": "market_cap",
        "rebalancing_frequency": "monthly",
        "market_caps": "{\"AAPL\": 3436202642196, \"MSFT\": 3144993500241, \"GOOGL\": 969430108231, \"AMZN\": 1888840584893, \"TSLA\": 705919572515, \"JNJ\": 386313864929, \"PG\": 400988885176}",
        "volatilities": "{\"AAPL\": 0.01429610035133022, \"MSFT\": 0.01250539724436889, \"GOOGL\": 0.017528420249807768, \"AMZN\": 0.017790672344677006, \"TSLA\": 0.034150240896718434, \"JNJ\": 0.009692984381120687, \"PG\": 0.00943202747844786}",
        "portfolio": "{\"initial_capital\": \"2000000.00\", \"assets\": [\"AAPL\", \"MSFT\", \"GOOGL\", \"AMZN\", \"TSLA\", \"JNJ\", \"PG\"]}"
    }
}