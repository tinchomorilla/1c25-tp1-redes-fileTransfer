from lib.Client.client import Client
from lib.Client.args_parser import Parser
from lib.Common.logger import initialize_logger


def main():
    parser = Parser("Flags for download command")
    args = parser.parse_args_download()
    
    logger = initialize_logger(args.debug_level, "download")

    logger.info("[CLIENT] Iniciando logger para download en modo info")

    client = Client(args.host, int(args.port), args.protocol, logger)

    # filepath = ruta donde se almacenara el archivo localmente
    # filename = nombre del archivo que se encuentra en el servidor
    client.download(args.dst, args.filename)
   

if __name__ == "__main__":
    main()
