import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import csv
from log_utils import obter_eventos_log

class VisualizadorEventos:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Eventos do Sistema")
        self.root.geometry("1600x900")
        self.root.minsize(1600, 900)

        # Mapeamento dos intervalos de atualização disponíveis
        self.mapa_intervalos = {
            "Única (manual)": 0,
            "5 segundos": 5,
            "10 segundos": 10,
            "20 segundos": 20,
            "30 segundos": 30
        }

        # Tipos de evento disponíveis para filtro
        self.tipos_evento = ["Todos", "Error", "Warning", "Information"]
        self.parar_atualizacao = False
        self.sort_column = None
        self.sort_reverse = False
        self.criar_interface()

    def criar_interface(self):
        # Cria o frame de controles (filtros, botões, busca)
        frame_controles = ttk.LabelFrame(self.root, text="Configurações", padding=10)
        frame_controles.pack(fill=tk.X, padx=10, pady=10)

        # Campo para definir a quantidade de eventos a buscar
        ttk.Label(frame_controles, text="Quantidade de Eventos:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.qtd_var = tk.IntVar(value=100)
        self.qtd_entry = ttk.Entry(frame_controles, textvariable=self.qtd_var, width=10)
        self.qtd_entry.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Combobox para selecionar o tipo de evento
        ttk.Label(frame_controles, text="Tipo:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.tipo_var = tk.StringVar(value="Todos")
        self.combo_tipo = ttk.Combobox(frame_controles, textvariable=self.tipo_var, state="readonly", width=15)
        self.combo_tipo['values'] = self.tipos_evento
        self.combo_tipo.grid(row=0, column=3, sticky=tk.W, padx=5)

        # Combobox para selecionar o intervalo de atualização automática
        ttk.Label(frame_controles, text="Intervalo Atualização:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.intervalo_var = tk.StringVar(value="Única (manual)")
        self.combo_intervalo = ttk.Combobox(frame_controles, textvariable=self.intervalo_var, state="readonly", width=20)
        self.combo_intervalo['values'] = list(self.mapa_intervalos.keys())
        self.combo_intervalo.grid(row=0, column=5, sticky=tk.W, padx=5)

        # Botão para iniciar a busca/atualização dos eventos
        self.botao_buscar = ttk.Button(frame_controles, text="Iniciar", command=self.iniciar_busca)
        self.botao_buscar.grid(row=0, column=6, padx=10)

        # Botão para parar a atualização automática
        self.botao_parar = ttk.Button(frame_controles, text="Parar", command=self.parar)
        self.botao_parar.grid(row=0, column=7, padx=5)

        # Campo de busca textual nos eventos
        ttk.Label(frame_controles, text="Buscar:").grid(row=0, column=8, sticky=tk.W, padx=5)
        self.busca_var = tk.StringVar()
        self.busca_entry = ttk.Entry(frame_controles, textvariable=self.busca_var, width=20)
        self.busca_entry.grid(row=0, column=9, sticky=tk.W, padx=5)

        # Botão para exportar os eventos exibidos para CSV
        self.botao_exportar = ttk.Button(frame_controles, text="Exportar CSV", command=self.exportar_csv)
        self.botao_exportar.grid(row=0, column=10, padx=10)

        # Frame para exibição dos eventos em formato de tabela
        frame_logs = ttk.LabelFrame(self.root, text="Eventos", padding=10)
        frame_logs.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        # Define as colunas da tabela de eventos
        columns = ("Data", "Tipo", "Fonte", "ID", "Mensagem")
        self.tree = ttk.Treeview(frame_logs, columns=columns, show="headings")
        for col in columns:
            # Permite ordenação ao clicar no cabeçalho da coluna
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_por_coluna(c))
            self.tree.column(col, anchor="w", width=150 if col != "Mensagem" else 400)

        # Barra de rolagem vertical para a tabela de eventos
        style = ttk.Style()
        style.configure("Vertical.TScrollbar", gripcount=0, width=20, background="#e0e0e0")
        vsb = ttk.Scrollbar(frame_logs, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Label de status para exibir a quantidade de eventos exibidos
        self.status_var = tk.StringVar(value="Eventos exibidos: 0")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=(10, 5))
        self.status_label.pack(fill=tk.X)

        self.eventos_atuais = []

        # Ordenação padrão: decrescente por Data
        self.sort_column = "Data"
        self.sort_reverse = True
        # Permite abrir detalhes do evento ao dar duplo clique
        self.tree.bind("<Double-1>", self.on_tree_double_click)

    def iniciar_busca(self):
        # Inicia a busca ou atualização automática dos eventos
        self.parar_atualizacao = False
        self.botao_buscar.config(text="Atualizando...", state="disabled")
        intervalo = self.mapa_intervalos[self.intervalo_var.get()]
        if intervalo == 0:
            self.buscar_eventos()
            self.botao_buscar.config(text="Iniciar", state="normal")
        else:
            # Inicia thread para atualização periódica
            threading.Thread(target=self.atualizacao_periodica, args=(intervalo,), daemon=True).start()

    def parar(self):
        # Para a atualização automática dos eventos
        self.parar_atualizacao = True
        self.botao_buscar.config(text="Iniciar", state="normal")

    def atualizacao_periodica(self, intervalo):
        # Atualiza os eventos periodicamente enquanto não for solicitado parar
        while not self.parar_atualizacao:
            self.buscar_eventos()
            time.sleep(intervalo)
        self.botao_buscar.config(text="Iniciar", state="normal")

    def buscar_eventos(self):
        # Busca os eventos de log e aplica filtros de tipo e busca textual
        self.tree.delete(*self.tree.get_children())
        qtd = self.qtd_var.get()
        tipo = self.tipo_var.get()

        try:
            self.status_var.set("Buscando eventos...")
            self.root.update_idletasks()
            eventos = obter_eventos_log(qtd)
            if tipo != "Todos":
                eventos = [evt for evt in eventos if evt.get('Type', '').lower() == tipo.lower()]
            busca = self.busca_var.get().lower()
            if busca:
                eventos = [evt for evt in eventos if busca in str(evt.get('Message', '')).lower()]
            self.eventos_atuais = eventos

            # Reaplica a ordenação anterior, se houver
            if hasattr(self, "sort_column") and self.sort_column:
                self.ordenar_por_coluna(self.sort_column, manter_direcao=True)
            else:
                self.preencher_treeview(eventos)

            self.status_var.set(f"Eventos exibidos: {len(eventos)}")
        except Exception as e:
            messagebox.showerror("Erro ao buscar eventos", str(e))

    def preencher_treeview(self, eventos):
        # Preenche a tabela de eventos na interface gráfica
        self.tree.delete(*self.tree.get_children())
        self.iid_to_evento = {}
        for idx, evt in enumerate(eventos):
            iid = str(idx)  # Usa o índice como identificador único
            self.tree.insert("", "end", iid=iid, values=(
                evt.get('DateTime',''),
                evt.get('Type',''),
                evt.get('Source',''),
                evt.get('Id',''),
                evt.get('Message','').split('\n')[0]
            ))
            self.iid_to_evento[iid] = evt

    def ordenar_por_coluna(self, col, manter_direcao=False):
        # Ordena os eventos exibidos pela coluna selecionada
        col_map = {
            "Data": "DateTime",
            "Tipo": "Type",
            "Fonte": "Source",
            "ID": "Id",
            "Mensagem": "Message"
        }
        key = col_map[col]
        # Alterna a direção da ordenação, exceto se for para manter a direção anterior
        if self.sort_column == col and not manter_direcao:
            self.sort_reverse = not self.sort_reverse
        elif self.sort_column != col:
            self.sort_reverse = False
        self.sort_column = col

        def sort_key(evt):
            val = evt.get(key, "")
            if key == "DateTime":
                try:
                    return str(val)
                except Exception:
                    return ""
            if key == "Id":
                try:
                    return int(val)
                except Exception:
                    return 0
            return val.lower() if isinstance(val, str) else val

        eventos_ordenados = sorted(self.eventos_atuais, key=sort_key, reverse=self.sort_reverse)
        self.preencher_treeview(eventos_ordenados)
        self.eventos_atuais = eventos_ordenados

        # Atualiza os títulos das colunas com a seta indicando ordenação
        for c in col_map:
            arrow = ""
            if c == col:
                arrow = " ▼" if self.sort_reverse else " ▲"
            self.tree.heading(c, text=c + arrow, command=lambda c=c: self.ordenar_por_coluna(c))

    def on_tree_double_click(self, event):
        # Exibe detalhes do evento ao dar duplo clique na linha
        item_id = self.tree.focus()
        if not item_id:
            return
        if self.tree.identify_region(event.x, event.y) == "heading":
            return
        evento = self.iid_to_evento.get(item_id)
        if evento:
            self.mostrar_detalhes(evento)

    def mostrar_detalhes(self, evento):
        # Mostra uma janela com detalhes completos do evento selecionado
        msg = f"Data: {evento.get('DateTime','')}\nFonte: {evento.get('Source','')}\nID: {evento.get('Id','')}\nTipo: {evento.get('Type','')}\n\nMensagem:\n{evento.get('Message','')}"
        messagebox.showinfo("Detalhes do Evento", msg)

    def exportar_csv(self):
        # Exporta os eventos exibidos para um arquivo CSV
        if not self.eventos_atuais:
            messagebox.showwarning("Exportação", "Nenhum evento para exportar.")
            return
        caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if caminho:
            with open(caminho, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Data", "Tipo", "Fonte", "ID", "Mensagem"])
                for evt in self.eventos_atuais:
                    writer.writerow([
                        evt.get('DateTime',''),
                        evt.get('Type',''),
                        evt.get('Source',''),
                        evt.get('Id',''),
                        evt.get('Message','')
                    ])
            messagebox.showinfo("Exportação", "Exportação concluída!")
