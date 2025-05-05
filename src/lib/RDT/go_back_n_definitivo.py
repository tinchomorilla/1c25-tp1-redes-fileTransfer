import threading
import time
import queue
from socket import timeout
from lib.Common.constants import *
from lib.Packet.packet import Packet
from lib.RDT.ack_handler import ACKHandler
from lib.RDT.handshake import Protocol


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

    def start_transmits(self):
        while self.running:
            with self.lock:
                if self.next_seq_number <= self.base + self.window_size:
                    packet = self.sent_packets[self.next_seq_number]
                    if packet:
                        self.logger.debug(f"[GBN Send] Enviando packet {packet.sequence_number}")
                        self.stream.send_to(packet.to_bytes(), self.address)
                        if packet.is_fin():
                            self.logger.debug(f"[GBN Send] Enviando FIN packet {packet.sequence_number}")
                            self.stream.send_to(packet.to_bytes(), self.address)
                            self.running = False
                            return
                        self.next_seq_number += 1
            # Pequeño sleep para no saturar CPU
            #threading.Event().wait(0.2)

    # def send(self, packet, stream):

    #     self.logger.debug(
    #         f"[GBN Send] Esperando para enviar el paquete... seq_num: {self.next_seq_number} base {self.base}"
    #     )
    #     if self.next_seq_number < self.base + self.window_size:
    #         packet.sequence_number = self.next_seq_number
    #         packet.ack_number = 0  # Ignorado por el receptor

    #         self.sent_packets[self.next_seq_number] = packet

    #         stream.send_to(packet.to_bytes(), self.address)
    #         self.logger.debug(
    #             f"[GBN Send] Enviando packet con packet_seq_num {packet.sequence_number} y self.seq_num {self.next_seq_number}"
    #         )

    #         self.next_seq_number += 1
    #         self.logger.debug(f"[GBN Send] Actualizando seq a {self.next_seq_number}")

    #         return
    #     else:
    #         self.handle_full_window()

    # def handle_ack(self, stream):
    #     while True:
    #         self.logger.debug("[GBN ACK] Esperando ACK...")
    #         try:

    #             ack_packet = stream.receive()
    #             self.logger.debug(f"[GBN ACK] Received ACK: {ack_packet}")
    #             if ack_packet.is_ack():
    #                 if ack_packet.get_ack_number() == self.base:
    #                     self.base += 1

    #                     if self.base == self.next_seq_number:
    #                         # El timer se detiene porque ya 
    #                         # no hay paquetes pendientes para enviar
    #                         pass
    #                     else:
    #                         # Se deberia reiniciar el timer  
    #                         # ya que self.base cambio
    #                         pass

    #                 elif ack_packet.get_ack_number() < self.base:
    #                     # No hago nada hasta que salte el timeout de self.base,
    #                     # una vez que salte el timeout, se reenvian todos los paquetes
    #                     # desde self.base
    #                     pass
    #                 elif ack_packet.get_ack_number() > self.base:
    #                     # Confiamos en el Receiver que si me mando un
    #                     # ACK mayor a self.base, es porque ya recibio todos los
    #                     # paquetes anteriores, pero los ACKs se peerdieron en el camino.
    #                     self.base = ack_packet.get_ack_number() + 1
    #                     self.sent_packets = {
    #                         k: v for k, v in self.sent_packets.items() if k >= self.base
    #                     }
    #                     #start timer devuelta ya que base cambio

    #         except timeout:
    #             self.logger.debug("[GBN ACK] Timeout esperando ACK...")
    #             # Timeout, reenviar todos los paquetes desde self.base
    #             continue

    def recv(self, stream):
        while True:
            self.logger.debug("[GBN RECV] Antes del try, esperando paquete...")
            try:
                packet = stream.receive()
                self.logger.debug(
                    f"[GBN RECV] Recibido packet {packet.sequence_number}"
                )
                self.logger.debug(
                    f"[GBN RECV] self.last_ack_number: {self.last_ack_number}"
                )

                if packet.is_fin():
                    self.logger.debug("[GBN RECV] Paquete FIN recibido")
                    ack = Packet.new_ack_packet(
                        self.last_ack_number, packet.sequence_number, None
                    )
                    return packet
                
                if packet.sequence_number == self.last_ack_number:

                    ack = Packet.new_ack_packet(
                        self.last_ack_number, packet.sequence_number, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"[GBN RECV] ACK enviado: {ack}")
                    self.last_ack_number += 1
                    return packet

                else:
                    self.logger.debug(
                        f"[GBN RECV] Paquete fuera de orden: {packet.sequence_number}, esperando {self.last_ack_number}"
                    )
                    ack_number = self.last_ack_number - 1 if self.last_ack_number > 0 else 0
                    ack = Packet.new_ack_packet(
                        self.last_ack_number, ack_number, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    continue

            except (timeout, queue.Empty):
                self.logger.debug("[GBN RECV] Timeoute esperando...")
                ack_number = self.last_ack_number - 1 if self.last_ack_number > 0 else 0
                ack = Packet.new_ack_packet(
                    self.last_ack_number, ack_number, None
                )
                stream.send_to(ack.to_bytes(), self.address)
                continue
