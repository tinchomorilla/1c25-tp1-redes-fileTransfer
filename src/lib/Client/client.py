import socket
import sys
from os.path import abspath, dirname

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))
from lib.RDT.stop_and_wait import MAX_DATA_SIZE, StopAndWaitRDT

DOWNLOAD_MARKER = b"__DOWNLOAD_DONE__"
UPLOAD_MARKER = b"__UPLOAD_DONE__"

class Client:
    def __init__(self, server_addr: str, server_port: int, protocol: str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_addr = server_addr
        self.server_port = server_port
        self.rdt = self._initialize_rdt(protocol)

    def upload(self, src: str, filename: str):

        # Enviar comando inicial UPLOAD <filename>
        init_msg = f"UPLOAD|{filename.strip()}".encode()
        self.rdt.send(init_msg)

        # Abrir archivo y fragmentar
        with open(src, "rb") as f:
            while True:
                chunk = f.read(MAX_DATA_SIZE)
                if not chunk:
                    break
                self.rdt.send(chunk)

        # Enviar marcador de fin de transmisión
        self.rdt.send(UPLOAD_MARKER)
        print(f"[CLIENT] Archivo '{src}' enviado como '{filename}'")

        # Cerrar socket
        self.socket.close()

    def download(self, dst: str, name: str):
        # Enviar comando inicial DOWNLOAD <filename>
        init_msg = f"DOWNLOAD|{name.strip()}".encode()
        self.rdt.send(init_msg)

        # Abrir archivo para escritura
        with open(dst, "wb") as f:
            while True:
                chunk = self.rdt.recv()
                if chunk == DOWNLOAD_MARKER:
                    break
                f.write(chunk)

        print(f"[CLIENT] Archivo '{name}' descargado como '{dst}'")

        # Cerrar socket
        self.socket.close()

    def _initialize_rdt(self, protocol: str):
        if protocol == "stop_and_wait":
            return StopAndWaitRDT(self.socket, addr=(self.server_addr, self.server_port))
        else:
            return GoBackNRDT()