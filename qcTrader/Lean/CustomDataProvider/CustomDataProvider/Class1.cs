
using QuantConnect.Interfaces;


namespace CustomDataProvider
{
    public class CsvDataProvider : IDataProvider
    {
        // Declare the event as per the interface requirements
        public event EventHandler<QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs>? NewDataRequest;

        private readonly string _baseDirectory;

        public CsvDataProvider(string baseDirectory)
        {
            _baseDirectory = baseDirectory;
        }

        public Stream? Fetch(string key)
        {
            // Use the base directory directly as the file path
            string filePath = _baseDirectory; // Assuming _baseDirectory is the full path to the file

            bool fetchedSuccessfully = File.Exists(filePath);

            // Use the correct EventArgs from QuantConnect.Interfaces with path and success status
            OnNewDataRequest(new QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs(filePath, fetchedSuccessfully));

            // Open and return the file stream if the file exists
            if (fetchedSuccessfully)
            {
                return new FileStream(filePath, FileMode.Open, FileAccess.Read, FileShare.Read);
            }

            // Return null if the file is not found
            return null;
        }

        // Protected method to safely raise the event
        protected virtual void OnNewDataRequest(QuantConnect.Interfaces.DataProviderNewDataRequestEventArgs e)
        {
            // Safely invoke the event using the correct EventArgs type
            NewDataRequest?.Invoke(this, e);
        }
    }
}
