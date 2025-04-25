from server import Server
from parse_args import parse_arguments


def main():
    args = parse_arguments()

    # Instancia del servidor
    server = Server(args.host, args.port, args.storage, args.protocol)

    # Iniciar el servidor
    server.start()


if __name__ == "__main__":
    main()
