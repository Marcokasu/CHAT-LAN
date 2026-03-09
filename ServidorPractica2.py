import socket
import threading

#VARIABLES GLOBALES
# Configuración del servidor
HOST = '0.0.0.0' 
PORT = 5000
MAX_HISTORIAL = 20

clientes = {} 
# Lista con los últimos 20 mensajes 
historial = [] 
# Para evitar condiciones de carrera al modificar diccionarios/listas
lock = threading.Lock()

def transmitir_a_todos(mensaje, remitente_socket=None):
    #Envia un mensaje a todos los clientes excepto al remitente.
    with lock:
        for cliente_sock in list(clientes.keys()):
            if cliente_sock != remitente_socket:
                try:
                    cliente_sock.send((mensaje + "\n").encode('utf-8'))
                except:
                    eliminar_cliente(cliente_sock)

def actualizar_lista_usuarios():
    #Envia la lista actualizada de usuarios a todos los clientes.
    with lock:
        usuarios = ",".join(clientes.values())
    transmitir_a_todos(f"USERS|{usuarios}")

def guardar_en_historial(mensaje):
    #Guarda el mensaje en el historial con limite de 20.
    with lock:
        historial.append(mensaje)
        if len(historial) > MAX_HISTORIAL:
            historial.pop(0)

def eliminar_cliente(cliente_socket):
    #Elimina al cliente y notifica a los demas.
    with lock:
        if cliente_socket in clientes:
            nombre = clientes[cliente_socket]
            del clientes[cliente_socket]
            cliente_socket.close()

            notificacion = f"SYSTEM|{nombre} ha salido del chat"
            print(notificacion)
            usuarios = ",".join(clientes.values())

            for cliente_sock in list(clientes.keys()):
                try:
                    cliente_sock.send((notificacion + "\n").encode('utf-8'))
                    cliente_sock.send((f"USERS|{usuarios}" + "\n").encode('utf-8'))
                except:
                    pass

def manejar_cliente(cliente_socket, direccion):
    #Hilo dedicado a cada cliente.
    try:
        # Primer mensaje = nombre del usuario
        nombre_usuario = cliente_socket.recv(1024).decode('utf-8').strip()

        with lock:
            clientes[cliente_socket] = nombre_usuario

        print(f"[{direccion}] se unió como {nombre_usuario}")

        # Enviar historial solo al recien conectado
        with lock:
            if historial:
                historial_str = "||".join(historial)
                cliente_socket.send((f"HISTORY|{historial_str}" + "\n").encode('utf-8'))

        # Notificar a los demas que entro
        notificacion = f"SYSTEM|{nombre_usuario} se ha unido al chat"
        transmitir_a_todos(notificacion, cliente_socket)

        # Actualizar lista de usuarios en todos
        actualizar_lista_usuarios()

        # Bucle principal para recibir mensajes
        while True:
            mensaje_recibido = cliente_socket.recv(1024).decode('utf-8').strip()

            if not mensaje_recibido or mensaje_recibido == "EXIT|":
                break

            mensaje_formateado = f"{nombre_usuario}: {mensaje_recibido}"
            guardar_en_historial(mensaje_formateado)
            transmitir_a_todos(f"CHAT|{mensaje_formateado}", cliente_socket)

    except Exception as e:
        print(f"Error con {direccion}: {e}")
    finally:
        eliminar_cliente(cliente_socket)

#Iniciar servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORT))
servidor.listen(5)
print(f"Servidor iniciado en el puerto {PORT}. Esperando conexiones...")

while True:
    try:
        cliente_sock, direccion_cliente = servidor.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(cliente_sock, direccion_cliente))
        hilo.daemon = True
        hilo.start()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        servidor.close()
        break