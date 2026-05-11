"""Logging configuration for ai-scraper."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

# Shared console for consistent output
console = Console()


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    json_format: bool = False,
) -> None:
    """Set up logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional file path for logs.
        json_format: Use JSON format for logs.
    """
    handlers: list[logging.Handler] = [
        RichHandler(rich_tracebacks=True, console=console)
    ]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)

        if json_format:

            class JSONFormatter(logging.Formatter):
                def format(self, record: logging.LogRecord) -> str:
                    log_entry = {
                        "timestamp": self.formatTime(record),
                        "level": record.levelname,
                        "message": record.getMessage(),
                        "module": record.module,
                        "function": record.funcName,
                    }
                    return json.dumps(log_entry)

            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
        handlers.append(file_handler)

    logging.basicConfig(
        level=logging.getLevelName(level),
        format="%(message)s",
        handlers=handlers,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger.

    Args:
        name: Logger name.

    Returns:
        Configured logger.
    """
    return logging.getLogger(name)
