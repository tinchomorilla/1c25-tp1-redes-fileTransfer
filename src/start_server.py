import sys
from os.path import abspath, dirname
from lib.Server.server import Server
from lib.Server.parse_args import parse_arguments
# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))


def main():
    args = parse_arguments()

    # Instancia del servidor
    server = Server(args.host, args.port, args.storage, args.protocol)

    # Iniciar el servidor
    server.run()


if __name__ == "__main__":
    main()
