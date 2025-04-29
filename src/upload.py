from lib.Client.client import Client
from lib.Client.args_parser import parse_arguments


def main():
    args = parse_arguments() 

    print("[CLIENT] Argumentos recibidos:")

    # Instancia del cliente
    client = Client(args.addr, args.port, args.protocol)

    
    print(f"[CLIENT] Subiendo archivo")
    client.upload(args.filepath, args.filename)
   

if __name__ == "__main__":
    main()