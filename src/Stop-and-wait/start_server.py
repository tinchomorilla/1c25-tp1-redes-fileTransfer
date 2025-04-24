# start_server.py
import argparse
import os
import socket
import threading
from rdt import StopAndWaitRDT, MAX_DATA_SIZE

DONE_MARKER = b'__UPLOAD_DONE__'

def handle_client(sock, addr, storage_dir):
    print(f"[SERVER] Atendiendo nuevo cliente: {addr}")
    rdt = StopAndWaitRDT(sock, is_sender=False)

    # Primer mensaje: UPLOAD|filename
    init_msg, _ = rdt.recv()
    if not init_msg.startswith(b"UPLOAD|"):
        print(f"[SERVER] Comando invalido de {addr}")
        return

    filename = init_msg.decode().split("|")[1]
    filepath = os.path.join(storage_dir, filename)

    with open(filepath, "wb") as f:
        print(f"[SERVER] Recibiendo archivo: {filename}")
        while True:
            data, _ = rdt.recv()
            if data == DONE_MARKER:
                print(f"[SERVER] Fin de transmisión recibido de {addr}")
                break
            f.write(data)

    print(f"[SERVER] Archivo recibido: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Start Stop & Wait file server.")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Server IP address")
    parser.add_argument("-p", "--port", required=True, type=int, help="Port to bind to")
    parser.add_argument("-s", "--storage", required=True, help="Storage directory path")
    parser.add_argument("-r", "--protocol", default="stop_and_wait", help="Recovery protocol (ignored for now)")
    args = parser.parse_args()

    os.makedirs(args.storage, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    print(f"[SERVER] Escuchando en {args.host}:{args.port}")

    # Como es UDP, podemos compartir el socket entre hilos
    while True:
        try:
            sock.settimeout(None)
            data, addr = sock.recvfrom(1024)
            sock.sendto(data, addr)  # reenviamos para que el hilo pueda empezar
            # t = threading.Thread(target=handle_client, args=(sock, addr, args.storage))
            # t.start()
            handle_client(sock, addr, args.storage)
        except KeyboardInterrupt:
            print("[SERVER] Cerrando servidor")
            break

if __name__ == "__main__":
    main()
