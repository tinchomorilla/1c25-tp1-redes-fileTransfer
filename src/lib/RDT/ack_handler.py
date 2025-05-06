import queue
from socket import timeout
from threading import Thread, Timer
import threading
import time


class ACKHandler(Thread):
    """
    Thread for monitoring acknowledgement receipt.
    """

    def __init__(self, gbn_protocol):
        super().__init__()
        self.gbn = gbn_protocol
        self.timer = None
        self.base_timeout_interval = 0.01
        self.timeout_interval = 0.01

    def run(self):
        while self.gbn.running:
            self.gbn.logger.debug("[GBN ACK] Esperando ACK...")
            try:
                ack_packet = self.gbn.stream.receive()
                if ack_packet.is_fin():
                    self.gbn.logger.debug("[GBN ACK] Received FIN")
                    self.gbn.running = False
                    break
                if ack_packet.is_ack():
                    self.gbn.logger.debug(f"[GBN ACK] Received ACK: {ack_packet}")
                    self.gbn.logger.debug("[GBN ACK] self.gbn.base: %d", self.gbn.base)
                    with self.gbn.lock:
                        if ack_packet.first_ack_was_received_correctly() and self.gbn.base == 0:
                            # Si el ACK es el primero y la base es 0, significa que
                            # el receptor ha recibido el primer paquete
                            # y el timer se inicia.
                            self.update_base_with(increase_by_1=True)
                        elif ack_packet.get_ack_number() == self.gbn.base and self.gbn.base > 0:
                            self.update_base_with(increase_by_1=True)
                        elif ack_packet.get_ack_number() < self.gbn.base:
                            # No hago nada hasta que salte el timeout de self.gbn.base,
                            # una vez que salte el timeout, se reenvian todos los paquetes
                            # desde self.gbn.base
                            pass
                        elif ack_packet.get_ack_number() > self.gbn.base:
                            # Confiamos en el Receiver que si me mando un
                            # ACK mayor a self.gbn.base, es porque ya recibio todos los
                            # paquetes anteriores, pero los ACKs se peerdieron en el camino.
                            self.update_base_with(ack_packet.get_ack_number() + 1)   
                                                     
            except (timeout, queue.Empty):
                self.gbn.logger.debug("[GBN ACK] Timeout esperando ACK...")
                
                #self.timeout_handler()
                continue

    def start_timer(self, bool=None):
        if self.timer:
            self.timer.cancel()
        if bool:
            self.timer = Timer(self.base_timeout_interval, self.timeout_handler)
        else:
            self.timer = Timer(self.timeout_interval, self.timeout_handler)
        self.gbn.logger.debug(
            f"[GBN ACK] Timer started with interval: {self.timeout_interval}"
        )
        self.timer.start()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def timeout_handler(self):
        with self.gbn.lock:
            self.gbn.logger.debug(
                f"[GBN] Timeout: reenviando desde base {self.gbn.base} hasta {self.gbn.next_seq_number}"
            )
            # time.sleep(0.1)
            for seq in range(self.gbn.base, self.gbn.next_seq_number):
                pkt = self.gbn.sent_packets[seq]
                self.gbn.logger.debug(
                    f"[GBN Resend] Reenviando packet {pkt.sequence_number}"
                )
                self.gbn.stream.send_to(pkt.to_bytes(), self.gbn.address)

    def update_base_with(self, increment=None, increase_by_1=False):
        """
        Actualiza self.gbn.base dependiendo del caso.
        :param ack_number: Por defecto es None.
        :param increment: Si es True, incrementa self.gbn.base en 1.
                          Si es False, asigna ack_number + 1.
        """
        if increase_by_1:
            self.gbn.base += 1
            self.gbn.logger.debug(f"[GBN ACK] Incrementando base a {self.gbn.base}")
        else:
            self.gbn.base = increment
            self.gbn.logger.debug(
                f"[GBN ACK] Actualizando base a {self.gbn.base} con ACK {increment-1}"
            )

        if self.gbn.base == self.gbn.next_seq_number:
            # El timer se detiene porque ya
            # no hay paquetes pendientes para enviar
            self.stop_timer()
        else:
            # Se deberia reiniciar el timer
            # ya que self.gbn.base cambio
            self.start_timer(bool=True)
