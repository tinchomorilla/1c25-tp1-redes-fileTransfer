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
        else:
            status = self._wait_ack(stream)
            if status==OK:
                stream.send_to(packet.to_bytes(), self.address)
                self.logger.debug(f"Packet sent as ({packet})")
                self.packet_window[packet.sequence_number] = packet
                self.sequence_number += 1
        if packet.is_fin():
            self._wait_last_packets(stream)

        

    def recv(self, stream):
        receive_count = 0
        while True:
            try:
                packet = stream.receive()
                if packet.is_fin() and packet.sequence_number == self.ack_number:
                    self.logger.debug(f"(RECV)  Received FIN packet: {packet}, from address {self.address}")
                    self.ack_number += 1
                    ack = Packet.new_fin_packet()
                    ack.sequence_number = self.sequence_number
                    ack.ack_number = self.ack_number
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"(RECV)  Sent FIN Packet ({ack}) to address {self.address}")
                    return packet
                if not packet.is_ack() and packet.sequence_number == self.ack_number:
                    self.logger.debug(f"(RECV)  Received correct packet as {packet} from address {self.address}")
                    self.ack_number += 1
                    ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                    stream.send_to(ack.to_bytes(), self.address)                    
                    return packet
                else:
                    # Si el sender me envio un paquete desordenado
                    # es decir, un paquete que no es el que el Receiver esperaba
                    # lo ignoro, pero le aviso cual es el ACK que estoy esperando recibir
                    # Si el Sender me envio un paquete que ya he recibido, lo ignoro
                    # pero le aviso cual es el proximo ACK que estoy esperando recibir
                    self.logger.debug(f"(RECV) Received incorrect packet as {packet} from address {self.address}")
                    ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                    stream.send_to(ack.to_bytes(), self.address)
            except (timeout, queue.Empty):
                ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                stream.send_to(ack.to_bytes(), self.address)
                self.logger.debug(f"(RECV)  Ask for retransmission for ({self.ack_number}) para el address {self.address}")
                continue
            receive_count+=1
        
        
    def _wait_last_packets(self, stream):
        retries = 0
        while(len(self.packet_window) > 0 ):
            if(retries >= WINDOW_SIZE):
                self.logger.debug(f"Retransmission limit reached")
                return
            self.logger.debug(f"Waiting last packets for address {self.address}")
            self._wait_ack(stream)
            retries +=1


    def _wait_ack(self, stream):
        retries = 0
        while True:
            repeated_ack = 0
            while repeated_ack < MAX_REPEATED_ACKS:   
                try:
                    ack_packet = stream.receive()
                    self.logger.debug(f"[WAIT_ACK] Received packet as {ack_packet} from address {self.address}")

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
                            return OK
                        repeated_ack += 1
                    else:
                        continue
            
                except (timeout, queue.Empty):
                    self.logger.debug("Timeout event occurred on send. Retrying...")
                    repeated_ack += 1

            for pkt in self.packet_window.values():
                stream.send_to(pkt.to_bytes(), self.address)
                self.logger.debug(f"Retransmitted packet sent as ({pkt}) to address {self.address}")

            retries += 1



    