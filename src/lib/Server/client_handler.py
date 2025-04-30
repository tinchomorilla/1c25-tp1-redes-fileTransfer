import os
import threading
from lib.RDT.stop_and_wait import MAX_DATA_SIZE

DONE_MARKER = b"__UPLOAD_DONE__"
lock = threading.Lock()


class ClientHandler:
    def __init__(self, rdt, storage_dir):
        self.rdt = rdt
        self.storage_dir = storage_dir  # Directorio de almacenamiento en el servidor

    def handle(self):
        """Lógica para manejar comandos del cliente."""
        print(f"[CLIENT_HANDLER] Esperando mensaje inicial del cliente...")
        init_msg = self.rdt.recv()

        if init_msg.startswith(b"UPLOAD|"):
            self.handle_upload(init_msg)
        elif init_msg.startswith(b"DOWNLOAD|"):
            self.handle_download(init_msg)
        else:
            print(f"[CLIENT_HANDLER] Comando no reconocido: {init_msg.decode()}")

    def handle_upload(self, init_msg):
        """Lógica para manejar la subida de archivos desde el cliente."""
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

    def handle_download(self, init_msg):
        """Lógica para manejar la descarga de archivos hacia el cliente."""
        filename = init_msg.decode().split("|")[1]
        filepath = os.path.join("./src/lib/Server/downloads", filename)

        if not os.path.exists(filepath):
            print(f"[SERVER] Archivo no encontrado: {filepath}")
            # Opcional: enviar mensaje de error al cliente
            return

        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(MAX_DATA_SIZE)
                if not chunk:
                    break
                self.rdt.send(chunk)

        self.rdt.send(b"__DOWNLOAD_DONE__")
        print(f"[SERVER] Archivo enviado correctamente: {filepath}")
