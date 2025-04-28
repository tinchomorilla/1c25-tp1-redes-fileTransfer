import socket
import sys
from os.path import abspath, dirname

# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))
from src.RDT.stop_and_wait import MAX_DATA_SIZE, StopAndWaitRDT


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
            self.socket, addr=(self.server_addr, self.server_port), is_sender=True
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
        rdt.send(b"__UPLOAD_DONE__")
        print(f"[CLIENT] Archivo '{src}' enviado como '{filename}'")

        # Cerrar socket
        self.socket.close()

    def download(self, name: str, dst: str):
        pass
