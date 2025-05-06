import queue
import socket
from threading import Thread as thread
import os
import threading
from lib.Errors.exceptions import MaxSizeFileError
from lib.Packet.packet import Packet
from lib.RDT.go_back_n import GoBackN
from lib.RDT.stop_and_wait import StopAndWait
from lib.RDT.stream_wrapper import StreamWrapper
from lib.Common.constants import DOWNLOAD, MAX_FILE_SIZE, PAYLOAD_SIZE, SAW_PROTOCOL


lock = threading.Lock()

class ClientHandler(thread):
    def __init__(
        self, 
        client_address,
        sequence_number_client,
        protocol,
        logger,
        filename,
        is_download,
        storage_dir
    ):
        self.address = client_address
        self.sequence_number_client = sequence_number_client
        self.stream = StreamWrapper(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), queue.Queue())        
        self.logger = logger
        self.filename = filename
        self.is_download = is_download
        self.rdt = StopAndWait(self.address, self.logger) if protocol == SAW_PROTOCOL else GoBackN(self.address, self.logger)
        self.storage_dir = storage_dir
        thread.__init__(self)
        

    def run(self):
        try:
            self.logger.info(f"[CLIENT_HANDLER] Iniciando handshake con {self.address}")
            self.rdt.response_handshake(self.stream, self.address, self.sequence_number_client)
            self.logger.info(f"[CLIENT_HANDLER] Handshake completo con {self.address}")
            self.rdt.sequence_number = 0
            self.rdt.ack_number = 0
            if self.is_download:
                self.handle_download()
            else:
                self.handle_upload()
        except Exception as e:
            self.logger.error(f"[CLIENT_HANDLER] Error en la transferencia: {e}")


    def handle_upload(self):
        """Lógica para manejar la subida de archivos desde el cliente."""

        filepath = os.path.join(self.storage_dir, self.filename)

        
        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE:
            raise MaxSizeFileError(f"El archivo {filepath} supera el tamaño máximo permitido de {MAX_FILE_SIZE} bytes")
        
        with open(filepath, 'wb') as f:  
            while True:
                packet = self.rdt.recv(self.stream)
                if packet.is_fin():
                    break
                f.write(packet.get_payload())

        self.logger.info(f"[CLIENT_HANDLER] Archivo recibido correctamente: {filepath}")


    def handle_download(self):
        """Lógica para manejar la descarga de archivos hacia el cliente."""
        
        filepath = os.path.join(self.storage_dir, self.filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo {filepath} no existe")

        with open(filepath, "rb") as f:
            data = f.read(PAYLOAD_SIZE)
            while data:
                packet = Packet.new_regular_packet(data, DOWNLOAD)
                packet.download = DOWNLOAD
                self.rdt.send(packet, self.stream)
                data = f.read(PAYLOAD_SIZE)
                
            fin_packet = Packet.new_fin_packet()
            self.rdt.send(fin_packet, self.stream)

        self.logger.info("[CLIENT_HANDLER] Download completed")

    def enqueue(self, packet):
            self.stream.enqueue(packet)
        
    def is_alive(self):
        return super().is_alive()