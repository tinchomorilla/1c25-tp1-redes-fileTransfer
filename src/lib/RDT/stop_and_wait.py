import socket
import struct

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
    def __init__(self, sock: socket.socket, addr=None, queue=None):
        self.sock = sock
        self.addr = addr
        self.queue = queue
        self.seq = 0

    def send(self, data: bytes, type: int):
        """Envía datos utilizando el protocolo Stop-and-Wait."""
        while True:
            print("[RDT] Creando paquete...")
            pkt = self._make_packet(type, self.seq, data)
            print(f"[RDT] Enviando paquete: tipo={type}, seq={self.seq}, len={len(data)}")
            self.sock.sendto(pkt, self.addr)
            if self._wait_for_ack():
                return

    def _wait_for_ack(self) -> bool:
        """Espera un ACK válido y verifica si es duplicado."""
        try:
            self.sock.settimeout(TIMEOUT)
            print(f"[RDT] Esperando ACK...")
            ack_pkt, ack_addr = self.sock.recvfrom(1024)
            ack_type, ack_seq, _ = self._parse_header(ack_pkt)
            print(f"[RDT] ACK recibido: tipo={ack_type}, seq={ack_seq}")

            if ack_type == TYPE_INIT_ACK:
                print(f"[RDT] ACK de inicialización recibido")
                return True

            if ack_type == TYPE_ACK and ack_seq == self.seq and ack_addr == self.addr:
                print(f"[RDT] ACK válido recibido para SEQ={self.seq}")
                self.seq ^= 1  # Alterna el número de secuencia
                return True
        except socket.timeout:
            print(f"[RDT] Timeout esperando ACK, reenviando paquete...")
            return False

    def recv_server(self) -> bytes:
        while True:

            pkt = self.queue.get() 
            if not pkt:
                print(f"[RDT] Cola vacía, esperando...")
                continue
        
            print(f"[RDT] Paquete desencolado de: {self.addr}")

            pkt_type, pkt_seq, pkt_len = self._parse_header(pkt)
            data = pkt[HEADER_SIZE : HEADER_SIZE + pkt_len]

            if pkt_type == TYPE_INIT:
                print(f"[RDT] Paquete de inicialización recibido")
                init_ack = self._make_packet(TYPE_INIT_ACK, self.seq, b"")
                self.sock.sendto(init_ack, self.addr)
                print(f"[RDT] ACK de inicialización enviado: {self.seq}")
                return data

            if pkt_type == TYPE_DATA and pkt_seq == self.seq:
                ack = self._make_packet(TYPE_ACK, self.seq, b"")
                print(f"[RDT] ACK enviado: {self.seq}")
                self.sock.sendto(ack, self.addr)
                self.seq ^= 1
                return data
            else:
                dup_ack = self._make_packet(TYPE_ACK, self.seq ^ 1, b"")
                self.sock.sendto(dup_ack, self.addr)

    def recv_client(self) -> bytes:
        while True:
            try:
                self.sock.settimeout(TIMEOUT)
                pkt, addr = self.sock.recvfrom(1024)
                print(f"[RDT] Paquete recibido de: {addr}")
            except socket.timeout:
                print(f"[RDT] Timeout alcanzado, continuando...")
                continue

            pkt_type, pkt_seq, pkt_len = self._parse_header(pkt)
            data = pkt[HEADER_SIZE:HEADER_SIZE + pkt_len]

            if pkt_type == TYPE_DATA and pkt_seq == self.seq:
                ack = self._make_packet(TYPE_ACK, self.seq, b'')
                print(f"[RDT] ACK enviado: {self.seq}")
                self.sock.sendto(ack, addr)
                self.seq ^= 1
                return data
            else:
                dup_ack = self._make_packet(TYPE_ACK, self.seq ^ 1, b'')
                self.sock.sendto(dup_ack, addr)

    def _make_packet(self, pkt_type: int, seq: int, data: bytes) -> bytes:
        header = struct.pack(HEADER_FMT, pkt_type, seq, len(data))
        return header + data

    def _parse_header(self, pkt: bytes):
        return struct.unpack(HEADER_FMT, pkt[:HEADER_SIZE])

   