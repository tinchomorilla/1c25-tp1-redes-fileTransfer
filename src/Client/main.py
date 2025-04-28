from parse_args import parse_arguments  # pylint: disable=import-error
from client import Client  # pylint: disable=import-error

def main():
    args = parse_arguments() 

    print("[CLIENT] Argumentos recibidos:")

    # Instancia del cliente
    client = Client(args.addr, args.port, args.protocol)

    # Ejecutar el comando correspondiente
    if args.command == "upload":
        print(f"[CLIENT] Subiendo archivo")
        client.upload(args.filepath, args.filename)
    elif args.command == "download":
        client.download(args.filename, args.filepath)
    else:
        print("Comando no reconocido.")
        exit(1)

if __name__ == "__main__":
    main()