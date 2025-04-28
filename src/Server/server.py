import os
import socket
import sys
from os.path import abspath, dirname
from src.Server.listener import Listener
# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))


class Server:
    def __init__(self, host: str, port: int, storage_dir: str, protocol: str):
        self.host = host
        self.port = port
        self.storage_dir = storage_dir
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = protocol

    def run(self):
        """Inicializa el servidor y comienza a escuchar conexiones."""
        os.makedirs(self.storage_dir, exist_ok=True)
        self.sock.bind((self.host, self.port))
        print(f"[SERVER] Escuchando en {self.host}:{self.port}")

        listener = Listener(self.sock)
        listener.listen(self.storage_dir)
