import tkinter as tk
from tkinter import ttk, messagebox
from buscaLogEventos import LeitorDeEventos
import win32evtlog

# Classe que monta a interface gráfica para visualizar os eventos
class visualizadorEventos:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Eventos do Windows")

        self.mapa_tipos_evento = {
            "Informação": win32evtlog.EVENTLOG_INFORMATION_TYPE,
            "Aviso": win32evtlog.EVENTLOG_WARNING_TYPE,
            "Erro": win32evtlog.EVENTLOG_ERROR_TYPE,
            "Todos": None
        }

        self.criar_elementos_interface()
# Cria e organiza os widgets da interface gráfica.
    def criar_elementos_interface(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Tipo de Evento:").grid(column=0, row=0, sticky=tk.W)
        self.tipo_evento_var = tk.StringVar(value="Todos")
        self.combo = ttk.Combobox(frame, textvariable=self.tipo_evento_var, state="readonly")
        self.combo['values'] = list(self.mapa_tipos_evento.keys())
        self.combo.grid(column=1, row=0, sticky=tk.W)

        self.botao_buscar = ttk.Button(frame, text="Buscar Eventos", command=self.buscar_eventos)
        self.botao_buscar.grid(column=2, row=0, padx=5)

        self.area_texto = tk.Text(frame, wrap=tk.WORD, height=25, width=100)
        self.area_texto.grid(column=0, row=1, columnspan=3, pady=10)

    def buscar_eventos(self):
#Busca e exibe os eventos do Windows conforme o tipo selecionado.
        self.area_texto.delete(1.0, tk.END)
        rotulo_tipo = self.tipo_evento_var.get()
        tipo_evento = self.mapa_tipos_evento[rotulo_tipo]
        leitor = LeitorDeEventos()

        try:
            eventos = leitor.ler_eventos(tipos_evento=None if tipo_evento is None else [tipo_evento])
            for evt in eventos:
                mensagem = evt['Mensagem'] if evt['Mensagem'] else ['']
                self.area_texto.insert(tk.END, f"[{evt['DataHora']}] {evt['Fonte']} - ID {evt['ID']}\n")
                self.area_texto.insert(tk.END, f"Tipo: {evt['Tipo']}\n")
                self.area_texto.insert(tk.END, "Mensagem:\n  " + "\n  ".join(mensagem) + "\n\n")
        except Exception as e:
            messagebox.showerror("Erro", str(e))