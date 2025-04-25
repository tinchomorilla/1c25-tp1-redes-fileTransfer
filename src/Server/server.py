import os
import socket
from src.Server.listener import Listener


class Server:
    def __init__(self, host: str, port: int, storage_dir: str):
        self.host = host
        self.port = port
        self.storage_dir = storage_dir
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        """Inicializa el servidor y comienza a escuchar conexiones."""
        os.makedirs(self.storage_dir, exist_ok=True)
        self.sock.bind((self.host, self.port))
        print(f"[SERVER] Escuchando en {self.host}:{self.port}")

        listener = Listener(self.sock)
        listener.listen(self.storage_dir)
