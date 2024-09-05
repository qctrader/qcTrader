
using QuantConnect.Interfaces;
using System.ComponentModel.Composition;

namespace CustomDataProvider
{
    [Export(typeof(IDataProvider))]
    [Export("CustomDataProvider.CsvDataProvider", typeof(IDataProvider))]
    public class CsvDataProvider : IDataProvider
    {
        // Declare the event as per the interface requirements
        public event EventHandler<QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs>? NewDataRequest;

        private readonly string _baseDirectory;

        [ImportingConstructor]
        public CsvDataProvider([Import("BaseDirectory")] string baseDirectory)
        {
            _baseDirectory = baseDirectory;
        }

        //public Stream? Fetch(string key)
        //{
        //    // Use the base directory directly as the file path
        //    string filePath = Path.Combine(_baseDirectory, key);

        //    bool fetchedSuccessfully = File.Exists(filePath);

        //    // Use the correct EventArgs from QuantConnect.Interfaces with path and success status
        //    OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(filePath, fetchedSuccessfully));

        //    // Open and return the file stream if the file exists
        //    if (fetchedSuccessfully)
        //    {
        //        return new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read);
        //    }

        //    // Return null if the file is not found
        //    return null;
        //}

        public Stream? Fetch(string key)
        {
            // Combine the base directory with the key to form the full file path
            string filePath = Path.Combine(_baseDirectory, key);

            bool fetchedSuccessfully = true;

            try
            {
                // Fetch the file stream if the file exists
                return new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read);
            }
            catch (Exception ex)
            {
                fetchedSuccessfully = false;
                if (ex is DirectoryNotFoundException || ex is FileNotFoundException)
                {
                    // Return null if the file is not found
                    return null;
                }
                // Log or handle other exceptions as needed
                throw;
            }
            finally
            {
                // Raise the NewDataRequest event
                OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(filePath, fetchedSuccessfully));
            }
        }

        // Protected method to safely raise the event
        protected virtual void OnNewDataRequest(QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs e)
        {
            // Safely invoke the event using the correct EventArgs type
            NewDataRequest?.Invoke(this, e);
        }
    }
}
