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