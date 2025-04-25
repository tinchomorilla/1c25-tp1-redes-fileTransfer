from client_handler import ClientHandler

class Listener:
    def __init__(self, sock, storage_dir):
        self.sock = sock
        self.storage_dir = storage_dir

    def listen(self):
        """Escucha conexiones entrantes y delega el manejo a handle_client."""
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                print(f"[LISTENER] Atendiendo nuevo cliente: {addr}")
                client = ClientHandler(self.sock, addr, self.storage_dir, data)
                client.handle()                
            except KeyboardInterrupt:
                print("[LISTENER] Cerrando servidor")
                break