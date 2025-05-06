from lib.Common.constants import PACKET_SIZE, TIMEOUT_QUEUE, TIMEOUT_SOCKET
from lib.Packet.packet import Packet
import queue

class StreamWrapper:
    def __init__(self, socket, queue):
        self.socket = socket
        self.queue = queue
        self.socket.settimeout(TIMEOUT_SOCKET)
    
    def receive(self):
        if self.queue is None:
            data, _address = self.socket.recvfrom(PACKET_SIZE)
            return Packet.from_bytes(data)
        else:
            return self.queue.get(True, TIMEOUT_QUEUE)
    
    def send_to(self, bytes, address):
        self.socket.sendto(bytes, address)

    def close(self):
        self.socket.close()
    
    def enqueue(self, packet):
        self.queue.put(packet)


    def set_timeout(self):
        if self.queue is None:
            self.socket.settimeout(TIMEOUT_SOCKET)