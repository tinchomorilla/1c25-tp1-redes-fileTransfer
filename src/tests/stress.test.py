import multiprocessing
import random
import string
import subprocess

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9001
UPLOAD_SRC = "/home/tincho/Documents/Facultad/redes/tps_redes/src/Client/uploads/momo.jpeg"  # El archivo que querés subir
NUM_CLIENTS = 5  # Número de clientes simultáneos


def random_filename(base="copia"):
    """Genera un nombre de archivo aleatorio."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{base}_{suffix}.jpeg"


def upload_client(target_name):
    """Función que llama a main.py para enviar un archivo."""
    subprocess.run(
        [
            "python3",
            "src/Client/main.py",
            "upload",
            "-H",
            SERVER_IP,
            "-p",
            str(SERVER_PORT),
            "-s",
            UPLOAD_SRC,
            "-n",
            target_name,
            "-r",
            "stop-and-wait",
        ],
        check=True,
    )


def main():
    processes = []

    for _ in range(NUM_CLIENTS):
        filename = random_filename()
        p = multiprocessing.Process(target=upload_client, args=(filename,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("[STRESS TEST] Todos los uploads han terminado.")


if __name__ == "__main__":
    main()
