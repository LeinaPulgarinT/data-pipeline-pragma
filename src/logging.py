import logging
import os
import sys


def setup_logging() -> None:
    """Configure root logger for the application.

    Reads LOG_LEVEL from environment (default INFO). Logs to stdout.
    """
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # Basic configuration for the root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
