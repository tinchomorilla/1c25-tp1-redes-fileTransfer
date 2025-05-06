import threading
import time
import queue
from socket import timeout
from lib.Common.constants import *
from lib.Packet.packet import Packet
from lib.RDT.ack_handler import ACKHandler
from lib.RDT.handshake import Protocol

FIRST_ACK_RECEIVED = True

class GoBackN(Protocol):
    def __init__(self, address, logger):
        super().__init__(address, logger)
        self.window_size = WINDOW_SIZE
        self.next_seq_number = 0
        self.last_ack_number = 0
        self.base = 0
        self.sent_packets = []  # seq_num -> packet
        self.lock = threading.Lock()
        self.running = True
        self.stream = None
        self.logger = logger

    def generate_packets(self, src):
        """
        Genereate packets to be sent.
        """

        with open(src, "rb") as f:
            sequence_number = 0
            while True:
                # Read data such that
                # size of data chunk should not exceed maximum payload size
                data = f.read(PAYLOAD_SIZE)

                # If not data, finish reading
                if not data:
                    fin_packet = Packet.new_fin_packet()
                    fin_packet.sequence_number = sequence_number
                    self.sent_packets.append(fin_packet)
                    self.logger.error(f"[GBN Send] Lectura de archivo finalizada")
                    break

                # Create a packet with the data
                pkt = Packet.new_regular_packet(data, None)
                pkt.sequence_number = sequence_number
                self.sent_packets.append(pkt)
                sequence_number += 1

    def send(self, src, stream):
        if self.stream is None:
            self.stream = stream

        self.generate_packets(src)

        ack_thread = ACKHandler(self)
        ack_thread.start()

        self.start_transmits()
        # ack_thread.join()

    def start_transmits(self):
        while self.running:
            with self.lock:
                if self.next_seq_number <= self.base + self.window_size:
                    packet = self.sent_packets[self.next_seq_number]
                    if packet:
                        self.logger.debug(
                            f"[GBN Send] Enviando packet {packet.sequence_number}"
                        )
                        self.stream.send_to(packet.to_bytes(), self.address)
                        self.next_seq_number += 1
                
                    
               
                

    def recv(self, stream):
        while True:
            # self.logger.debug("[GBN RECV] Antes del try, esperando paquete...")
            try:
                packet = stream.receive()
                self.logger.debug(
                    f"[GBN RECV] Recibido packet {packet.sequence_number}"
                )
                self.logger.debug(
                    f"[GBN RECV] self.last_ack_number: {self.last_ack_number}"
                )

                if packet.sequence_number == self.last_ack_number:
                    self.logger.debug(
                        f"[GBN RECV] Paquete en orden: {packet.sequence_number}, esperando {self.last_ack_number}"
                    )

                    ack = None

                    if packet.is_fin():
                        self.logger.debug("[GBN RECV] Paquete FIN recibido")
                        ack = Packet.new_fin_packet()
                    else:
                        ack = Packet.new_ack_packet(
                            self.last_ack_number, packet.sequence_number, FIRST_ACK_RECEIVED
                        )
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"[GBN RECV] ACK enviado: {ack}")
                    self.last_ack_number += 1
                    return packet

                else:
                    self.logger.debug(
                        f"[GBN RECV] Paquete fuera de orden: {packet.sequence_number}, esperando {self.last_ack_number}"
                    )
                    self.logger.debug(
                        f"[GBN RECV] self.last_ack_number: {self.last_ack_number}"
                    )

                    ack_number = (
                        self.last_ack_number - 1 if self.last_ack_number > 0 else 0
                    )

                    ack = Packet.new_ack_packet(self.last_ack_number, ack_number, False)
                    self.logger.debug(f"[GBN RECV] ACK enviado en el ELSE: {ack}")
                    stream.send_to(ack.to_bytes(), self.address)
                    continue

            except (timeout, queue.Empty):
                self.logger.debug("[GBN RECV] Timeoute esperando...")
                ack = self.make_ack_packet()
                stream.send_to(ack.to_bytes(), self.address)
                continue

    def make_ack_packet(self):
        ack_number = self.last_ack_number - 1 if self.last_ack_number > 0 else 0
        if self.last_ack_number == 0:
            # Si todavia no se recibio el primer paquete y hubo timeout,
            # se envia un ACK como siempre, pero
            # se pone un flag en False para que el receptor sepa que es el primer ACK
            # y que el paquete 0 en realidad NO fue recibido, si no que hubo un timeout
            # y el primer paquete se perdio.
            ack = Packet.new_ack_packet(self.last_ack_number, ack_number, not FIRST_ACK_RECEIVED)
        else:
            ack = Packet.new_ack_packet(self.last_ack_number, ack_number, False)

        return ack
