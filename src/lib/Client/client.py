import queue
import socket
import sys
from os.path import abspath, dirname
import threading

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))
from lib.constants import *

from lib.RDT.stop_and_wait import StopAndWaitRDT

class Client:
    def __init__(self, server_addr: str, server_port: int, protocol: str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_addr = server_addr
        self.server_port = server_port
        self.protocol = protocol
        self.handlers = {}
        self.lock = threading.Lock()

    def upload(self, src: str, filename: str):
        # Inicializar RDT
        rdt = StopAndWaitRDT(
            self.socket, addr=(self.server_addr, self.server_port)
        )

        # Enviar comando inicial UPLOAD <filename>
        init_msg = f"UPLOAD|{filename.strip()}".encode()
        rdt.send(init_msg)

        # Abrir archivo y fragmentar
        with open(src, "rb") as f:
            while True:
                chunk = f.read(MAX_DATA_SIZE)
                if not chunk:
                    break
                rdt.send(chunk)

        # Enviar marcador de fin de transmisión
        rdt.send(UPLOAD_DONE_MARKER)
        print(f"[CLIENT] Archivo '{src}' enviado como '{filename}'")

        # Cerrar socket
        self.socket.close()

    def download(self, dst: str, name: str):
        q = queue.Queue()

        # Crear RDT con queue (como en el servidor)
        rdt = StopAndWaitRDT(self.socket, addr=(self.server_addr, self.server_port), queue=q)

        # Enviar comando inicial DOWNLOAD
        init_msg = f"DOWNLOAD|{name.strip()}".encode()
        rdt.send(init_msg)
        print(f"[CLIENT] Enviando mensaje inicial: {init_msg.decode()}")
        
        # Lanzar thread lector centralizado
        threading.Thread(
            target=self.reader, args=(q, dst), daemon=True
        ).start()

        # Esperar y escribir chunks del archivo
        with open(dst, "wb") as f:
            while True:
                chunk = rdt.recv()
                if chunk == DOWNLOAD_DONE_MARKER:
                    break
                f.write(chunk)

        print(f"[CLIENT] Archivo '{name}' descargado como '{dst}'")
        self.socket.close()

    def reader(self, q, dst):
            """Lector que mete paquetes en la queue si son del servidor"""
            while True:
                try:
                    data, addr = self.socket.recvfrom(1024)
                    print("[CLIENT] AGREGANDO DATA EN LA COLA")
                    q.put(data)
                except socket.timeout:
                    continue
