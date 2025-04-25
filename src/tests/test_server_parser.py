import sys
import pytest
from src.Server.parse_args import parse_arguments

def test_parse_upload_command():
    test_args = [
        "main.py",
        "-H", "127.0.0.1",
        "-p", "9000",
        "-s", "./storage",
        "-r", "stop_and_wait",
    ]
    sys.argv = test_args
    args = parse_arguments()

    assert args.host == "127.0.0.1"
    assert args.port == 9000
    assert args.storage == "./storage"
    assert args.protocol == "stop_and_wait"

def test_parse_default_host():
    test_args = [
        "main.py",
        "-p", "9000",
        "-s", "./storage",
        "-r", "stop_and_wait",
    ]
    sys.argv = test_args
    args = parse_arguments()

    assert args.host == "0.0.0.0"  # Valor por defecto
    assert args.port == 9000
    assert args.storage == "./storage"
    assert args.protocol == "stop_and_wait"

def test_missing_required_arguments():
    test_args = [
        "main.py",
        "-H", "127.0.0.1",
        "-p", "9000",
    ]
    sys.argv = test_args

    with pytest.raises(SystemExit):  # El parser debe salir si faltan argumentos
        parse_arguments()