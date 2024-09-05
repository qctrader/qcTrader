//using System;
//using System.ComponentModel.Composition.Hosting;
//using System.ComponentModel.Composition;
//using System.Reflection;
//using QuantConnect.Interfaces;

//class Program
//{
//    static void Main(string[] args)
//    {
//        string assemblyPath = @"D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\composer\CustomDataProvider.dll";

//        try
//        {
//            var catalog = new AssemblyCatalog(assemblyPath);
//            var container = new CompositionContainer(catalog);

//            // Attempt to retrieve the exported IDataProvider
//            var provider = container.GetExportedValue<IDataProvider>("CustomDataProvider.CsvDataProvider");

//            if (provider != null)
//            {
//                Console.WriteLine("Exported IDataProvider successfully loaded.");
//                // Optional: Test the Fetch method
//                using (var stream = provider.Fetch("your_file_path"))
//                {
//                    if (stream != null)
//                    {
//                        Console.WriteLine("Data fetched successfully.");
//                    }
//                    else
//                    {
//                        Console.WriteLine("Data fetch failed.");
//                    }
//                }
//            }
//            else
//            {
//                Console.WriteLine("IDataProvider not found.");
//            }
//        }
//        catch (CompositionException ex)
//        {
//            Console.WriteLine($"Composition error: {ex.Message}");
//        }
//        catch (ReflectionTypeLoadException ex)
//        {
//            Console.WriteLine("ReflectionTypeLoadException: " + ex.Message);
//            foreach (var loaderException in ex.LoaderExceptions)
//            {
//                Console.WriteLine(loaderException.Message);
//            }
//        }
//        catch (Exception ex)
//        {
//            Console.WriteLine($"An error occurred: {ex.Message}");
//        }
//    }
//}


using QuantConnect.Interfaces;
using System;
using System.ComponentModel.Composition;
using System.ComponentModel.Composition.Hosting;
using System.Linq;

class Program
{
    static void Main(string[] args)
    {
        string assemblyPath = @"D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\composer\CustomDataProvider.dll";
        var catalog = new AssemblyCatalog(assemblyPath);
        var container = new CompositionContainer(catalog);

        // List all available exports for debugging
        var exports = catalog.Parts.SelectMany(part => part.ExportDefinitions).ToList();

        foreach (var export in exports)
        {
            Console.WriteLine($"Export: {export.ContractName}");
        }

        try
        {
            var provider = container.GetExportedValue<IDataProvider>("CustomDataProvider.CsvDataProvider");
            Console.WriteLine("Exported IDataProvider successfully loaded.");
        }
        catch (CompositionException ex)
        {
            Console.WriteLine($"Composition error: {ex.Message}");
        }
    }
}

