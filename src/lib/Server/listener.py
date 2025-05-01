import socket
import sys
from os.path import abspath, dirname
import threading
from lib.RDT.stop_and_wait import StopAndWaitRDT
from lib.Server.client_handler import ClientHandler

sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))

import queue

lock = threading.Lock()


class Listener:
    def __init__(self, sock, addr: str, port: int):
        self.sock = sock
        self.server_addr = addr
        self.server_port = port
        self.handlers = {}


    def listen(self, storage_dir, protocol: str):
        """Escucha conexiones entrantes y delega el manejo a handle_client."""
        print(f"[LISTENER] LISTENER INICIADO")
        while True:
            print(f"[LISTENER] Esperando paquetes...")
            try:
                data, addr = self.sock.recvfrom(1024)
                print(f"[LISTENER] Paquete recibido de {addr}")
                with lock:
                    print(f"[LISTENER] ANTES DEL IF ADDR")
                    if addr not in self.handlers:
                        print(f"[LISTENER] Nuevo cliente conectado: {addr}")
                        q = queue.Queue()
                        self.handlers[addr] = q
                        threading.Thread(
                            target=self.handle_client,
                            args=(addr, q, storage_dir, protocol),
                            daemon=True,
                        ).start()

                    self.handlers[addr].put(data)
            except socket.timeout:
                print(f"[LISTENER] Timeout alcanzado, continuando...")
                continue

    def handle_client(self, addr, q, storage_dir, protocol):
        try:
            rdt = self.initialize_rdt(protocol, q)
            client = ClientHandler(rdt, storage_dir)
            client.handle()
        except Exception as e:
            print(f"[LISTENER] Error procesando cliente {addr}: {e}")
        finally:
            with lock:
                if addr in self.handlers:
                    del self.handlers[addr]

    def initialize_rdt(self, protocol, q: queue.Queue):
        if protocol == "stop_and_wait":
            return StopAndWaitRDT(self.sock, addr=(self.server_addr, self.server_port), queue=q)
        else:
            return GoBackNRDT()
