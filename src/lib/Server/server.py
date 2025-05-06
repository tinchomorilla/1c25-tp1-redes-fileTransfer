import os
import socket
import sys
from os.path import abspath, dirname
from lib.Server.listener import Listener
# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))


class Server:
    def __init__(self, host: str, port: int, storage_dir: str, protocol: str, logger):
        self.host = host
        self.port = port
        self.storage_dir = storage_dir
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = protocol
        self.logger = logger

    def run(self):
        """Inicializa el servidor y comienza a escuchar conexiones."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        try:
            self.sock.bind((self.host, int(self.port)))
            self.logger.info(f"[SERVER] Servidor iniciado en {self.host}:{self.port}")
            listener = Listener(self.sock, self.protocol, self.logger, self.storage_dir)
            listener.listen()
        except socket.error as e:
            self.logger.error(f"[SERVER] Error al enlazar el socket: {e}")
            self.sock.close()
            sys.exit(1)

        
        
