from lib.Common.constants import *
from lib.Packet.packet import Packet
from socket import *
import queue

from lib.RDT.handshake import Protocol 

class StopAndWait(Protocol):
   
    def send(self, packet, stream):
        self.logger.debug(f"Preparing packet to {self.address}")
        send_count = 0
        while send_count < RETRIES:
            try:
                packet.sequence_number = self.sequence_number
                packet.ack_number = self.ack_number

                stream.send_to(packet.to_bytes(), self.address)
                self.logger.debug(f"Packet sent as ({packet})")

                ack_packet = stream.receive()
                self.logger.debug(f"Received packet as {ack_packet}")

                if not ack_packet.is_ack() or ack_packet.ack_number != self.sequence_number + 1:
                    self.logger.error("Received packet is not ack or ack number is not correct")
                    return
                else:
                    self.ack_number = ack_packet.sequence_number + 1
                    self.sequence_number += 1
                    return
            except (timeout, queue.Empty):
                self.logger.debug("[SAW_SEND] Timeout event occurred on send. Retrying...")
                send_count += 1
        
    
    
    def recv(self, stream):
        receive_count = 0
        #while receive_count < RETRIES + 1:
        while True:
            try:
                packet = stream.receive()
                self.logger.debug(f"Received packet as {packet}")
                if packet.is_fin() and packet.sequence_number == self.ack_number:
                    self.logger.debug("Received fin packet")
                    self.ack_number += 1
                    ack = Packet.new_fin_packet()
                    ack.sequence_number = self.sequence_number
                    ack.ack_number = self.ack_number
                    stream.send_to(ack.to_bytes(), self.address)
                    self.sequence_number += 1
                    self.logger.debug(f"Sent ack as {ack} DE FIN")
                    return packet    
                elif packet.sequence_number != self.ack_number:
                    self.logger.error("Ack number is not correct")
                    ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"Sent ack as {ack}")
                    continue
                else:
                    self.ack_number = packet.sequence_number + 1
                    ack = Packet.new_ack_packet(self.sequence_number, self.ack_number, None)
                    stream.send_to(ack.to_bytes(), self.address)
                    self.logger.debug(f"Sent ack as {ack}")
                    self.sequence_number += 1
                    return packet
                
            except (timeout, queue.Empty):
                self.logger.debug("Timeout event occurred on receive. Retrying...")
                receive_count += 1
        
        
