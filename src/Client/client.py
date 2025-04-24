from socket import *

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 12000
BUFFER_SIZE = 2048

class Client:
    def __init__(self, sever_addr=SERVER_ADDR, server_port=SERVER_PORT):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.server_addr = sever_addr
        self.server_port = server_port

    def upload(self, message: str):
        modified_message, server_address = self._send_msg(message)
        print(modified_message.decode())
        self.socket.close()

    def _send_msg(self, message: str):
        self.socket.sendto(message.encode(), (self.server_addr, self.server_port))
        return self.socket.recvfrom(BUFFER_SIZE)

    def download(self):
        pass