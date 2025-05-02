import socket
import sys
from os.path import abspath, dirname
from lib.Packet.packet import Packet
from lib.RDT.go_back_n import GoBackN
from lib.RDT.stream_wrapper import StreamWrapper
from lib.Common.constants import (
    DOWNLOAD,
    PAYLOAD_SIZE,
    SAW_PROTOCOL,
    GBN_PROTOCOL,
    UPLOAD,
)


# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))
from lib.RDT.stop_and_wait import StopAndWait

DOWNLOAD_MARKER = b"__DOWNLOAD_DONE__"
UPLOAD_MARKER = b"__UPLOAD_DONE__"


class Client:
    def __init__(self, server_ip: str, server_port: int, protocol: str, logger):
        self.stream = StreamWrapper(
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM), None
        )
        self.server_ip = server_ip
        self.server_port = server_port
        self.rdt = (
            StopAndWait(address=(self.server_ip, self.server_port), logger=logger)
            if protocol == SAW_PROTOCOL
            else GoBackN(self.socket, addr=(self.server_ip, self.server_port))
        )
        self.logger = logger

    def upload(self, src: str, filename: str):

        print(f"[CLIENT] Iniciando Handshake '{src}' como '{filename}'")
        self.rdt.initialize_handshake(self.stream, filename, UPLOAD)
        print(f"[CLIENT] Handshake completo")
        # Abrir archivo y fragmentar
        with open(src, "rb") as f:
            print("[CLIENT] Archivo abierto")
            data = f.read(PAYLOAD_SIZE)
            print(f"[CLIENT] Leyendo {len(data)} bytes")
            while data:
                print("[CLIENT] Creando paquete")
                packet = Packet.new_regular_packet(data, UPLOAD)
                print("[CLIENT] Paquete creado")
                self.rdt.send(packet, self.stream)
                print(f"[CLIENT] Enviando paquete de {len(data)} bytes")
                data = f.read(PAYLOAD_SIZE)
            fin_packet = Packet.new_fin_packet()

        print("[CLIENT] Enviando paquete de finalización")
        self.rdt.send(fin_packet, self.stream)
        print(f"[CLIENT] Archivo '{src}' enviado como '{filename}'")

    def download(self, dst: str, filename: str):

        self.rdt.initialize_handshake(self.stream, filename, DOWNLOAD)

        with open(dst, "wb") as f:
            while True:
                packet = self.rdt.recv()
                if packet.is_fin():
                    break
                f.write(packet.get_payload())

        print(f"[CLIENT] Archivo '{filename}' descargado como '{dst}'")
