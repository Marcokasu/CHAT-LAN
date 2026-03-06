import socket
import threading
import tkinter as tk
from tkinter import messagebox
import random


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
    
    def conectar_servidor(self):
        ip = self.entry_ip.get().strip()
        self.nombre_usuario = self.entry_nombre.get().strip()

        if not ip or not self.nombre_usuario:
            messagebox.showwarning("Error", "Llene todos los campos.")
            return

        try:
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.connect((ip, 5000))
            self.socket_cliente.send(self.nombre_usuario.encode('utf-8'))

            self.login_win.destroy()
            self.construir_interfaz_principal()

            hilo_recepcion = threading.Thread(target=self.recibir_mensajes)
            hilo_recepcion.daemon = True
            hilo_recepcion.start()

        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor:\n{e}")

    def obtener_color_usuario(self, nombre):
    #Asigna un color fijo y aleatorio a cada usuario.
    if nombre not in self.colores_asignados:
        color = random.choice(self.lista_colores)
        self.colores_asignados[nombre] = color
        self.area_chat.tag_config(f'user_{nombre}', foreground=color, font=("Arial", 11, "bold"))
    return f'user_{nombre}'


    def procesar_mensaje(self, mensaje):
        #Clasifica y muestra cada mensaje segun su tipo.
        if mensaje.startswith("SYSTEM|"):
            self.mostrar_mensaje_sistema(mensaje.split("|", 1)[1])

        elif mensaje.startswith("CHAT|"):
            self.procesar_mensaje_usuario(mensaje.split("|", 1)[1])

        elif mensaje.startswith("HISTORY|"):
            for msg in mensaje.split("|", 1)[1].split("||"):
                if msg:
                    self.procesar_mensaje_usuario(msg)

        elif mensaje.startswith("USERS|"):
            usuarios = mensaje.split("|", 1)[1].split(",")
            self.lista_usuarios.delete(0, tk.END)
            for u in usuarios:
                if u:
                    self.lista_usuarios.insert(tk.END, u)

