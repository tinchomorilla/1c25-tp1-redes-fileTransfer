import socket
import sys
from os.path import abspath, dirname
from lib.Errors.exceptions import MaximumRetriesError
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

# from tqdm import tqdm
import os


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
            else GoBackN(address=(self.server_ip, self.server_port), logger=logger)
        )
        self.logger = logger

    def upload(self, src: str, filename: str):
        try:
            self.rdt.initialize_handshake(self.stream, filename, UPLOAD)
        except Exception as e:
            self.logger.error(f"Error during handshake: {e}")
            return
        # Calcular el tamaño total del archivo
        total_bytes = os.path.getsize(src)
        sent_bytes = 0
        bytes_transferred = 0
        total_packets_sent = 0

        self.rdt.sequence_number = 0
        self.rdt.ack_number = 0

        with open(src, "rb") as f:
            data = f.read(PAYLOAD_SIZE)
            while data:
                packet = Packet.new_regular_packet(data, UPLOAD)
                self.rdt.send(packet, self.stream)
                data = f.read(PAYLOAD_SIZE)
                bytes_transferred += len(packet.get_payload())
                total_packets_sent += 1
                self.logger.debug(
                    f"[CLIENT] Enviados {bytes_transferred} / {total_bytes} bytes ({total_bytes - bytes_transferred} restantes)"
                )
                self.logger.debug(
                    f"[CLIENT] {bytes_transferred}/{total_bytes} bytes ({100 * bytes_transferred / total_bytes:.2f}%)"
                )

            fin_packet = Packet.new_fin_packet()
            try:
                self.rdt.send(fin_packet, self.stream)
            except MaximumRetriesError as e:
                self.logger.error(f"Exception occurred: {e}")

            self.logger.info(f"Upload completed for file: {filename}")
            self.logger.info(f"Total number of packets sent: {total_packets_sent}")

    def download(self, dst: str, filename: str):
        try:
            self.rdt.initialize_handshake(self.stream, filename, DOWNLOAD)
        except Exception as e:
            self.logger.error(f"Error during handshake: {e}")
            return
        with open(dst, "wb") as f:
            while True:
                packet = self.rdt.recv(self.stream)
                if packet.is_fin():
                    break
                f.write(packet.get_payload())

        self.logger.info(f"[CLIENT] Archivo '{filename}' descargado como '{dst}'")
