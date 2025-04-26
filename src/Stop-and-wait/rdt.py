import socket
import struct
import time

# Tipos de mensaje
TYPE_DATA = 0
TYPE_ACK = 1
TYPE_INIT = 2
TYPE_INIT_ACK = 3
TYPE_READY = 4

# Formato del encabezado: !BBH = (tipo, secuencia, longitud)
HEADER_FMT = "!BBH"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
TIMEOUT = 10.0  # segundos
MAX_DATA_SIZE = 1024 - HEADER_SIZE

class StopAndWaitRDT:
    def __init__(self, sock: socket.socket, addr=None, queue=None, is_sender=True):
        self.sock = sock
        self.addr = addr
        self.queue = queue  # <-- la cola de paquetes entrantes
        self.is_sender = is_sender
        self.seq = 0
        self.timeout = 10.0  # podemos manejar timeout manual si queremos

    def send(self, data: bytes):
        while True:
            pkt = self._make_packet(TYPE_DATA, self.seq, data)
            self.sock.sendto(pkt, self.addr)
            try:
                self.sock.settimeout(self.timeout)
                ack_pkt, ack_addr = self.sock.recvfrom(1024)
                ack_type, ack_seq, _ = self._parse_header(ack_pkt)
                if ack_type == TYPE_ACK and ack_seq == self.seq and ack_addr == self.addr:
                    self.seq ^= 1
                    return
            except socket.timeout:
                continue

    def recv(self) -> bytes:
        while True:
            pkt = self.queue.get()  # ahora leemos de la queue
            pkt_type, pkt_seq, pkt_len = self._parse_header(pkt)
            data = pkt[HEADER_SIZE:HEADER_SIZE + pkt_len]

            if pkt_type == TYPE_DATA and pkt_seq == self.seq:
                ack = self._make_packet(TYPE_ACK, self.seq, b'')
                self.sock.sendto(ack, self.addr)
                self.seq ^= 1
                return data
            else:
                dup_ack = self._make_packet(TYPE_ACK, self.seq ^ 1, b'')
                self.sock.sendto(dup_ack, self.addr)

    def _make_packet(self, pkt_type: int, seq: int, data: bytes) -> bytes:
        header = struct.pack(HEADER_FMT, pkt_type, seq, len(data))
        return header + data

    def _parse_header(self, pkt: bytes):
        return struct.unpack(HEADER_FMT, pkt[:HEADER_SIZE])
