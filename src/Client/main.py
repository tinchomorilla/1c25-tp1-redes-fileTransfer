from client import Client
from src.Client.parse_args import parse_arguments  

def main():
    args = parse_arguments()  

    # Instancia del cliente
    client = Client(args.addr, args.port, args.protocol)

    # Ejecutar el comando correspondiente
    if args.command == "upload":
        client.upload(args.filepath, args.filename)
    elif args.command == "download":
        client.download(args.filename, args.filepath)
    else:
        print("Comando no reconocido.")
        exit(1)

if __name__ == "__main__":
    main()