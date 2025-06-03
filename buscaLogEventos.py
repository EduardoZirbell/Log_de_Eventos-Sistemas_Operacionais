import win32evtlog

#Classe responsável por acessar e ler os eventos do log do Windows
class LeitorDeEventos:
    def __init__(self, servidor='localhost', tipo_log='System'):
        self.servidor = servidor
        self.tipo_log = tipo_log

    def ler_eventos(self, tipos_evento=None, maximo=100):
#tipos_evento: Lista de constantes win32evtlog.EVENTLOG_* ou None para todos
#maximo: Número máximo de eventos a serem lidos.
        handle = win32evtlog.OpenEventLog(self.servidor, self.tipo_log)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        eventos = []
        total = 0
        while True:
            registros = win32evtlog.ReadEventLog(handle, flags, 0)
            if not registros:
                break

            for registro in registros:
                if tipos_evento is None or registro.EventType in tipos_evento:
                    eventos.append({
                        'Fonte': registro.SourceName,
                        'DataHora': registro.TimeGenerated.Format(),
                        'ID': registro.EventID,
                        'Tipo': registro.EventType,
                        'Mensagem': registro.StringInserts
                    })
                    total += 1
                    if total >= maximo:
                        return eventos

        return eventos