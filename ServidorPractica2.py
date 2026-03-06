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