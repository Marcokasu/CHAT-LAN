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

def actualizar_lista_usuarios():
    #Envia la lista actualizada de usuarios a todos los clientes.
    with lock:
        usuarios = ",".join(clientes.values())
    transmitir_a_todos(f"USERS|{usuarios}")