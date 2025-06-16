using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.Json;

public class LogEvent
{
    public string Source { get; set; }
    public DateTime DateTime { get; set; }
    public int Id { get; set; }
    public string Type { get; set; }
    public string Message { get; set; }
}

public class LogReader
{
    public IEnumerable<LogEvent> ReadEvents(int maxEvents)
    {
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
        {
            return ReadWindowsEvents(maxEvents);
        }
        else
        {
            return ReadUnixEvents(maxEvents);
        }
    }

    private IEnumerable<LogEvent> ReadWindowsEvents(int maxEvents)
    {
        var events = new List<LogEvent>();
        using (EventLog eventLog = new EventLog("System"))
        {
            int total = eventLog.Entries.Count;
            int count = 0;
            // Percorre do mais recente para o mais antigo
            for (int i = total - 1; i >= 0 && count < maxEvents; i--)
            {
                var entry = eventLog.Entries[i];
                events.Add(new LogEvent
                {
                    Source = entry.Source,
                    DateTime = entry.TimeGenerated,
                    Id = entry.InstanceId.GetHashCode(),
                    Type = entry.EntryType.ToString(),
                    Message = entry.Message
                });
                count++;
            }
        }
        return events;
    }

    private IEnumerable<LogEvent> ReadUnixEvents(int maxEvents)
    {
        var events = new List<LogEvent>();
        string logPath = File.Exists("/var/log/syslog") ? "/var/log/syslog" : "/var/log/messages";
        if (!File.Exists(logPath))
            return events;

        int count = 0;
        foreach (var line in File.ReadLines(logPath))
        {
            events.Add(new LogEvent
            {
                Source = "syslog",
                DateTime = DateTime.Now, // Parsing real date/time would require more logic
                Id = 0,
                Type = "Info",
                Message = line
            });
            count++;
            if (count >= maxEvents) break;
        }
        return events;
    }
}

public class Program
{
    public static void Main(string[] args)
    {
        int maxEvents = int.MaxValue;
        if (args.Length > 0 && int.TryParse(args[0], out int n))
            maxEvents = n;

        var reader = new LogReader();
        var events = reader.ReadEvents(maxEvents);
        string json = JsonSerializer.Serialize(events);
        Console.WriteLine(json);
    }
}