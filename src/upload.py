import argparse

from client import Client
SERVER_NAME = '127.0.0.1'
SERVER_PORT = 12000
BUFFER_SIZE = 2048

def main():
    client = Client()

    parser = argparse.ArgumentParser(description="Upload files to a server.")
    parser.add_argument('-s', '--src', type=str, default="", help="Message")

    args = parser.parse_args()

    client.upload(args.src)

if __name__ == '__main__':
    main()