import logging
import sys
from typing import Optional
from ..config.settings import settings


def setup_logging(
    service_name: str,
    log_level: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup standardized logging for a service.

    Args:
        service_name: Name of the service for logger identification
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages

    Returns:
        Configured logger instance
    """
    if log_level is None:
        log_level = settings.log_level

    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Create formatter and add it to the handler
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Prevent duplicate logs from parent loggers
    logger.propagate = False

    return logger


def get_logger(service_name: str) -> logging.Logger:
    """
    Get a logger instance for a service.

    Args:
        service_name: Name of the service

    Returns:
        Logger instance
    """
    return logging.getLogger(service_name)


# Default logger setup
def setup_basic_logging():
    """Setup basic logging configuration for all services."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
