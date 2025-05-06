import logging
import sys

from lib.Common.constants import COLOUR_BLUE, COLOUR_END, COLOUR_GREEN, COLOUR_RED

def initialize_logger(debug_level, action_name):
    color = COLOUR_BLUE
    if action_name == "upload":
        color = COLOUR_GREEN
    elif action_name == "download":
        color = COLOUR_RED

    logger = logging.getLogger(f"filetransfer.{action_name}")  # logger con nombre único
    logger.setLevel(debug_level)
    logger.propagate = False  # ⛔️ evita que los logs suban al root logger

    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            f"[{color}{action_name}{COLOUR_END} %(levelname)s] - %(message)s",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger