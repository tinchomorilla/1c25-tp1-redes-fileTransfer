import socket
import sys
from os.path import abspath, dirname
from lib.Packet.packet import Packet
from lib.Server.client_handler import ClientHandler
from lib.Common.constants import PACKET_SIZE

sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))

class Listener:
    def __init__(self, sock, protocol, logger, storage_dir):
        self.sock = sock
        self.protocol = protocol
        self.logger = logger
        self.client_handlers = {}
        self.storage_dir = storage_dir

    def listen(self):
        """Escucha conexiones entrantes y delega el manejo a handle_client."""
        self.logger.info(f"[LISTENER] Listening on {self.sock.getsockname()}")
        while True:
            try:
                data, addr = self.sock.recvfrom(PACKET_SIZE)
                packet = Packet.from_bytes(data)
                self.logger.debug(f"[LISTENER] Received packet from {addr}: {packet}")
                if packet.is_syn() and addr not in self.client_handlers:
                    filename_length = packet.get_payload()[0]
                    filename = packet.get_payload()[1:filename_length + 1].decode('utf-8')
                    handler = ClientHandler(
                        addr,
                        packet.sequence_number,
                        self.protocol,
                        self.logger,
                        filename,
                        packet.is_download(),
                        self.storage_dir
                        )
                    self.client_handlers[addr] = handler
                    self.client_handlers[addr].start()
                else:
                    if(addr in self.client_handlers):
                        self.client_handlers[addr].enqueue(packet)
            except socket.timeout:
                continue

    def verify_threads(self):
            new_threads = {}
            for thread in self.client_handlers.values():
                if not thread.is_alive():
                    del thread
                else:
                    new_threads[thread.address] = thread
            self.client_handlers = new_threads 