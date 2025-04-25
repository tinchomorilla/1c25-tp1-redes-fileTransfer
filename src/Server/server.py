import os
import socket
from src.RDT.stop_and_wait import StopAndWaitRDT
from parse_args import parse_arguments

DONE_MARKER = b'__UPLOAD_DONE__'

class Server:
    def __init__(self, host: str, port: int, storage_dir: str, protocol: str):
        self.host = host
        self.port = port
        self.storage_dir = storage_dir
        self.protocol = protocol  # Protocolo de recuperación de errores (e.g., Stop-and-Wait)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        os.makedirs(self.storage_dir, exist_ok=True)
        self.sock.bind((self.host, self.port))
        print(f"[SERVER] Escuchando en {self.host}:{self.port}")

        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                print(f"[SERVER] Atendiendo nuevo cliente: {addr}")
                self.handle_client(addr, data)
            except KeyboardInterrupt:
                print("[SERVER] Cerrando servidor")
                break

    def handle_client(self, addr, init_msg):
        rdt = StopAndWaitRDT(self.sock, is_sender=False)

        # Validar comando inicial
        if not init_msg.startswith(b"UPLOAD|"):
            print(f"[SERVER] Comando inválido de {addr}")
            return

        filename = init_msg.decode().split("|")[1]
        filepath = os.path.join(self.storage_dir, filename)

        with open(filepath, "wb") as f:
            print(f"[SERVER] Recibiendo archivo: {filename}")
            while True:
                data, _ = rdt.recv()
                if data == DONE_MARKER:
                    print(f"[SERVER] Fin de transmisión recibido de {addr}")
                    break
                f.write(data)

        print(f"[SERVER] Archivo recibido: {filepath}")