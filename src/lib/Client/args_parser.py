import argparse
import ipaddress


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Cliente para subir y descargar archivos."
    )

    # Argumentos comunes
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Aumentar la verbosidad de la salida"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Reducir la verbosidad de la salida"
    )
    parser.add_argument(
        "-H", "--addr", required=True, help="Dirección IP del servidor"
    )
    parser.add_argument(
        "-p", "--port", type=int, required=True, help="Puerto del servidor"
    )
    parser.add_argument(
        "-r", "--protocol", required=True, help="Protocolo de recuperación de errores"
    )

    # Argumentos específicos para upload y download
    parser.add_argument(
        "-s", "--src", help="En upload, ruta donde se encuentra el archivo a subir."
    )
    parser.add_argument(
        "-d", "--dst", help="En download, ruta donde se guardará el archivo localmente."
    )
    parser.add_argument(
        "-n", "--filename", help="Si es upload, nombre del archivo con el que se guardará en el servidor. Si es download, nombre del archivo a descargar."
    )

    args = parser.parse_args()

    # Validar que la dirección IP sea válida
    try:
        ipaddress.ip_address(args.addr)
    except ValueError:
        parser.error(f"La dirección IP '{args.addr}' no es válida.")

    # Validar que los argumentos requeridos estén presentes según el comando
    if args.src and args.dst:
        parser.error("No puedes usar --src y --dst al mismo tiempo.")
    elif args.src:  # Comando upload
        if not args.filename:
            parser.error("Para 'upload' se requiere --filename.")
    elif args.dst:  # Comando download
        if not args.filename:
            parser.error("Para 'download' se requiere --filename.")
    else:
        parser.error("Debes especificar --src para upload o --dst para download.")

    return args