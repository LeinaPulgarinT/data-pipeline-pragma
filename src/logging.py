import logging
import os
import sys


def setup_logging() -> None:
    """Configura el sistema de logging de la aplicación.

    Lee el nivel desde la variable de entorno LOG_LEVEL (por defecto INFO)
    y escribe los logs en stdout.
    """
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
