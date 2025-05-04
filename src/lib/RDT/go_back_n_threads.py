import threading
import time
import queue
from socket import timeout
from lib.Common.constants import *
from lib.Packet.packet import Packet
from lib.RDT.handshake import Protocol


class GoBackN(Protocol):
    def __init__(self, address, logger):
        super().__init__(address, logger)
        self.window_size = WINDOW_SIZE
        self.sent_packets = {}  # seq_num -> packet
        self.base = 0
        self.sequence_number = 0

        self.ack_received_event = threading.Event()
        self.timeout_event = threading.Event()
        self.stop_event = threading.Event()

        self.lock = threading.Lock()

        self.resend_thread = None
        self.ack_thread = None

        self.stream = None

    def send(self, packet, stream):
        if self.stream is None:
            self.stream = stream
            self.start_threads()
            

        while True:
            with self.lock:
                if self.sequence_number < self.base + self.window_size:
                    packet.sequence_number = self.sequence_number
                    packet.ack_number = 0  # Ignorado por el receptor

                    self.sent_packets[self.sequence_number] = packet

                    stream.send_to(packet.to_bytes(), self.address)
                    self.logger.debug(
                        f"[GBN Send] Enviando packet con packet_seq_num {packet.sequence_number} y self.seq_num {self.sequence_number}"
                    )

                    if self.base == self.sequence_number:
                        self.logger.debug(f"[GBN Send] Iniciando temporizador para el paquete")
                        self.timeout_event.set()  # Activar temporizador
                    
                    self.sequence_number += 1
                    self.logger.debug(f"[GBN Send] Actualizando {self.sequence_number} a")
                    break
            #print(f"[GBN Send] Sequence number: { self.sequence_number} Base: {self.base}")
            time.sleep(0.01)


    def recv(self, stream):
        while True:
            self.logger.debug("[GBN RECV] Antes del try, esperando paquete...")
            try:
                packet = stream.receive()
                self.logger.debug(f"[GBN RECV] Recibido packet {packet.sequence_number}")
                self.logger.debug(f"[GBN RECV] self.sequence_number: {self.sequence_number}")
                if packet.sequence_number == self.sequence_number:

                    ack = Packet.new_ack_packet(
                        self.sequence_number, packet.sequence_number, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"[GBN RECV] ACK enviado: {ack}")
                    self.sequence_number += 1
                    return packet
                elif packet.sequence_number > self.sequence_number:
                    ack = Packet.new_ack_packet(
                        packet.sequence_number, self.sequence_number - 1, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(
                        f"[GBN RECV] Paquete fuera de orden. Paquete recibido mas grande que self.seq_num."
                    )
                elif packet.sequence_number < self.sequence_number:
                    self.logger.debug("[GBN RECV] Paquete mas chico que self.seq_num")
                    ack = Packet.new_ack_packet(
                        self.sequence_number, self.sequence_number-1, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
            except (timeout, queue.Empty):
                self.logger.debug("[GBN RECV] Timeout o cola vacía. Esperando...")
                continue

    def start_threads(self):
        self.ack_thread = threading.Thread(target=self._listen_for_acks, daemon=True)
        self.ack_thread.start()
        self.resend_thread = threading.Thread(target=self._resend_loop, daemon=True)
        self.resend_thread.start()

    def _listen_for_acks(self):
        self.logger.debug("[GBN-LISTEN_FOR_ACKS] Antes de entrar al while")
        while True:
            self.logger.debug("[GBN-LISTEN_FOR_ACKS] Esperando ACKs")
            try:
                packet = self.stream.receive()
                self.logger.debug(
                    f"[GBN-LISTEN_FOR_ACKS] Recibido el packet {packet}. ANTES DEL IF ACK"
                )
                if packet.is_ack():
                    ack_num = packet.ack_number
                    self.ack_number = ack_num
                    self.logger.debug(f"[GBN-LISTEN_FOR_ACKS] Recibido el ACK {ack_num}")
                    self.logger.debug(f"[GBN-LISTEN_FOR_ACKS] self.base vale: {self.base}")

                    with self.lock:
                        if ack_num == self.base:
                            self.sent_packets.pop(self.base, None)
                            self.base += 1
                            self.timeout_event.set()

                        elif ack_num < self.base:
                            self.logger.debug(
                                f"[GBN-LISTEN_FOR_ACKS] ACK {ack_num} < self.base {self.base}"
                            )
                            self.logger.debug(f"[GBN-LISTEN_FOR_ACKS] Reenviando paquetes")
                            #Modificar Variables para que Send vaya para atras
                            #self.sequence_number = self.base
                            self.timeout_event.set()

                        elif ack_num > self.base:
                            self.logger.debug(
                                f"[GBN ACK] Recibido ACK acumulativo hasta {ack_num - 1}"
                            )
                            self.base = ack_num + 1
                            self.sent_packets = {
                                k: v
                                for k, v in self.sent_packets.items()
                                if k >= self.base
                            }
                            if self.base == self.sequence_number:
                                self.timeout_event.clear()
                            else:
                                self.timeout_event.set()

            except (timeout, queue.Empty):
                self.timeout_event.set()
                continue

    def _resend_loop(self):
        while not self.stop_event.is_set():
            self.logger.debug("[GBN RESEND] Esperando timeout...")
            if self.timeout_event.wait(TIMEOUT_ACK):
                self.logger.debug("[GBN RESEND] Antes del lock")
                with self.lock:
                    if self.base < self.sequence_number:
                        self.logger.debug(
                            f"[GBN RESEND] Timeout. Reenviando desde {self.base} hasta {self.sequence_number - 1}"
                        )
                        for seq in range(self.base, self.sequence_number):
                            packet = self.sent_packets.get(seq)
                            if packet:
                                self.stream.send_to(packet.to_bytes(), self.address)
                                self.logger.debug(f"[GBN RESEND] Reenviado packet {seq}")
                    else:
                        self.logger.debug(
                            "[GBN RESEND] Todos los paquetes fueron ACKeados. No se reenvía nada."
                        )
                    self.timeout_event.clear()

    # def _resend_loop(self):
    #     last_sent_time = time.time()

    #     while not self.stop_event.is_set():
    #         time.sleep(0.01)  # pequeño sleep para no hacer busy waiting

    #         with self.lock:
    #             if self.base < self.sequence_number:
    #                 elapsed = time.time() - last_sent_time
    #                 if elapsed >= TIMEOUT_ACK:
    #                     self.logger.debug(
    #                         f"[GBN RESEND] Timeout. Reenviando desde {self.base} hasta {self.sequence_number - 1}"
    #                     )
    #                     for seq in range(self.base, self.sequence_number):
    #                         packet = self.sent_packets.get(seq)
    #                         if packet:
    #                             self.stream.send_to(packet.to_bytes(), self.address)
    #                             self.logger.debug(f"[GBN RESEND] Reenviado packet {seq}")
    #                     last_sent_time = time.time()  # reiniciar timeout
    #             else:
    #                 # Todos los paquetes fueron ACKeados: reiniciar reloj solo si vuelve a haber enviados
    #                 last_sent_time = time.time()

    def stop(self):
        self.logger.debug("[GBN STOP] Deteniendo el protocolo")
        self.stop_event.set()
        self.timeout_event.set()
        if self.ack_thread:
            self.ack_thread.join()
        if self.resend_thread:
            self.resend_thread.join()
