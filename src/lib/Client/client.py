import socket
import sys
from os.path import abspath, dirname

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))
from lib.RDT.stop_and_wait import MAX_DATA_SIZE, TYPE_DATA, TYPE_INIT, StopAndWaitRDT

DOWNLOAD_MARKER = b"__DOWNLOAD_DONE__"
UPLOAD_MARKER = b"__UPLOAD_DONE__"

class Client:
    def __init__(self, server_addr: str, server_port: int, protocol: str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_addr = server_addr
        self.server_port = server_port
        self.protocol = (
            protocol  # Protocolo de recuperación de errores (e.g., Stop-and-Wait)
        )

    def upload(self, src: str, filename: str):
        # Inicializar RDT
        rdt = StopAndWaitRDT(
            self.socket, addr=(self.server_addr, self.server_port)
        )

        # Enviar comando inicial UPLOAD <filename>
        init_msg = f"UPLOAD|{filename.strip()}".encode()
        rdt.send(init_msg, TYPE_INIT)

        # Abrir archivo y fragmentar
        with open(src, "rb") as f:
            while True:
                chunk = f.read(MAX_DATA_SIZE)
                if not chunk:
                    break
                rdt.send(chunk, TYPE_DATA)

        # Enviar marcador de fin de transmisión
        rdt.send(UPLOAD_MARKER, TYPE_DATA)
        print(f"[CLIENT] Archivo '{src}' enviado como '{filename}'")

        # Cerrar socket
        self.socket.close()

    def download(self, dst: str, name: str):
        # Inicializar RDT
        rdt = StopAndWaitRDT(
            self.socket, addr=(self.server_addr, self.server_port)
        )

        # Enviar comando inicial DOWNLOAD <filename>
        init_msg = f"DOWNLOAD|{name.strip()}".encode()
        rdt.send(init_msg, TYPE_INIT)

        # Abrir archivo para escritura
        with open(dst, "wb") as f:
            while True:
                chunk = rdt.recv_client()
                if chunk == DOWNLOAD_MARKER:
                    break
                f.write(chunk)

        print(f"[CLIENT] Archivo '{name}' descargado como '{dst}'")

        # Cerrar socket
        self.socket.close()