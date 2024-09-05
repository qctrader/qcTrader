using System.Reflection;

var assembly = Assembly.LoadFrom("D:\\qcTrader-par1\\qcTrader\\qcTrader\\Lean\\Launcher\\composer\\CustomDataProvider.dll");
var type = assembly.GetType("CustomDataProvider.CsvDataProvider");

if (type == null)
{
    Console.WriteLine("Type not found");
}
else
{
    Console.WriteLine("Type loaded successfully");
}
