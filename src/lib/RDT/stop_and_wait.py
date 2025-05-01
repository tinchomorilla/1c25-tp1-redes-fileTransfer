import socket
import struct
from lib.constants import *

class StopAndWaitRDT:
    def __init__(self, sock: socket.socket, addr=None, queue=None):
        self.sock = sock
        self.addr = addr
        self.queue = queue  # <-- la cola de paquetes entrantes
        self.seq = 0
        self.timeout = TIMEOUT
        self.sock.settimeout(self.timeout)

    def send(self, data: bytes):
        while True:
            pkt = self._make_packet(TYPE_DATA, self.seq, data)
            self.sock.sendto(pkt, self.addr)
            print(f"[RDT] Paquete enviado: {self.addr} de SEQ {self.seq}")
            try:
                print(f"[RDT] Esperando ACK...")
                ack_pkt, ack_addr = self.sock.recvfrom(1024)
                ack_type, ack_seq, _ = self._parse_header(ack_pkt)
                print(f"[RDT] ACK recibido: {ack_type}")
                if ack_type == TYPE_ACK and ack_seq == self.seq and ack_addr == self.addr:
                    self.seq ^= 1
                    return
            except socket.timeout:
                continue

    def recv(self) -> bytes:
        while True:
            pkt = self.queue.get()  
            print(f"[RDT] Paquete desencolado de: {self.addr}")
           
            pkt_type, pkt_seq, pkt_len = self._parse_header(pkt)
            data = pkt[HEADER_SIZE:HEADER_SIZE + pkt_len]

            print(f"[RDT] Paquete recibido: {pkt_type} de SEQ {pkt_seq} con longitud {pkt_len}")

            if pkt_type == TYPE_DATA and pkt_seq == self.seq:
                ack = self._make_packet(TYPE_ACK, self.seq, b'')
                print(f"[RDT] ACK enviado: {self.seq}")
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
