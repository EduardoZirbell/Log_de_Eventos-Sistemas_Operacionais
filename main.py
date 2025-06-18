import tkinter as tk
from visual import VisualizadorEventos

if __name__ == "__main__":
    # Cria a janela principal da aplicação Tkinter
    root = tk.Tk()
    # Inicializa o visualizador de eventos passando a janela principal
    app = VisualizadorEventos(root)
    # Inicia o loop principal da aplicação
    root.mainloop()
