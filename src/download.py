from lib.Client.client import Client
from lib.Client.args_parser import parse_arguments


def main():
    args = parse_arguments() 

    print("[CLIENT] Argumentos recibidos:")

    # Instancia del cliente
    client = Client(args.addr, args.port, args.protocol)

    
    print(f"[CLIENT] Subiendo archivo")

    # filepath = ruta donde se almacenara el archivo localmente
    # filename = nombre del archivo que se encuentra en el servidor
    client.download(args.dst, args.filename)
   

if __name__ == "__main__":
    main()
