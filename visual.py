import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import csv
import os
import subprocess
import json
from tkinter import filedialog

class VisualizadorEventos:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Eventos do Sistema")
        self.root.geometry("1000x720")
        self.root.minsize(800, 600)

        self.mapa_intervalos = {
            "Única (manual)": 0,
            "5 segundos": 5,
            "10 segundos": 10,
            "20 segundos": 20,
            "30 segundos": 30
        }

        self.tipos_evento = ["Todos", "Error", "Warning", "Information"]
        self.parar_atualizacao = False
        self.criar_interface()

    def criar_interface(self):
        frame_controles = ttk.LabelFrame(self.root, text="Configurações", padding=10)
        frame_controles.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_controles, text="Quantidade de Eventos:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.qtd_var = tk.IntVar(value=100)
        self.qtd_entry = ttk.Entry(frame_controles, textvariable=self.qtd_var, width=10)
        self.qtd_entry.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(frame_controles, text="Tipo:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.tipo_var = tk.StringVar(value="Todos")
        self.combo_tipo = ttk.Combobox(frame_controles, textvariable=self.tipo_var, state="readonly", width=15)
        self.combo_tipo['values'] = self.tipos_evento
        self.combo_tipo.grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Label(frame_controles, text="Intervalo Atualização:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.intervalo_var = tk.StringVar(value="Única (manual)")
        self.combo_intervalo = ttk.Combobox(frame_controles, textvariable=self.intervalo_var, state="readonly", width=20)
        self.combo_intervalo['values'] = list(self.mapa_intervalos.keys())
        self.combo_intervalo.grid(row=0, column=5, sticky=tk.W, padx=5)

        self.botao_buscar = ttk.Button(frame_controles, text="Iniciar", command=self.iniciar_busca)
        self.botao_buscar.grid(row=0, column=6, padx=10)

        self.botao_parar = ttk.Button(frame_controles, text="Parar", command=self.parar)
        self.botao_parar.grid(row=0, column=7, padx=5)

        ttk.Label(frame_controles, text="Buscar:").grid(row=0, column=8, sticky=tk.W, padx=5)
        self.busca_var = tk.StringVar()
        self.busca_entry = ttk.Entry(frame_controles, textvariable=self.busca_var, width=20)
        self.busca_entry.grid(row=0, column=9, sticky=tk.W, padx=5)

        self.botao_exportar = ttk.Button(frame_controles, text="Exportar CSV", command=self.exportar_csv)
        self.botao_exportar.grid(row=0, column=10, padx=10)

        frame_logs = ttk.LabelFrame(self.root, text="Eventos", padding=10)
        frame_logs.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        # Substitui o ScrolledText pelo Treeview
        columns = ("Data", "Tipo", "Fonte", "ID", "Mensagem")
        self.tree = ttk.Treeview(frame_logs, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.W, width=150 if col != "Mensagem" else 400)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.status_var = tk.StringVar(value="Eventos exibidos: 0")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=(10, 5))
        self.status_label.pack(fill=tk.X)

        self.eventos_atuais = []

    def iniciar_busca(self):
        self.parar_atualizacao = False
        self.botao_buscar.config(text="Atualizando...", state="disabled")
        intervalo = self.mapa_intervalos[self.intervalo_var.get()]
        if intervalo == 0:
            self.buscar_eventos()
            self.botao_buscar.config(text="Iniciar", state="normal")
        else:
            threading.Thread(target=self.atualizacao_periodica, args=(intervalo,), daemon=True).start()

    def parar(self):
        self.parar_atualizacao = True
        self.botao_buscar.config(text="Iniciar", state="normal")

    def atualizacao_periodica(self, intervalo):
        while not self.parar_atualizacao:
            self.buscar_eventos()
            time.sleep(intervalo)
        self.botao_buscar.config(text="Iniciar", state="normal")

    def buscar_eventos(self):
        self.tree.delete(*self.tree.get_children())  # Limpa a árvore de eventos
        qtd = self.qtd_var.get()
        tipo = self.tipo_var.get()

        try:
            self.status_var.set("Buscando eventos...")
            self.root.update_idletasks()
            eventos = self.get_log_events(qtd)
            # Filtra por tipo, se não for "Todos"
            if tipo != "Todos":
                eventos = [evt for evt in eventos if evt.get('Type', '').lower() == tipo.lower()]
            busca = self.busca_var.get().lower()
            if busca:
                eventos = [evt for evt in eventos if busca in str(evt.get('Message', '')).lower()]
            eventos = eventos[:qtd]  # Limita a quantidade exibida
            eventos.sort(key=lambda evt: evt.get('DateTime', ''), reverse=True)

            for evt in eventos:
                self.tree.insert("", tk.END, values=(
                    evt.get('DateTime',''),
                    evt.get('Type',''),
                    evt.get('Source',''),
                    evt.get('Id',''),
                    evt.get('Message','').split('\n')[0]  # Mensagem resumida
                ))

            self.status_var.set(f"Eventos exibidos: {len(eventos)}")
            self.eventos_atuais = eventos

        except Exception as e:
            messagebox.showerror("Erro ao buscar eventos", str(e))

    def on_tree_double_click(self, event):
        item_id = self.tree.focus()
        if not item_id:
            return
        idx = self.tree.index(item_id)
        if 0 <= idx < len(self.eventos_atuais):
            evento = self.eventos_atuais[idx]
            self.mostrar_detalhes(evento)

    def mostrar_detalhes(self, evento):
        msg = f"Data: {evento.get('DateTime','')}\nFonte: {evento.get('Source','')}\nID: {evento.get('Id','')}\nTipo: {evento.get('Type','')}\n\nMensagem:\n{evento.get('Message','')}"
        messagebox.showinfo("Detalhes do Evento", msg)

    def exportar_csv(self):
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

    def get_log_events(self, qtd):
        exe = os.path.join("LogReaderApp", "bin", "Release", "net9.0", "LogReaderApp.exe")
        if not os.path.exists(exe):
            raise FileNotFoundError(f"Executável não encontrado: {exe}")
        result = subprocess.run([exe, str(qtd)], capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print("Erro ao executar LogReader:", result.stderr)
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualizadorEventos(root)
    root.mainloop()
