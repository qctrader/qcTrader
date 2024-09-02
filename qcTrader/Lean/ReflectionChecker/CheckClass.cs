using System;
using System.Reflection;

class Program
{
    static void Main()
    {
        string assemblyPath = @"..\Launcher\composer\YFinanceDataProvider.dll";
        Assembly assembly = Assembly.LoadFrom(assemblyPath);

        // Check if the class exists
        Type type = assembly.GetType("YFinanceDataProvider.PythonRunner");
        
        if (type != null)
        {
            Console.WriteLine("Class found: " + type.FullName);
            
            // Check if the class is public and has a default constructor
            bool hasDefaultConstructor = type.GetConstructor(Type.EmptyTypes) != null;
            Console.WriteLine("Has default constructor: " + hasDefaultConstructor);
        }
        else
        {
            Console.WriteLine("Class not found.");
        }
    }
}
