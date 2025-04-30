import multiprocessing
import random
import string
import subprocess

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9000
NUM_CLIENTS = 5  # Número de clientes simultáneos


def random_filename(base="copia"):
    """Genera un nombre de archivo aleatorio."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{base}_{suffix}.jpeg"


def download_client(target_name):
    """Función que llama a main.py para enviar un archivo."""
    filename = random_filename()
    download_src = "./src/lib/Client/downloads/" + filename # Path donde quiero guardar el archivo
    subprocess.run(
        [
            "python3",
            "src/download.py",
            "-H",
            SERVER_IP,
            "-p",
            str(SERVER_PORT),
            "-d",
            download_src,
            "-n",
            target_name,
            "-r",
            "stop_and_wait",
        ],
        check=True,
    )


def main():
    processes = []

    for _ in range(NUM_CLIENTS):
        filename = "momo.jpeg" # Nombre del archivo a descargar (debe existir en el servidor)
        p = multiprocessing.Process(target=download_client, args=(filename,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("[STRESS TEST] Todos los han terminado.")


if __name__ == "__main__":
    main()
