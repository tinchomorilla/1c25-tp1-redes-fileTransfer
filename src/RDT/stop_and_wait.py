import socket
import struct
import time

# Tipos de mensaje
TYPE_DATA = 0
TYPE_ACK = 1

# Formato del encabezado: !BBH = (tipo, secuencia, longitud)
HEADER_FMT = "!BBH"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
TIMEOUT = 10.0  # segundos
MAX_DATA_SIZE = 1024 - HEADER_SIZE

class StopAndWaitRDT:
    def __init__(self, sock: socket.socket, addr=None, is_sender=True):
        self.sock = sock
        self.addr = addr
        self.is_sender = is_sender
        self.seq = 0
        self.sock.settimeout(TIMEOUT)

    def send(self, data: bytes):
        """Envia un fragmento de datos y espera su ACK"""
        while True:
            pkt = self._make_packet(TYPE_DATA, self.seq, data)
            print(f"[RDT] Enviando paquete: {self.seq}, longitud: {len(data)}")
            self.sock.sendto(pkt, self.addr)
            try:
                ack_pkt, _ = self.sock.recvfrom(1024)
                ack_type, ack_seq, _ = self._parse_header(ack_pkt)
                if ack_type == TYPE_ACK and ack_seq == self.seq:
                    print(f"[RDT] ACK recibido: {ack_seq} para SEQ: {self.seq}")
                    self.seq ^= 1  # toggle seq
                    return
            except socket.timeout:
                print(f"[RDT] Timeout esperando ACK, reintentando...")

    def recv(self) -> tuple[bytes, tuple]:
        """Recibe un fragmento de datos válido y envía ACK"""
        while True:
            try:
                pkt, addr = self.sock.recvfrom(1024)
                pkt_type, pkt_seq, pkt_len = self._parse_header(pkt)
                data = pkt[HEADER_SIZE:HEADER_SIZE + pkt_len]

                if pkt_type == TYPE_DATA and pkt_seq == self.seq:
                    ack = self._make_packet(TYPE_ACK, self.seq, b'')
                    self.sock.sendto(ack, addr)
                    self.seq ^= 1
                    return data, addr
                else:
                    # ACK duplicado por si el otro no lo recibió
                    dup_ack = self._make_packet(TYPE_ACK, self.seq ^ 1, b'')
                    self.sock.sendto(dup_ack, addr)
            except socket.timeout:
                continue  # Seguimos esperando

    def _make_packet(self, pkt_type: int, seq: int, data: bytes) -> bytes:
        header = struct.pack(HEADER_FMT, pkt_type, seq, len(data))
        return header + data

    def _parse_header(self, pkt: bytes):
        return struct.unpack(HEADER_FMT, pkt[:HEADER_SIZE])
