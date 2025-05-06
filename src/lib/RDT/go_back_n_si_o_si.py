import queue
from lib.Common.constants import *
from lib.Packet.packet import Packet
from socket import *

from lib.RDT.handshake import Protocol

class GoBackN(Protocol):
    def __init__(self, address, logger):
        super().__init__(address, logger)
        self.packet_window = {}
        
    def send(self, packet, stream):
        packet.sequence_number = self.sequence_number
        packet.ack_number = self.ack_number
        
        if len(self.packet_window) <  WINDOW_SIZE:
            self.logger.debug(f"(ENVIANDO) window size is {len(self.packet_window)}, SEQUENCE NUMB is {packet.sequence_number}")
            stream.send_to(packet.to_bytes(), self.address)
            self.logger.debug(f"Packet sent as ({packet})")
            self.packet_window[packet.sequence_number] = packet
            self.sequence_number += 1
            self.logger.debug(f"(SEND) DENTRO DEL len(self.packet_window) <  WINDOW_SIZE")
            self.logger.debug(f"(SEND) self.packet_window es {self.packet_window.keys()}")
        else:
            self.logger.debug(f"(VENTANA LLENA) Window size is {len(self.packet_window)}, waiting for ack")
            status = self._wait_ack(stream)

            if status==OK:
                stream.send_to(packet.to_bytes(), self.address)
                self.logger.debug(f"Packet sent as ({packet})")
                self.packet_window[packet.sequence_number] = packet
                self.sequence_number += 1
            if status==FIN:
                self.logger.debug(f"(SEND) ESTAMOS EN FIN, ENTRANDO A SEND DE NUEVO ?")
                # self.send(packet, stream)
        if packet.is_fin():
            self._wait_last_packets(stream)

        self.logger.debug(f"(SEND) self.packet_window es {self.packet_window.keys()}")
        

    def recv(self, stream):
        receive_count = 0
                
        while True:
            try:
                packet = stream.receive()
                self.logger.debug(f"(RECV)  Received packet as {packet}")
                self.logger.debug(f"(RECV)  Mi self.ack_number es {self.ack_number}")

                if packet.is_fin() and packet.sequence_number == self.ack_number:
                    self.logger.debug(f"(RECV)  Received FIN packet vale {packet}")
                    self.ack_number += 1
                    ack = Packet.new_fin_packet()
                    ack.sequence_number = self.sequence_number
                    ack.ack_number = self.ack_number
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"(RECV)  Sent FIN Packet ({ack})")
                    self.logger.debug(f"(RECV)  ANTES DEL RETURN EL PAQUETE VALE {packet}")
                    return packet

                if packet.sequence_number == self.ack_number:
                    self.ack_number += 1
                    
                    ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"(RECV)  Sent ack as ({ack})")
                    self.logger.debug(f"(RECV)  ANTES DEL RETURN EL PAQUETE VALE {packet}")
                    return packet
                
                else:
                    # Si el sender me envio un paquete desordenado
                    # es decir, un paquete que no es el que el Receiver esperaba
                    # lo ignoro, pero le aviso cual es el ACK que estoy esperando recibir
                    # Si el Sender me envio un paquete que ya he recibido, lo ignoro
                    # pero le aviso cual es el proximo ACK que estoy esperando recibir
                    self.logger.debug("(RECV)  (INCORRECTO) Received packet ack number is not correct")
                    ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"(RECV)  Sent ack as ({ack})")   

            except (timeout, queue.Empty):
                ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                self.logger.debug(f"(RECV)  Ask for retransmission for ({self.ack_number})")
                stream.send_to(ack.to_bytes(), self.address)
                self.logger.debug("(RECV)  Timeout event occurred on receive. Retrying...")

            receive_count+=1
        
        #self.logger.debug(f"(EXITING RECV) Retries exceeded for receiving packet")
        
    def _wait_last_packets(self, stream):
        retries = 0
        while(len(self.packet_window) > 0 ):
            if(retries >= WINDOW_SIZE):
                self.logger.debug(f"Retransmission limit reached")
                return
            self.logger.debug(f"Waiting last packets")
            self._wait_ack(stream)
            retries +=1


    def _wait_ack(self, stream):
        retries = 0
        while True:
            repeated_ack = 0
            while repeated_ack < MAX_REPEATED_ACKS:   
                try:
                    ack_packet = stream.receive()
                    self.logger.debug(f"Received packet as {ack_packet}")

                    if ack_packet.is_fin():
                        new_dic = {} 
                        self.packet_window = new_dic
                        return OK

                    if ack_packet.is_ack(): 
                        if ack_packet.ack_number - 1 in self.packet_window:
                            self.packet_window.pop(ack_packet.ack_number - 1)

                            new_dic = {} 
                            for sec in self.packet_window.keys():
                                if sec >= ack_packet.ack_number:
                                    new_dic[sec] = self.packet_window[sec]
                            self.packet_window = new_dic
                            self.logger.debug(f"(WAIT_ACK) self.packet_window es {self.packet_window.keys}")
                            return OK
                        repeated_ack += 1
                    else:
                        continue
            
                except (timeout, queue.Empty):
                    self.logger.debug("Timeout event occurred on send. Retrying...")
                    repeated_ack += 1

            for pkt in self.packet_window.values():
                self.logger.debug(f"En la retransmision self.packet_window es {self.packet_window.keys()}")
                stream.send_to(pkt.to_bytes(), self.address)
                self.logger.debug(f"Retransmitted packet sent as ({pkt})")

            retries += 1



    def _wait_ack_2(self, stream):
        while True:
            try:
                ack_packet = stream.receive()
                self.logger.debug(f"Received packet as {ack_packet}")

                if ack_packet.is_fin():
                    new_dic = {} 
                    self.packet_window = new_dic
                    return OK

                if ack_packet.is_ack(): 
                    self.logger.debug(f"(WAIT_ACK) ANTES DE LA COMPARACION")
                    self.logger.debug(f"(WAIT_ACK) (ack_packet.ack_number - 1) es: {ack_packet.ack_number - 1}")
                    if (ack_packet.ack_number - 1) in self.packet_window: 
                        self.logger.debug(f"(WAIT_ACK) DENTRO DEL IF, ANTES DE LIMPIAR LA VENTANA ")
                        self.packet_window.pop(ack_packet.ack_number - 1)
                        new_dic = {} 
                        for sec in self.packet_window.keys():
                            if sec >= ack_packet.ack_number:
                                new_dic[sec] = self.packet_window[sec]
                        self.packet_window = new_dic
                        self.logger.debug(f"(WAIT_ACK) self.packet_window es {self.packet_window.keys()}")
                        return OK
                    else:
                        self.logger.debug(f"(WAIT_ACK) DENTRO DEL ELSE, NO HAGO NADA")
                        self.logger.debug(f"(WAIT_ACK) (ack_packet.ack_number - 1) es: {ack_packet.ack_number - 1}")
                        self.logger.debug(f"(WAIT_ACK) self.packet_window es {self.packet_window.keys()}")
                        return OK
                        #continue

            except (timeout, queue.Empty):
                self.logger.debug("Timeout event occurred on send. Retrying...")
                for pkt in self.packet_window.values():
                    self.logger.debug(f"En la retransmision self.packet_window es {self.packet_window.keys()}")
                    stream.send_to(pkt.to_bytes(), self.address)
                    self.logger.debug(f"Retransmitted packet sent as ({pkt})")

        