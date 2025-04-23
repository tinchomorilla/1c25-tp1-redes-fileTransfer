from server import Server
SERVER_PORT = 12000
BUFFER_SIZE = 2048
SERVER_NAME = '127.0.0.1'

def main():
    server = Server(SERVER_NAME, SERVER_PORT)
    server.start()

if __name__ == '__main__':
    main()