import argparse
import os
import threading
import queue
import socket
from rdt import StopAndWaitRDT, MAX_DATA_SIZE

DONE_MARKER = b'UPLOAD_DONE'

handlers = {}
lock = threading.Lock()

def reader(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        with lock:
            if addr not in handlers:
                q = queue.Queue()
                handlers[addr] = q
                threading.Thread(target=handle_client, args=(sock, addr, q), daemon=True).start()
            handlers[addr].put(data)

def handle_client(sock, addr, q):
    print(f"[SERVER] Atendiendo nuevo cliente: {addr}")
    rdt = StopAndWaitRDT(sock, addr=addr, queue=q)

    try:
        # Recibir nombre del archivo
        init_msg = rdt.recv()
        if not init_msg.startswith(b"UPLOAD|"):
            print(f"[SERVER] Comando inicial inválido de {addr}")
            return

        filename = init_msg.decode().split("|")[1]
        filepath = os.path.join("./downloads", filename)

        with open(filepath, "wb") as f:
            while True:
                data = rdt.recv()
                if data == DONE_MARKER:
                    break
                f.write(data)

        print(f"[SERVER] Archivo recibido correctamente: {filepath}")
    except Exception as e:
        print(f"[SERVER] Error procesando cliente {addr}: {e}")
    finally:
        with lock:
            if addr in handlers:
                del handlers[addr]

def main():
    parser = argparse.ArgumentParser(description="Start Stop & Wait file server.")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Server IP address")
    parser.add_argument("-p", "--port", required=True, type=int, help="Port to bind to")
    parser.add_argument("-s", "--storage", required=True, help="Storage directory path")
    parser.add_argument("-r", "--protocol", default="stop_and_wait", help="Recovery protocol (ignored for now)")
    args = parser.parse_args()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((args.host, args.port))
    print(f"[SERVER] Escuchando en {args.host}:{args.port}")

    # threading.Thread(target=reader, args=(server_sock,), daemon=True).start()

    # # El main thread puede dormir para siempre o manejar shutdown
    # threading.Event().wait()

    while True:
        data, addr = server_sock.recvfrom(1024)
        with lock:
            if addr not in handlers:
                q = queue.Queue()
                handlers[addr] = q
                threading.Thread(target=handle_client, args=(server_sock, addr, q), daemon=True).start()
                
            handlers[addr].put(data)

if __name__ == "__main__":
    main()
