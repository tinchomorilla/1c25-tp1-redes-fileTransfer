import queue
from lib.Common.constants import *
from lib.Packet.packet import Packet
from socket import *

from lib.RDT.handshake import Protocol

class GoBackN(Protocol):
    def __init__(self, address, logger):
        super().__init__(address, logger)
        self.packet_window = {}  # seq_num -> packet

    def send(self, packet, stream):
        packet.sequence_number = self.sequence_number
        packet.ack_number = self.ack_number

        if len(self.packet_window) < WINDOW_SIZE:
            stream.send_to(packet.to_bytes(), self.address)
            self.logger.debug(f"[GBN] Packet sent ({packet})")
            self.packet_window[packet.sequence_number] = packet
            self.sequence_number += 1
        else:
            self._wait_ack(stream)
            self.send(packet, stream)  # intentar nuevamente luego de liberar ventana

        if packet.is_fin():
            self._wait_all_acks(stream)

    def _wait_ack(self, stream):
        retries = 0
        while retries < MAX_RETRANSMITS:
            try:
                ack_packet = stream.receive()
                self.logger.debug(f"[GBN] Received ACK: {ack_packet}")
                if ack_packet.is_ack():
                    ack_num = ack_packet.ack_number
                    # Avance acumulativo
                    keys_to_remove = [seq for seq in self.packet_window if seq < ack_num]
                    for seq in keys_to_remove:
                        del self.packet_window[seq]
                    self.logger.debug(f"[GBN] ACK up to {ack_num - 1}, base advanced")
                    return
            except (timeout, queue.Empty):
                self.logger.debug("[GBN] Timeout, resending all unacked packets")
                self._resend_all(stream)
                retries += 1

    def _resend_all(self, stream):
        for seq in sorted(self.packet_window.keys()):
            pkt = self.packet_window[seq]
            stream.send_to(pkt.to_bytes(), self.address)
            self.logger.debug(f"[GBN] Re-sent packet {pkt.sequence_number}")

    def recv(self, stream):
        retries = 0
        while retries < RETRIES:
            try:
                packet = stream.receive()
                self.logger.debug(f"[GBN] Received packet {packet.sequence_number}, expected {self.sequence_number}")

                if packet.sequence_number == self.sequence_number:
                    ack = Packet.new_ack_packet(
                        self.sequence_number, packet.sequence_number + 1, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"[GBN RECV] ACK enviado: {ack}")
                    
                    self.sequence_number += 1
                    self.logger.debug(f"[GBN RECV] self.seq_num actualizado a {self.sequence_number}")
                    return packet
                elif packet.sequence_number > self.sequence_number:
                    self.logger.debug(
                        f"[GBN RECV] Paquete fuera de orden. Paquete recibido mas grande que self.seq_num."
                    )
                    ack = Packet.new_ack_packet(
                        packet.sequence_number, self.sequence_number - 1, None
                    )
                    self.logger.debug(f"[GBN RECV] ACK enviado: {ack}")
                    stream.send_to(ack.to_bytes(), self.address)
                elif packet.sequence_number < self.sequence_number:
                    self.logger.debug("[GBN RECV] Paquete mas chico que self.seq_num")
                    ack = Packet.new_ack_packet(
                        self.sequence_number, self.sequence_number-1, None
                    )
                    self.logger.debug(f"[GBN RECV] ACK enviado: {ack}")
                    stream.send_to(ack.to_bytes(), self.address)
            except (timeout, queue.Empty):
                ack = Packet.new_ack_packet(self.sequence_number, self.sequence_number-1, None)
                stream.send_to(ack.to_bytes(), self.address)
                self.logger.debug(f"[GBN] Timeout. Re-sent ACK {ack}")
                retries += 1

    def _wait_all_acks(self, stream):
        retries = 0
        while len(self.packet_window) > 0 and retries < MAX_RETRANSMITS:
            self.logger.debug("[GBN] Waiting for remaining ACKs")
            self._wait_ack(stream)
            retries += 1
