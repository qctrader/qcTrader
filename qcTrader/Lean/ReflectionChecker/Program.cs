using System;
using System.Reflection;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length != 2)
        {
            Console.WriteLine("Usage: ReflectionChecker <assemblyPath> <typeName>");
            return;
        }

        string assemblyPath = args[0];
        string typeName = args[1];

        CheckAssembly(assemblyPath, typeName);
    }

    static void CheckAssembly(string assemblyPath, string typeName)
    {
        try
        {
            Assembly assembly = Assembly.LoadFrom(assemblyPath);
            Type type = assembly.GetType(typeName);

            if (type != null)
            {
                Console.WriteLine($"Type '{typeName}' found in assembly '{assemblyPath}'.");
            }
            else
            {
                Console.WriteLine($"Type '{typeName}' not found in assembly '{assemblyPath}'.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}

