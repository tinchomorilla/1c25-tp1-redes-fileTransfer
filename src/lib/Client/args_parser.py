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
        "-s", "--filepath", help="Si es upload, ruta donde se encuentra el archivo a subir. Si es download, ruta donde se guardará el archivo localmente."
    )
    parser.add_argument(
        "-n", "--filename", help="Si es upload, nombre del archivo con el que se guardara en el servidor. Si es download, nombre del archivo a descargar."
    )

    args = parser.parse_args()

    # Validar que la dirección IP sea válida
    try:
        ipaddress.ip_address(args.addr)
    except ValueError:
        parser.error(f"La dirección IP '{args.addr}' no es válida.")

    # Validar que los argumentos requeridos estén presentes según el comando
   
    if not args.filepath or not args.filename:
        parser.error("Se requiere --filepath y --filename.")
    
    if args.protocol not in ["stop_and_wait", "go_back_n"]:
        parser.error("Protocolo no soportado. Usa 'stop_and_wait' o 'go_back_n'.")


    return args