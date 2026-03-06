import socket
import threading

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
