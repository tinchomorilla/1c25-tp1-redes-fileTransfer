from client import Client
from src.Client.parse_args import parse_arguments  

def main():
    args = parse_arguments()  

    # Instancia del cliente
    client = Client(args.host, args.port, args.protocol)

    # Ejecutar el comando correspondiente
    if args.command == "upload":
        client.upload(args.src, args.name)
    elif args.command == "download":
        client.download(args.name, args.dst)
    else:
        print("Comando no reconocido.")
        exit(1)

if __name__ == "__main__":
    main()