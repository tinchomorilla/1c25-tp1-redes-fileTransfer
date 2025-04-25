import os
from src.RDT.stop_and_wait import StopAndWaitRDT

DONE_MARKER = b"__UPLOAD_DONE__"

class ClientHandler:
    def __init__(self, sock, addr, storage_dir, init_msg):
        self.sock = sock  # Socket compartido con el servidor
        self.addr = addr  # Dirección del cliente (IP y puerto)
        self.storage_dir = storage_dir  # Directorio de almacenamiento en el servidor
        self.filename = init_msg.decode().split("|")[1]
      

        
    def handle(self):
        """Maneja la lógica de comunicación con un cliente."""
        print(f"[Client Handler] Atendiendo cliente: {self.addr}, archivo: {self.filename}")
        self._receive_file()

    def _receive_file(self):
        """Lógica para recibir un archivo desde un cliente."""
        rdt = StopAndWaitRDT(self.sock, is_sender=False)
        filepath = os.path.join(self.storage_dir, self.filename)

        with open(filepath, "wb") as f:
            print(f"[Client Handler] Recibiendo archivo: {self.filename}")
            while True:
                data, _ = rdt.recv()
                if data.startswith(b"UPLOAD|"):
                    print(f"[DEBUG] Ignorando mensaje inicial: {data}")
                    continue
                if data == DONE_MARKER:
                    print(f"[Client Handler] Fin de transmisión recibido de {self.addr}")
                    print(f"[Client Handler] Recibiendo fragmento de {len(data)} bytes")

                    break
                print(f"[Client Handler] Recibiendo fragmento de {len(data)} bytes")
                f.write(data)

        print(f"[Client Handler] Archivo recibido: {filepath}")