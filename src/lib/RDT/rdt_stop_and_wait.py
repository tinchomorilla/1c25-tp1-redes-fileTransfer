import socket
import struct
import threading
import queue

from lib.constants import *

class StopAndWaitRDT:
    def __init__(self, sock: socket.socket, addr):
        self.sock = sock
        self.addr = addr
        self.seq = 0
        self.timeout = TIMEOUT
        self.queue = queue.Queue()
        self.running = True

        # Lanzar hilo de recepcion interno
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()

    def send(self, data: bytes, pkt_type=TYPE_DATA):
        while True:
            pkt = self._make_packet(pkt_type, self.seq, data)
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
            pkt = self.queue.get()
            pkt_type, pkt_seq, pkt_len = self._parse_header(pkt)
            data = pkt[HEADER_SIZE:HEADER_SIZE + pkt_len]

            if pkt_type == TYPE_DATA and pkt_seq == self.seq:
                ack = self._make_packet(TYPE_ACK, self.seq, b'')
                self.sock.sendto(ack, self.addr)
                self.seq ^= 1
                return data
            elif pkt_type == TYPE_DONE:
                ack = self._make_packet(TYPE_ACK, pkt_seq, b'')
                self.sock.sendto(ack, self.addr)
                self.seq ^= 1
                return RDT_DONE_MARKER
            else:
                dup_ack = self._make_packet(TYPE_ACK, self.seq ^ 1, b'')
                self.sock.sendto(dup_ack, self.addr)

    def close(self):
        self.running = False
        self.listener_thread.join(timeout=0.1)

    def _listen_loop(self):
        while self.running:
            try:
                pkt, addr = self.sock.recvfrom(1024)
                if addr == self.addr:
                    self.queue.put(pkt)
            except Exception:
                continue

    def _make_packet(self, pkt_type: int, seq: int, data: bytes) -> bytes:
        header = struct.pack(HEADER_FMT, pkt_type, seq, len(data))
        return header + data

    def _parse_header(self, pkt: bytes):
        return struct.unpack(HEADER_FMT, pkt[:HEADER_SIZE])

class RDTListener:
    def __init__(self, bind_addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(bind_addr)
        self.lock = threading.Lock()
        self.handlers = {}

    def accept(self):
        pkt, addr = self.sock.recvfrom(1024)
        with self.lock:
            if addr not in self.handlers:
                print(f"[SERVER] Cliente nuevo {addr}: {pkt}")
                rdt = StopAndWaitRDT(self.sock, addr)
                self.handlers[addr] = rdt
            else:
                rdt = self.handlers[addr]
        pkt_type, pkt_seq, pkt_len = struct.unpack(HEADER_FMT, pkt[:HEADER_SIZE])
        payload = pkt[HEADER_SIZE:HEADER_SIZE + pkt_len]

        return rdt, payload
