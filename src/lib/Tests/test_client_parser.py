import pytest
from src.Client.parse_args import parse_arguments
import sys

def test_upload_arguments(monkeypatch):
    test_args = [
        "program_name",
        "upload",
        "-H", "127.0.0.1",
        "-p", "8080",
        "-s", "/path/to/source/file.txt",
        "-n", "file_on_server.txt",
        "-r", "protocol1",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()

    assert args.command == "upload"
    assert args.host == "127.0.0.1"
    assert args.port == 8080
    assert args.src == "/path/to/source/file.txt"
    assert args.name == "file_on_server.txt"
    assert args.protocol == "protocol1"

def test_download_arguments(monkeypatch):
    test_args = [
        "program_name",
        "download",
        "-H", "127.0.0.1",
        "-p", "8080",
        "-d", "/path/to/destination/file.txt",
        "-n", "file_on_server.txt",
        "-r", "protocol1",
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()

    assert args.command == "download"
    assert args.host == "127.0.0.1"
    assert args.port == 8080
    assert args.dst == "/path/to/destination/file.txt"
    assert args.name == "file_on_server.txt"
    assert args.protocol == "protocol1"

def test_missing_arguments_upload(monkeypatch):
    # Caso: Falta el argumento obligatorio --host para el comando upload
    test_args = [
        "program_name",
        "upload",
        "-p", "8080",
        "-s", "/path/to/source/file.txt",
        "-n", "file_on_server.txt",
        "-r", "protocol1",
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        parse_arguments()
    assert excinfo.value.code != 0  # Asegurarse de que el programa no salió con éxito

    # Caso: Falta el argumento obligatorio --src para el comando upload
    test_args = [
        "program_name",
        "upload",
        "-H", "127.0.0.1",
        "-p", "8080",
        "-n", "file_on_server.txt",
        "-r", "protocol1",
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        parse_arguments()
    assert excinfo.value.code != 0

def test_missing_arguments_download(monkeypatch):
    # Caso: Falta el argumento obligatorio --host para el comando download
    test_args = [
        "program_name",
        "download",
        "-p", "8080",
        "-d", "/path/to/destination/file.txt",
        "-n", "file_on_server.txt",
        "-r", "protocol1",
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        parse_arguments()
    assert excinfo.value.code != 0

    # Caso: Falta el argumento obligatorio --dst para el comando download
    test_args = [
        "program_name",
        "download",
        "-H", "127.0.0.1",
        "-p", "8080",
        "-n", "file_on_server.txt",
        "-r", "protocol1",
    ]
    monkeypatch.setattr(sys, "argv", test_args)

    with pytest.raises(SystemExit) as excinfo:
        parse_arguments()
    assert excinfo.value.code != 0