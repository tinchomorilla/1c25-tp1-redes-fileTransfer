import os
import threading

DONE_MARKER = b"__UPLOAD_DONE__"
lock = threading.Lock()


class ClientHandler:
    def __init__(self, rdt, storage_dir):
        self.rdt = rdt
        self.storage_dir = storage_dir  # Directorio de almacenamiento en el servidor

    def handle(self):
        """Lógica para recibir un archivo desde un cliente."""
        print(f"[CLIENT_HANDLER] Esperando mensaje inicial del cliente...")
        init_msg = self.rdt.recv()
        if not init_msg.startswith(b"UPLOAD|"):
            return

        print(f"[CLIENT_HANDLER] Mensaje inicial recibido: {init_msg.decode()}")
        filename = init_msg.decode().split("|")[1]
        filepath = os.path.join(self.storage_dir, filename)

        with open(filepath, "wb") as f:
            while True:
                data = self.rdt.recv()
                if data == DONE_MARKER:
                    break
                print(f"[CLIENT_HANDLER] Escribiendo datos...")
                f.write(data)

        print(f"[CLIENT_HANDLER] Archivo recibido correctamente: {filepath}")
