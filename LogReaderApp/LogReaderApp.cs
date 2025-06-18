using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.Json;

// Representa um evento de log do sistema
public class LogEvent
{
    // Fonte do evento (serviço, programa, etc.)
    public string Fonte { get; set; }
    // Data e hora do evento
    public DateTime DataHora { get; set; }
    // Identificador do evento
    public int Identificador { get; set; }
    // Tipo do evento (Info, Warning, Error)
    public string Tipo { get; set; }
    // Mensagem do evento
    public string Mensagem { get; set; }
}

// Representa o leitor de eventos do sistema operacional
public class LogReader
{
    // Verifique qual sistema operacional para decidir o método que irá usar
    public IEnumerable<LogEvent> LerEventos(int maximoEventos)
    {
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
        {
            return LerEventosWindows(maximoEventos);
        }
        else if (
            RuntimeInformation.IsOSPlatform(OSPlatform.Linux) ||
            RuntimeInformation.IsOSPlatform(OSPlatform.OSX) ||
            RuntimeInformation.OSDescription.ToLower().Contains("ubuntu")
        )
        {
            return LerEventosUnix(maximoEventos);
        }
        // Retorno padrão caso nenhum SO seja identificado
        else
        {
            return new List<LogEvent>();
        }
    }

    // Lê eventos do log do Windows
    private IEnumerable<LogEvent> LerEventosWindows(int maximoEventos)
    {
        // Cria uma lista para armazenar os eventos lidos
        var eventos = new List<LogEvent>();

        // Abre o log de eventos do sistema do Windows
        using (EventLog logWindows = new EventLog("System"))
        {
            // Total de entradas no log
            int total = logWindows.Entries.Count;
            int contador = 0; 

            // Percorre as entradas do log do mais recente para o mais antigo
            for (int i = total - 1; i >= 0 && contador < maximoEventos; i--)
            {
                var entrada = logWindows.Entries[i]; 

                eventos.Add(new LogEvent
                {
                    Fonte = entrada.Source, 
                    DataHora = entrada.TimeGenerated,
                    Identificador = entrada.InstanceId.GetHashCode(),
                    Tipo = entrada.EntryType.ToString(),
                    Mensagem = entrada.Message,
                });
                contador++;
            }
        }
        return eventos;
    }

    // Lê eventos do log do Linux
    private IEnumerable<LogEvent> LerEventosUnix(int maximoEventos)
    {
        var eventos = new List<LogEvent>();
        try
        {
            // Monta o comando para buscar os logs mais recentes no formato ISO
            var psi = new System.Diagnostics.ProcessStartInfo
            {
                FileName = "journalctl",
                // -n {maximoEventos}: Mostra apenas os {maximoEventos} eventos mais rentes.
                // --no-pager: Faz com que a saída seja exibida diretamente, sem usar um paginador como o less.
                // -o short-iso: Define o formato de saída das linhas como ISO curto (data/hora legível).
                Arguments = $"-n {maximoEventos} --no-pager -o short-iso",
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            using (var processo = System.Diagnostics.Process.Start(psi))
            using (var leitor = processo.StandardOutput)
            {
                string linha;
                int contador = 0;
                while ((linha = leitor.ReadLine()) != null)
                {
                    // Ignora linhas em branco e cabeçalhos do journalctl
                    if (string.IsNullOrWhiteSpace(linha)) continue;
                    if (linha.TrimStart().StartsWith("-- Logs begin at") || linha.TrimStart().StartsWith("-- No entries --")) continue;

                    // Extrai a data do início da linha (formato ISO)
                    string[] partes = linha.Split(' ', 3);
                    DateTime dataHora = DateTime.Now;
                    if (partes.Length > 0)
                        DateTime.TryParse(partes[0], out dataHora);

                    // Extrai o serviço (source) do evento
                    string fonte = "journalctl";
                    if (partes.Length > 2)
                    {
                        var depoisHost = partes[2];
                        var idx = depoisHost.IndexOf(':');
                        if (idx > 0)
                            fonte = depoisHost.Substring(0, idx);
                    }

                    // Define o tipo do evento com base no texto da linha
                    string tipo = "Info";
                    if (linha.ToLower().Contains("error") || linha.ToLower().Contains("err")) tipo = "Error";
                    else if (linha.ToLower().Contains("warn")) tipo = "Warning";

                    // Adiciona o evento à lista
                    eventos.Add(new LogEvent
                    {
                        Fonte = fonte,
                        DataHora = dataHora,
                        Identificador = 0,
                        Tipo = tipo,
                        Mensagem = linha
                    });
                    contador++;
                    if (contador >= maximoEventos) break;
                }
            }
        }
        catch (Exception ex)
        {
            // Em caso de erro, adiciona um evento de erro à lista
            eventos.Add(new LogEvent
            {
                Fonte = "journalctl",
                DataHora = DateTime.Now,
                Identificador = 0,
                Tipo = "Error",
                Mensagem = "Erro ao ler journalctl: " + ex.Message,
            });
        }
        return eventos;
    }
}

// Classe principal do programa
public class Program
{
    public static void Main(string[] args)
    {
        int maximoEventos = int.MaxValue;
        // Lê a quantidade de eventos a buscar a partir dos argumentos
        if (args.Length > 0 && int.TryParse(args[0], out int n))
            maximoEventos = n;

        var leitor = new LogReader();
        var eventos = leitor.LerEventos(maximoEventos);
        // Serializa a lista de eventos para JSON e imprime no console
        string json = JsonSerializer.Serialize(eventos);
        Console.WriteLine(json);
    }
}