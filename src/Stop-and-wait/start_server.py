import argparse
import os
import socket
import threading
from rdt import StopAndWaitRDT, MAX_DATA_SIZE, TYPE_INIT, TYPE_READY, TYPE_INIT_ACK

DONE_MARKER = b'_UPLOAD_DONE_'
clients_in_progress = set()

def handle_client(sock, addr, storage_dir, filename):
    print(f"[SERVER] Atendiendo cliente: {addr}")
    rdt = StopAndWaitRDT(sock, addr=addr, is_sender=False)

    filepath = os.path.join(storage_dir, filename)

    with open(filepath, "wb") as f:
        while True:
            data, _ = rdt.recv()
            if data == DONE_MARKER:
                print(f"[SERVER] Fin de transmisión recibido de {addr}")
                break
            print(f"[SERVER] Recibiendo datos de {addr}: {data}")
            f.write(data)

    print(f"[SERVER] Archivo recibido de {addr}: {filepath}")
    clients_in_progress.discard(addr)

def main():
    parser = argparse.ArgumentParser(description="Start Stop & Wait file server.")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Server IP address")
    parser.add_argument("-p", "--port", required=True, type=int, help="Port to bind to")
    parser.add_argument("-s", "--storage", required=True, help="Storage directory path")
    parser.add_argument("-r", "--protocol", default="stop_and_wait", help="Recovery protocol (ignored for now)")
    args = parser.parse_args()

    os.makedirs(args.storage, exist_ok=True)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((args.host, args.port))
    server_sock.settimeout(None)
    print(f"[SERVER] Escuchando en {args.host}:{args.port}")

    while True:
        try:
            # init_data, client_addr = server_sock.recvfrom(1024)

            # Handshake inicial: INIT
            rdt = StopAndWaitRDT(server_sock, is_sender=False)
            init_data, client_addr = rdt.recv()  # INIT

            if client_addr in clients_in_progress:
                continue

            rdt.addr = client_addr
            print(f"[SERVER] INIT recibido de {client_addr}: {init_data}")

            # Validar INIT y extraer nombre
            if not init_data.startswith(b"UPLOAD|"):
                print(f"[SERVER] Comando INIT inválido de {client_addr}")
                continue

            filename = init_data.decode().split("|")[1]

            # Responder INIT-ACK
            rdt.send(b"ACK_INIT", pkt_type=TYPE_INIT_ACK)

            # Esperar READY
            ready_data, _ = rdt.recv()
            if ready_data != b"READY":
                print(f"[SERVER] READY inválido de {client_addr}")
                continue

            clients_in_progress.add(client_addr)

            t = threading.Thread(
                target=handle_client,
                args=(server_sock, client_addr, args.storage, filename),
                daemon=True
            )
            t.start()
        except KeyboardInterrupt:
            print("[SERVER] Cerrando servidor")
            break

if __name__ == "__main__":
    main()
