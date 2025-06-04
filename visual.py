import tkinter as tk
from tkinter import ttk, messagebox
from buscaLogEventos import LeitorDeEventos
import win32evtlog
import threading
import time

#Classe principal da interface gráfica para visualizar eventos do Windows
class visualizadorEventos:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Eventos do Windows")

#Mapeia os tipos de evento para os valores do win32evtlog
        self.mapa_tipos_evento = {
            "Informação": win32evtlog.EVENTLOG_INFORMATION_TYPE,
            "Aviso": win32evtlog.EVENTLOG_WARNING_TYPE,
            "Erro": win32evtlog.EVENTLOG_ERROR_TYPE,
            "Todos": None
        }
#Intervalos de atualização disponíveis
        self.mapa_intervalos = {
            "Única (manual)": 0,
            "5 segundos": 5,
            "10 segundos": 10,
            "20 segundos": 20,
            "30 segundos": 30
        }

        self.parar_atualizacao = False

        self.criar_elementos_interface()

    def criar_elementos_interface(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Tipo de Evento:").grid(column=0, row=0, sticky=tk.W)
        self.tipo_evento_var = tk.StringVar(value="Todos")
        self.combo_tipo = ttk.Combobox(frame, textvariable=self.tipo_evento_var, state="readonly")
        self.combo_tipo['values'] = list(self.mapa_tipos_evento.keys())
        self.combo_tipo.grid(column=1, row=0, sticky=tk.W)

        ttk.Label(frame, text="qtd de Eventos:").grid(column=0, row=1, sticky=tk.W)
        self.qtd_var = tk.IntVar(value=100)
        self.qtd_entry = ttk.Entry(frame, textvariable=self.qtd_var, width=10)
        self.qtd_entry.grid(column=1, row=1, sticky=tk.W)

        ttk.Label(frame, text="Intervalo de Atualização:").grid(column=0, row=2, sticky=tk.W)
        self.intervalo_var = tk.StringVar(value="Única (manual)")
        self.combo_intervalo = ttk.Combobox(frame, textvariable=self.intervalo_var, state="readonly")
        self.combo_intervalo['values'] = list(self.mapa_intervalos.keys())
        self.combo_intervalo.grid(column=1, row=2, sticky=tk.W)

        self.botao_buscar = ttk.Button(frame, text="Iniciar", command=self.iniciar_busca)
        self.botao_buscar.grid(column=2, row=2, padx=5)

        self.botao_parar = ttk.Button(frame, text="Parar", command=self.parar)
        self.botao_parar.grid(column=2, row=3, pady=5)

        self.area_texto = tk.Text(frame, wrap=tk.WORD, height=25, width=100)
        self.area_texto.grid(column=0, row=4, columnspan=3, pady=10)

    def iniciar_busca(self):
        self.parar_atualizacao = False
        intervalo = self.mapa_intervalos[self.intervalo_var.get()]
        if intervalo == 0:
            self.buscar_eventos()  # Busca manual única
        else:
#Inicia busca periódica em uma thread separada
            threading.Thread(target=self.atualizacao_periodica, args=(intervalo,), daemon=True).start()

    def parar(self):
        self.parar_atualizacao = True  # Sinaliza para parar a atualização periódica

    def atualizacao_periodica(self, intervalo):
#Executa a busca de eventos em intervalos definidos até ser parado
        while not self.parar_atualizacao:
            self.buscar_eventos()
            time.sleep(intervalo)

    def buscar_eventos(self):
        self.area_texto.delete(1.0, tk.END)  # Limpa a área de texto
        rotulo_tipo = self.tipo_evento_var.get()
        tipo_evento = self.mapa_tipos_evento[rotulo_tipo]
        leitor = LeitorDeEventos()
        maximo = self.qtd_var.get()

        try:
#Busca os eventos usando o leitor
            eventos = leitor.ler_eventos(tipos_evento=None if tipo_evento is None else [tipo_evento], maximo=maximo)
            for evt in eventos:
                mensagem = evt['Mensagem'] if evt['Mensagem'] else ['']
#Exibe cada evento formatado na área de texto
                self.area_texto.insert(tk.END, f"[{evt['DataHora']}] {evt['Fonte']} - ID {evt['ID']}\n")
                self.area_texto.insert(tk.END, f"Tipo: {evt['Tipo']}\n")
                self.area_texto.insert(tk.END, "Mensagem:\n  " + "\n  ".join(mensagem) + "\n\n")
        except Exception as e:
            messagebox.showerror("Erro", str(e))  # Mostra erro caso ocorra