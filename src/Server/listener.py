from client_handler import ClientHandler

class Listener:
    def __init__(self, sock):
        self.sock = sock

    def listen(self, storage_dir):
        """Escucha conexiones entrantes y delega el manejo a handle_client."""
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                print(f"[LISTENER] Atendiendo nuevo cliente: {addr}")
                client = ClientHandler(self.sock, addr, storage_dir, data)
                client.handle()                
            except KeyboardInterrupt:
                print("[LISTENER] Cerrando servidor")
                break