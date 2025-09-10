"""Logging configuration utilities for common components."""

import logging
import sys
from typing import Optional


def configure_basic_logger(
    logger_name: Optional[str] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    stream=None
) -> logging.Logger:
    """Configure a basic logger with console output.

    Args:
        logger_name: Name of the logger. If None, configures the root logger.
        level: Logging level (e.g., logging.INFO, logging.DEBUG).
        format_string: Custom format string for log messages.
        stream: Output stream for the handler. Defaults to sys.stdout.

    Returns:
        Configured logger instance.
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if stream is None:
        stream = sys.stdout

    # Get or create logger
    logger = logging.getLogger(logger_name)

    # Only configure if no handlers exist to avoid duplicate logs
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(stream)
        handler.setLevel(level)

        # Create formatter and add to handler
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger


def setup_application_logging(level: int = logging.INFO) -> None:
    """Setup basic logging configuration for the entire application.

    This function configures the root logger with a console handler.

    Args:
        level: Logging level for the application.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
