from lib.Client.client import Client
from lib.Client.args_parser import Parser
from lib.Common.logger import initialize_logger

def main():

    parser = Parser("Flags for upload command")
    args = parser.parse_args_upload()
    
    logger = initialize_logger(args.debug_level, "upload")

    logger.info("[CLIENT] Iniciando logger para upload en modo info")

    client = Client(args.host, int(args.port), args.protocol, logger)

    client.upload(args.src, args.filename)
    
if __name__ == "__main__":
    main()