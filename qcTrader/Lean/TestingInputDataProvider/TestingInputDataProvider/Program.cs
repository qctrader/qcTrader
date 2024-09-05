
//using CustomDataProvider;  // Ensure this namespace matches where your CsvDataProvider class is defined

//namespace CsvDataProviderTest
//{
//    class Program
//    {
//        static void Main(string[] args)
//        {
//            // Example key (file path) to test
//            string key = "D:\\qcTrader-par1\\qcTrader\\qcTrader\\Lean\\Launcher\\bin\\Release\\Data\\equity\\usa\\daily\\msft.zip";  // Update this with the path to a real or test CSV file

//            // Initialize the CsvDataProvider
//            var dataProvider = new CustomDataProvider.CsvDataProvider();

//            // Call the Fetch method with the test key
//            using (var stream = dataProvider.Fetch(key))
//            {
//                if (stream == null)
//                {
//                    Console.WriteLine("File not found or could not be opened.");
//                }
//                else
//                {
//                    Console.WriteLine("File opened successfully.");

//                    // Optional: Read and display some data from the stream
//                    using (var reader = new StreamReader(stream))
//                    {
//                        string content = reader.ReadLine();  // Read the first line or more as needed
//                        Console.WriteLine($"First line of the file: {content}");
//                    }
//                }
//            }

//            // Keep the console window open
//            Console.WriteLine("Press Enter to exit...");
//            Console.ReadLine();
//        }
//    }
//}


using System.ComponentModel.Composition;
using System.ComponentModel.Composition.Hosting;
using CustomDataProvider;
using QuantConnect.Interfaces;

namespace CsvDataProviderTest
{
    class Program
    {
        static void Main(string[] args)
        {
            // Define the base directory for data
            string baseDirectory = @"D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\bin\Release\Data\equity\usa\daily";

            // Ensure the key is the relative path from baseDirectory
            string key = "msft.zip";  // File name relative to the baseDirectory

            var catalog = new AggregateCatalog();
            catalog.Catalogs.Add(new AssemblyCatalog(typeof(Program).Assembly));  // Current assembly
            catalog.Catalogs.Add(new AssemblyCatalog(typeof(CsvDataProvider).Assembly));  // Specific assembly for CsvDataProvider
            var container = new CompositionContainer(catalog);
            

            // Create a composition batch to add the baseDirectory export
            var batch = new CompositionBatch();
            batch.AddExportedValue("BaseDirectory", baseDirectory);  // Export the baseDirectory value
            container.Compose(batch);  // Compose the batch

            try
            {
                // Retrieve CsvDataProvider to verify MEF import works
                var provider = container.GetExportedValue<IDataProvider>("CustomDataProvider.CsvDataProvider");
                Console.WriteLine("CsvDataProvider loaded successfully with BaseDirectory: " + baseDirectory);

                // Call the Fetch method with the test key
                using (var stream = provider.Fetch(key))
                {
                    if (stream == null)
                    {
                        Console.WriteLine("File not found or could not be opened.");
                    }
                    else
                    {
                        Console.WriteLine("File opened successfully.");

                        // Optional: Read and display some data from the stream
                        using (var reader = new StreamReader(stream))
                        {
                            string content = reader.ReadLine();  // Read the first line or more as needed
                            Console.WriteLine($"First line of the file: {content}");
                        }
                    }
                }
            }
            catch (CompositionException ex)
            {
                Console.WriteLine($"MEF Composition error: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An unexpected error occurred: {ex.Message}");
            }

            // Keep the console window open
            Console.WriteLine("Press Enter to exit...");
            Console.ReadLine();
        }
    }
}


