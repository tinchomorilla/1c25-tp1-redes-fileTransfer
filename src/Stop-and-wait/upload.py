# upload.py
import argparse
import os
import socket
from rdt import StopAndWaitRDT, MAX_DATA_SIZE

# Comando especial para señalar fin de archivo
DONE_MARKER = b'__UPLOAD_DONE__'

def main():
    parser = argparse.ArgumentParser(description="Upload a file to the server using Stop & Wait RDT.")
    parser.add_argument("-H", "--host", required=True, help="Server IP address")
    parser.add_argument("-p", "--port", required=True, type=int, help="Server port")
    parser.add_argument("-s", "--src", required=True, help="Source file path")
    parser.add_argument("-n", "--name", required=True, help="Target filename on server")
    parser.add_argument("-r", "--protocol", default="stop_and_wait", help="Recovery protocol (ignored for now)")
    args = parser.parse_args()

    server_addr = (args.host, args.port)

    # Crear socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Inicializar RDT
    rdt = StopAndWaitRDT(sock, addr=server_addr, is_sender=True)

    # Enviar comando inicial UPLOAD <filename>
    init_msg = f"UPLOAD|{args.name}".encode()
    rdt.send(init_msg)

    # Abrir archivo y fragmentar
    with open(args.src, "rb") as f:
        while True:
            chunk = f.read(MAX_DATA_SIZE)
            if not chunk:
                break
            rdt.send(chunk)

    # Enviar marcador de fin de transmisión
    rdt.send(DONE_MARKER)
    print(f"[CLIENT] Archivo '{args.src}' enviado como '{args.name}'")

    sock.close()

if __name__ == "__main__":
    main()
