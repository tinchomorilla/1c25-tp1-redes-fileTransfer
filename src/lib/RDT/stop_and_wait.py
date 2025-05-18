from lib.Common.constants import *
from lib.Packet.packet import Packet
from socket import *
import queue

from lib.RDT.handshake import Protocol


class StopAndWait(Protocol):

    def send(self, packet, stream):
        self.logger.debug(f"Preparing packet to {self.address}")

        packet.sequence_number = self.sequence_number
        packet.ack_number = self.ack_number

        stream.send_to(packet.to_bytes(), self.address)
        self.logger.debug(f"Packet sent as ({packet})")
        self._wait_ack(packet, stream)

    def _wait_ack(self, packet, stream):
        self.logger.debug(f"Preparing packet to {self.address}")
        send_count = 0
        while send_count < RETRIES:
            try:
                recv_packet = stream.receive()
                self.logger.debug(f"Received packet as {recv_packet}")

                if (
                    recv_packet.is_fin()
                    and recv_packet.get_ack_number() == self.ack_number
                ):
                    self.logger.debug("Received fin packet")
                    return

                if not recv_packet.is_ack():
                    self.logger.debug("Received unexpected packet")
                    continue

                if recv_packet.get_ack_number() == self.sequence_number + 1:
                    self.logger.debug("Received correct ack packet")
                    self.sequence_number += 1
                    return
                else:
                    self.logger.debug("Receiver sent old ack")
                    stream.send_to(packet.to_bytes(), self.address)
                    self.logger.debug(f"Packet resent as ({packet})")
                    continue

            except (timeout, queue.Empty):
                self.logger.debug(
                    "[SAW_SEND] Timeout event occurred on send. Retrying..."
                )
                stream.send_to(packet.to_bytes(), self.address)
                send_count += 1
                continue

    def recv(self, stream):
        #receive_count = 0
        # while receive_count < RETRIES + 1:
        while True:
            try:
                packet = stream.receive()
                self.logger.debug(f"Received packet as {packet}")
                if packet.is_fin() and packet.sequence_number == self.ack_number:
                    self.logger.debug("Received fin packet")
                    self.ack_number += 1
                    ack = Packet.new_fin_packet()
                    ack.ack_number = self.ack_number
                    stream.send_to(ack.to_bytes(), self.address)
                    self.sequence_number += 1
                    self.logger.debug(f"Sent ack as {ack} DE FIN")
                    return packet

                if not packet.is_ack() and packet.sequence_number == self.ack_number:
                    self.ack_number += 1
                    ack = Packet.new_ack_packet(
                        self.sequence_number, self.ack_number, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"Sent ack as {ack}")
                    return packet
                else:
                    self.logger.debug("[RECV] Ack packet not expected")
                    ack = Packet.new_ack_packet(
                        self.sequence_number, self.ack_number, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"Sent ack as {ack}")

            except (timeout, queue.Empty):
                self.logger.debug("Timeout event occurred on receive. Retrying...")
                ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                stream.send_to(ack.to_bytes(), self.address)
                continue
