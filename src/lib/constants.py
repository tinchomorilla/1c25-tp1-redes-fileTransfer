# Tipos de mensaje
import struct


TYPE_DATA = 0
TYPE_ACK = 1
TYPE_INIT = 2
TYPE_INIT_ACK = 3
TYPE_READY = 4
TYPE_DONE = 5

# Formato del encabezado: !BBH = (tipo, secuencia, longitud)
HEADER_FMT = "!BBH"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
TIMEOUT = 10.0  # segundos
MAX_DATA_SIZE = 1024 - HEADER_SIZE

DOWNLOAD_DONE_MARKER = b"__DOWNLOAD_DONE__"
UPLOAD_DONE_MARKER = b"__UPLOAD_DONE__"
