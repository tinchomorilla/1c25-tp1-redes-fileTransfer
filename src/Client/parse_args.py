import argparse
import sys

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

    args = parser.parse_args()

    # Validar que todos los argumentos requeridos estén presentes
    if args.command == "upload":
        required_args = ["addr", "port", "filepath", "filename", "protocol"]
    elif args.command == "download":
        required_args = ["addr", "port", "filepath", "filename", "protocol"]
    else:
        parser.print_help()
        sys.exit("Error: Debes especificar un comando válido ('upload' o 'download').")

    # Verificar que todos los argumentos requeridos no sean None
    missing_args = [arg for arg in required_args if getattr(args, arg) is None]
    if missing_args:
        parser.print_help()
        sys.exit(f"Error: Faltan los siguientes argumentos requeridos: {', '.join(missing_args)}")

    return args