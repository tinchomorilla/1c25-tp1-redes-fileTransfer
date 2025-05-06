from socket import timeout
import threading
import time
import queue
from lib.Common.constants import *
from lib.Packet.packet import Packet
from lib.RDT.handshake import Protocol


class GoBackN(Protocol):
    def __init__(self, address, logger):
        super().__init__(address, logger)
        self.window_size = WINDOW_SIZE
        self.packet_buffer = []
        self.sent_packets = {}
        self.base = 0
        self.timer = None
        self.ack_listener_thread = None
        # self.next_seq_num = 0
        # Si recibimos el ACK "n" significa que todos los paquetes hasta "n"
        # han sido recibidos correctamente del lado del receptor
        self.ack_listener_thread_running = False
        self.all_acks_received = threading.Event()
        self.is_fin = False

    def send(self, packet, stream):
        if not self.ack_listener_thread_running:
            self.ack_listener_thread_running = True
            self.start_ack_listener(stream)

        self.is_fin = packet.is_fin()

        while True:
            if self.sequence_number < self.base + self.window_size:
                packet.sequence_number = self.sequence_number
                packet.ack_number = self.ack_number
                self.sent_packets[self.sequence_number] = packet
                print(
                    f"[GBN Send] Enviando packet con packet_seq_num {packet.sequence_number} y self.seq_num {self.sequence_number}"
                )
                stream.send_to(packet.to_bytes(), self.address)
                self.logger.info(f"[GBN Send] Sent packet {packet.sequence_number}")
                if self.base == self.sequence_number:
                    # Si es el primer paquete enviado de la ventana,
                    # inicio el temporizador
                    print(f"[GBN Send] Iniciando temporizador para el paquete")
                    self.start_timer(stream)
                self.sequence_number += 1
                print("[GBN Send] Actualizando self.seq_num a", self.sequence_number)
                break
            else:
                print(
                    "[GBN Send] Ventana llena, self.sequence_number:",
                    self.sequence_number,
                    "base:",
                    self.base,
                )
                self.logger.info(f"[GBN Send] Ventana llena, esperando y reintentando")
                time.sleep(0.1)

    def start_ack_listener(self, stream):
        self.ack_listener_thread = threading.Thread(
            target=self._listen_for_acks, args=(stream,), daemon=True
        ).start()

    def _listen_for_acks(self, stream):
        print("[GBN-LISTEN_FOR_ACKS] Antes de entrar al while")
        #time.sleep(3)
        while True:
            print("[GBN-LISTEN_FOR_ACKS] Esperando ACKs")
            try:
                packet = stream.receive()
                print(f"[GBN-LISTEN_FOR_ACKS] Recibido el packet {packet}. ANTES DEL IF ACK")
                if packet.is_ack():
                    # Handle the ACK packet
                    ack_num = packet.ack_number
                    self.ack_number = ack_num
                    print(f"[GBN-LISTEN_FOR_ACKS] Recibido el ACK {ack_num}")
                    print(f"[GBN-LISTEN_FOR_ACKS] self.base vale: {self.base}")
                    if ack_num == self.base:
                        self.sent_packets.pop(self.base, None)
                        self.base += 1
                        self.start_timer(stream)

                    elif ack_num < self.base:
                        print(
                            f"[GBN-LISTEN_FOR_ACKS] ACK {ack_num} < self.base {self.base}"
                        )
                        print(f"[GBN-LISTEN_FOR_ACKS] Reenviando paquetes")
                        self._resend_packets(stream)

                    elif ack_num > self.base:
                        self.base = ack_num + 1
                        self.sent_packets = {
                            k: v for k, v in self.sent_packets.items() if k >= self.base
                        }

                        if self.base == self.sequence_number:
                            print(
                                "[GBN-LISTEN_FOR_ACKS] Todos los paquetes fueron reconocidos, frenando el timer"
                            )
                            self.stop_timer()
                            #self.all_acks_received.set()
                        else:
                            print(
                                "[GBN-LISTEN_FOR_ACKS] Faltan paquetes por ACKear, reiniciando timer"
                            )
                            self.start_timer(stream)
                            #self.all_acks_received.clear()

                # if self.is_fin:
                #     self.stop_timer()
                #     self.ack_listener_thread.close()
                #     break

            except (timeout, queue.Empty):
                print()
                continue

    def wait_until_done(self, timeout=None):
        self.all_acks_received.wait(timeout=timeout)

    def start_timer(self, stream):
        if self.timer is not None:
            self.timer.cancel()
            print("[GBN-TIMER] Timer cancelado")
        self.timer = threading.Timer(TIMEOUT_ACK, self._resend_packets, [stream])
        print(
            f"[GBN-TIMER] Starting timer for packets {self.base} to {self.sequence_number}"
        )
        self.timer.start()

    def stop_timer(self):
        print(f"[GBN-TIMER] Stopping timer")
        if self.timer is not None:
            self.timer.cancel()
        else:
            print("[GBN-TIMER] Timer already stopped or not started")

    def _resend_packets(self, stream):
        for i in range(self.base, self.sequence_number-1):
            print(f"[GBN-RESEND] Reenviando el paquete {i}")
            packet = self.sent_packets[i]
            print(f"[GBN-RESEND] Paquete a reenviar: {packet}")
            stream.send_to(packet.to_bytes(), self.address)
            self.logger.info(f"Reenviando el paquete {packet.sequence_number}")
            
        print(f"[GBN-RESEND] Reiniciando el timer")
        self.start_timer(stream)
    
    def recv(self, stream):
        while True:
            try:
                packet = stream.receive()
                self.logger.debug(f"[GBN-RECV] Se recibio el packet: {packet}")
                print(
                    f"[GBN-RECV] Recibido packet {packet.sequence_number} con ack {packet.ack_number}"
                )
                print("[GBN-RECV] self.seq_num vale: ", self.sequence_number)
                if  packet.sequence_number == self.sequence_number:
                    ack = Packet.new_ack_packet(
                        self.sequence_number, packet.sequence_number, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    print(f"[GBN-RECV] Enviando ACK para el ack {ack}")
                    self.sequence_number += 1
                    return packet
                elif packet.sequence_number > self.sequence_number:
                    print(
                        f"[GBN-RECV] El paquete fuera de orden es {packet.sequence_number}"
                    )
                    print(f"[GBN-RECV] El paquete esperado es {self.sequence_number-1}")
                    ack = Packet.new_ack_packet(
                        self.sequence_number, self.sequence_number-1, None
                    )
                    stream.send_to(ack.to_bytes(), self.address)
                    
                    
            except (timeout, queue.Empty):
                self.logger.warning("[GBN-RECV] Timeout al recibir packets.")
                print("[GBN-RECV] Timeout al recibir packets.")



