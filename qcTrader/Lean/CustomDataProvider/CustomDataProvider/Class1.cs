using System;
using System.IO;
using QuantConnect.Interfaces;
using System.ComponentModel.Composition;
using QuantConnect.Configuration;

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
            bool fetchedSuccessfully = true;
            Console.WriteLine($"Key Received: {key}");
            string filePath = Path.Combine(_baseDirectory, key); // Combine base directory with key

            Console.WriteLine($"Attempting to open file at: {_baseDirectory}");

            try
            {
                // Attempt to open the file stream
                return new FileStream(_baseDirectory, FileMode.Open, FileAccess.Read, FileShare.Read);
            }
            catch (Exception ex)
            {
                fetchedSuccessfully = false;
                if (ex is DirectoryNotFoundException || ex is FileNotFoundException)
                {
                    Console.WriteLine("File not found or could not be opened.");
                    return null;
                }

                Console.WriteLine($"An error occurred: {ex.Message}");
                throw;
            }
            finally
            {
                // Raise the NewDataRequest event
                OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(filePath, fetchedSuccessfully));
            }
        }

        protected virtual void OnNewDataRequest(QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs e)
        {
            NewDataRequest?.Invoke(this, e);
        }
    }
}
