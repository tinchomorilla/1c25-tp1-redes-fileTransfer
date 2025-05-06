import sys
from os.path import abspath, dirname
from lib.Server.args_parser import Parser
from lib.Common.logger import initialize_logger
from lib.Server.server import Server
# Agregar el directorio raíz del proyecto al sys.path
sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))



def main():
    
    parser = Parser("Flags for Server Command")

    args = parser.parse_args_server()
    logger = initialize_logger(args.debug_level, "server")

    logger.info(f"[SERVER] Iniciando servidor en {args.host}:{args.port} con protocolo {args.protocol}")
    server = Server(args.host, args.port, args.storage_dir, args.protocol, logger)

    server.run()


if __name__ == "__main__":
    main()
