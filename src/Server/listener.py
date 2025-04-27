import sys
from os.path import abspath, dirname
import threading
from src.RDT.stop_and_wait import StopAndWaitRDT
from src.Server.client_handler import ClientHandler

sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))

import queue

lock = threading.Lock()


class Listener:
    def __init__(self, sock):
        self.sock = sock
        self.handlers = {}

    def listen(self, storage_dir):
        """Escucha conexiones entrantes y delega el manejo a handle_client."""
        while True:
            data, addr = self.sock.recvfrom(1024)
            with lock:
                print(f"[SERVER] Paquete recibido de {addr}")
                if addr not in self.handlers:
                    print(f"[SERVER] Nuevo cliente conectado: {addr}")
                    q = queue.Queue()
                    self.handlers[addr] = q
                    threading.Thread(
                        target=self.handle_client,
                        args=(self.sock, addr, q, storage_dir),
                        daemon=True,
                    ).start()

                self.handlers[addr].put(data)

    def handle_client(self, sock, addr, q, storage_dir):
        try:
            rdt = StopAndWaitRDT(sock, addr=addr, queue=q)
            client = ClientHandler(rdt, storage_dir)
            client.handle()
        except Exception as e:
            print(f"[SERVER] Error procesando cliente {addr}: {e}")
        finally:
            with lock:
                if addr in self.handlers:
                    del self.handlers[addr]
