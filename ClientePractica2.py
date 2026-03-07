import socket
import threading
import tkinter as tk
from tkinter import messagebox
import random


class ChatClienteLAN:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()

        self.socket_cliente = None
        self.nombre_usuario = ""
        self.colores_asignados = {}
        self.lista_colores = ["#FF5733", "#5FFE7C", "#3357FF", "#F333FF", "#33FFF5", "#FFC300", "#FF33A8", "#00FF00", "#FF9900"]
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

    def construir_interfaz_principal(self):
        self.root.deiconify()
        self.root.title(f"Chat Grupal LAN - {self.nombre_usuario}")
        self.root.geometry("800x520") #600x400
        self.root.configure(bg="#1e1e1e")

        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_frame = tk.Frame(main_frame, bg="#1e1e1e")
        top_frame.pack(fill=tk.BOTH, expand=True)

        # Área de mensajes (Text + Scrollbar manuales)
        chat_frame = tk.Frame(top_frame, bg="#1e1e1e")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        scrollbar = tk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.area_chat = tk.Text(chat_frame, wrap=tk.WORD, state=tk.DISABLED,
                                bg='black', fg='white', font=("Arial", 11),
                                yscrollcommand=scrollbar.set)
        self.area_chat.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.area_chat.yview)

        # Estilos visuales
        self.area_chat.tag_config('propio', foreground='#4CAF50', justify='right')
        self.area_chat.tag_config('sistema', foreground='#f39c12', font=('Arial', 9, 'italic'), justify='center')
        self.area_chat.tag_config('texto_blanco', foreground='white')

        # Panel lateral de usuarios
        users_frame = tk.Frame(top_frame, width=150, bg="#1e1e1e")
        users_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(users_frame, text="🟢 En linea", bg="#1e1e1e", fg="white", font=("Arial", 10, "bold")).pack()
        self.lista_usuarios = tk.Listbox(users_frame, bg="#2c3e50", fg="white", relief="flat")
        self.lista_usuarios.pack(fill=tk.BOTH, expand=True)

        # Campo de texto + botón enviar
        bottom_frame = tk.Frame(main_frame, bg="#1e1e1e")
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        self.entry_mensaje = tk.Entry(bottom_frame, font=("Arial", 12))
        self.entry_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_mensaje.bind("<Return>", lambda event: self.enviar_mensaje())

        tk.Button(bottom_frame, text="Enviar", command=self.enviar_mensaje,
                bg="#2980b9", fg="white", font=("Arial", 10, "bold"), relief="flat").pack(side=tk.RIGHT)

        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def obtener_color_usuario(self, nombre):
    #Asigna un color fijo y aleatorio a cada usuario.
        if nombre not in self.colores_asignados:
            color = random.choice(self.lista_colores)
            self.colores_asignados[nombre] = color
            self.area_chat.tag_config(f'user_{nombre}', foreground=color, font=("Arial", 11, "bold"))
        return f'user_{nombre}'

    def recibir_mensajes(self):
        #Hilo que escucha al servidor usando un buffer para separar mensajes.
        buffer = ""
        while True:
            try:
                data = self.socket_cliente.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data

                # Procesar cada mensaje completo separado por \n
                while "\n" in buffer:
                    mensaje, buffer = buffer.split("\n", 1)
                    mensaje = mensaje.strip()
                    if not mensaje:
                        continue
                    self.root.after(0, self.procesar_mensaje, mensaje)

            except:
                self.root.after(0, self.mostrar_mensaje_sistema, "Conexión perdida con el servidor.")
                break

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

