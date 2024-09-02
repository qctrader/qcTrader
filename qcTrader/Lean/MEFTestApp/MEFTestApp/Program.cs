using System;
using System.ComponentModel.Composition;
using System.ComponentModel.Composition.Hosting;
using System.IO;
using System.Reflection;

namespace MEFTestApp
{
    class Program
    {
        [Import(typeof(YFinanceDataProvider.PythonRunner))]
        public YFinanceDataProvider.PythonRunner Runner { get; set; }

        static void Main(string[] args)
        {
            var program = new Program();
            program.Compose();

            if (program.Runner != null)
            {
                program.Runner.RunPythonScript("Test script content");
                Console.WriteLine("PythonRunner loaded and method executed successfully.");
            }
            else
            {
                Console.WriteLine("Failed to load PythonRunner.");
            }

            Console.ReadLine();
        }

        private void Compose()
        {
            try
            {
                // Explicitly load the specific assembly
                string assemblyPath = @"D:\qcTrader-par1\qcTrader\qcTrader\Lean\Launcher\composer\YFinanceDataProvider.dll";
                var catalog = new AssemblyCatalog(assemblyPath);

                // Create a container to manage the parts
                var container = new CompositionContainer(catalog);

                // Compose the parts into the current class (this)
                container.ComposeParts(this);

                Console.WriteLine("Composition succeeded.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error during composition: {ex.Message}");
            }
        }
    }
}

