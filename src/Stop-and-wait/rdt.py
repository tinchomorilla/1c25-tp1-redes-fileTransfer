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
    def __init__(self, sock: socket.socket, addr=None, is_sender=True):
        self.sock = sock
        self.addr = addr
        self.is_sender = is_sender
        self.seq = 0
        self.sock.settimeout(TIMEOUT)

    def send(self, data: bytes, pkt_type=TYPE_DATA):
        """Envia un fragmento de datos y espera su ACK"""
        while True:
            pkt = self._make_packet(pkt_type, self.seq, data)
            print(f"[RDT] Enviando paquete tipo {pkt_type}, SEQ: {self.seq}, longitud: {len(data)}")
            self.sock.sendto(pkt, self.addr)
            try:
                ack_pkt, ack_addr = self.sock.recvfrom(1024)
                ack_type, ack_seq, _ = self._parse_header(ack_pkt)
                if ack_type == TYPE_ACK and ack_seq == self.seq:
                    print(f"[RDT] ACK recibido: {ack_seq} para SEQ: {self.seq}")
                    self.seq ^= 1
                    return
            except socket.timeout:
                print("[RDT] Timeout esperando ACK, reintentando...")

    def recv(self) -> tuple[bytes, tuple]:
        """Recibe un fragmento válido y envía ACK si corresponde"""
        while True:
            try:
                pkt, addr = self.sock.recvfrom(1024)
                if self.addr is not None and addr != self.addr:
                    continue  # Ignorar paquetes que no son del cliente esperado

                pkt_type, pkt_seq, pkt_len = self._parse_header(pkt)
                data = pkt[HEADER_SIZE:HEADER_SIZE + pkt_len]

                if pkt_type in [TYPE_DATA, TYPE_INIT, TYPE_READY, TYPE_INIT_ACK]:
                    if pkt_seq == self.seq:
                        ack = self._make_packet(TYPE_ACK, self.seq, b'')
                        self.sock.sendto(ack, addr)
                        self.seq ^= 1
                        return data, addr
                    else:
                        dup_ack = self._make_packet(TYPE_ACK, self.seq ^ 1, b'')
                        self.sock.sendto(dup_ack, addr)
            except socket.timeout:
                continue

    def _make_packet(self, pkt_type: int, seq: int, data: bytes) -> bytes:
        header = struct.pack(HEADER_FMT, pkt_type, seq, len(data))
        return header + data

    def _parse_header(self, pkt: bytes):
        return struct.unpack(HEADER_FMT, pkt[:HEADER_SIZE])
