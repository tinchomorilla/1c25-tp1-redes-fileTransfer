import argparse
import os
import socket
from rdt import StopAndWaitRDT, MAX_DATA_SIZE

DONE_MARKER = b'UPLOAD_DONE'

def main():
    parser = argparse.ArgumentParser(description="Upload a file to the server using StopAndWaitRDT.")
    parser.add_argument("-H", "--host", required=True, help="Server IP address")
    parser.add_argument("-p", "--port", required=True, type=int, help="Server port")
    parser.add_argument("-s", "--src", required=True, help="Source file path")
    parser.add_argument("-n", "--name", required=True, help="Target filename on server")
    args = parser.parse_args()

    server_addr = (args.host, args.port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    rdt = StopAndWaitRDT(sock, addr=server_addr, is_sender=True)

    print(f"[CLIENT] Conectando a {server_addr}...")

    # Paso 1: Enviar nombre de archivo
    init_msg = f"UPLOAD|{args.name}".encode()
    rdt.send(init_msg)
    print(f"[CLIENT] Nombre de archivo enviado: {args.name}")

    # Paso 2: Enviar contenido del archivo
    with open(args.src, "rb") as f:
        while True:
            chunk = f.read(MAX_DATA_SIZE)
            if not chunk:
                break
            rdt.send(chunk)

    # Paso 3: Enviar marcador de fin
    rdt.send(DONE_MARKER)

    print(f"[CLIENT] Archivo '{args.src}' enviado correctamente.")

if __name__ == "__main__":
    main()
