import tkinter as tk
from visual import visualizadorEventos

def main():
    root = tk.Tk()
    app = visualizadorEventos(root)
    root.mainloop()

if __name__ == "__main__":
    main()
