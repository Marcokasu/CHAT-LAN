import socket
import threading
import tkinter as tk


class ChatClienteLAN:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()

        # --- VENTANA DE LOGIN ---
        self.login_win = tk.Toplevel(self.root)
        self.login_win.title("Conectar al Chat")
        self.login_win.geometry("300x150")
        self.login_win.resizable(False, False)
        self.login_win.configure(bg="#711d8b")

        tk.Label(self.login_win, text="IP del Servidor:", bg="#2c3e50", fg="white").pack(pady=5)
        self.entry_ip = tk.Entry(self.login_win)
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.pack()

        tk.Label(self.login_win, text="Nombre de Usuario:", bg="#2c3e50", fg="white").pack(pady=5)
        self.entry_nombre = tk.Entry(self.login_win)
        self.entry_nombre.pack()

        tk.Button(self.login_win, text="Conectar", command=self.conectar_servidor,
                bg="#27ae60", fg="white", font=("Arial", 10, "bold"), relief="flat").pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self.login_win.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)