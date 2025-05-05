from socket import timeout
from threading import Thread, Timer
import threading


class ACKHandler(Thread):
    """
    Thread for monitoring acknowledgement receipt.
    """
    def __init__(self, gbn_protocol):
        super().__init__()
        self.gbn = gbn_protocol
        self.timer = None
        self.base_timeout_interval = 0.5  # por ejemplo, 1 segundo
        self.timeout_interval = 0.1

    def run(self):
        while self.gbn.running:
            self.gbn.logger.debug("[GBN ACK] Esperando ACK...")
            try:
                ack_packet = self.gbn.stream.receive()
                if ack_packet.is_ack():
                    self.gbn.logger.debug(f"[GBN ACK] Received ACK: {ack_packet}")
                    with self.gbn.lock:
                        if ack_packet.get_ack_number() == self.gbn.base:
                            self.gbn.base += 1
                            self.gbn.logger.debug(f"[GBN ACK] Actualizando base a {self.gbn.base}")
                            if self.gbn.base == self.gbn.next_seq_number:
                                # El timer se detiene porque ya 
                                # no hay paquetes pendientes para enviar
                                self.stop_timer()
                            else:
                                # Se deberia reiniciar el timer  
                                # ya que self.gbn.base cambio
                                self.start_timer(bool=True)
                                

                        elif ack_packet.get_ack_number() < self.gbn.base:
                            # No hago nada hasta que salte el timeout de self.gbn.base,
                            # una vez que salte el timeout, se reenvian todos los paquetes
                            # desde self.gbn.base
                            pass
                        elif ack_packet.get_ack_number() > self.gbn.base:
                            # Confiamos en el Receiver que si me mando un
                            # ACK mayor a self.gbn.base, es porque ya recibio todos los
                            # paquetes anteriores, pero los ACKs se peerdieron en el camino.
                            self.gbn.base = ack_packet.get_ack_number() + 1
                            self.start_timer(bool=True)
                    

            except timeout:
                self.gbn.logger.debug("[GBN ACK] Timeout esperando ACK...")
                # Timeout de la queue o del socket
                self.start_timer()
                continue

    def start_timer(self, bool=None):
        if self.timer:
            self.timer.cancel()
        if bool:
            self.timer = Timer(self.base_timeout_interval, self.timeout_handler)
        else:
            self.timer = Timer(self.timeout_interval, self.timeout_handler)
        self.gbn.logger.debug(f"[GBN ACK] Timer started with interval: {self.timeout_interval}")
        self.timer.start()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def timeout_handler(self):
            self.gbn.logger.debug("[GBN] Timeout: reenviando desde base...")
            for seq in range(self.gbn.base, self.gbn.next_seq_number):
                pkt = self.gbn.sent_packets[seq]
                self.gbn.logger.debug(f"[GBN Resend] Reenviando packet {pkt.sequence_number}")
                self.gbn.stream.send_to(pkt.to_bytes(), self.gbn.address)
            self.start_timer()
            
