from socket import *

BUFFER_SIZE = 2048

class Server:
    def __init__(self, addr, puerto):
        self.addr = addr
        self.puerto = puerto
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start(self):
        print(f"Server started at {self.addr}:{self.puerto}")
        self.socket.bind((self.addr, self.puerto))
        try:
            while True:
                message, client_address = self.socket.recvfrom(BUFFER_SIZE)
                print(f"Recieved message: \"{message.decode()}\" from client: {client_address}")
                modified_message = message.decode().upper()
                self.socket.sendto(modified_message.encode(), client_address)
        except KeyboardInterrupt:
            print()
            print("Server stopped")
        finally:
            self.socket.close()

    def download(self):
        pass