import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Cliente para subir y descargar archivos."
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Comandos disponibles: upload, download"
    )

    # Subcomando: upload
    upload_parser = subparsers.add_parser("upload", help="Subir un archivo al servidor")
    upload_parser.add_argument(
        "-H", "--addr", required=True, help="Dirección IP del servidor"
    )
    upload_parser.add_argument(
        "-p", "--port", type=int, required=True, help="Puerto del servidor"
    )
    upload_parser.add_argument(
        "-s", "--filepath", required=True, help="Ruta del archivo fuente"
    )
    upload_parser.add_argument(
        "-n", "--filename", required=True, help="Nombre del archivo en el servidor"
    )
    upload_parser.add_argument(
        "-r", "--protocol", required=True, help="Protocolo de recuperación de errores"
    )

    # Subcomando: download
    download_parser = subparsers.add_parser(
        "download", help="Descargar un archivo del servidor"
    )
    download_parser.add_argument(
        "-H", "--addr", required=True, help="Dirección IP del servidor"
    )
    download_parser.add_argument(
        "-p", "--port", type=int, required=True, help="Puerto del servidor"
    )
    download_parser.add_argument(
        "-d", "--filepath", required=True, help="Ruta de destino para guardar el archivo"
    )
    download_parser.add_argument(
        "-n", "--filename", required=True, help="Nombre del archivo en el servidor"
    )
    download_parser.add_argument(
        "-r", "--protocol", required=True, help="Protocolo de recuperación de errores"
    )

    return parser.parse_args()