import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Start Stop & Wait file server.")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Server IP address")
    parser.add_argument("-p", "--port", required=True, type=int, help="Port to bind to")
    parser.add_argument("-s", "--storage", required=True, help="Storage directory path")
    parser.add_argument(
        "-r", "--protocol", default="stop_and_wait", help="Recovery protocol (ignored for now)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Decrease output verbosity"
    )
    return parser.parse_args()