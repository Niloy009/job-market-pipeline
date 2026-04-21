"""Shared logging configuration for the job market pipeline.

Import the logger from this module in any other module to ensure
consistent log formatting across the entire codebase.

Typical usage:
    from src.logger import get_logger
    logger = get_logger(__name__)
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """Create and return a configured logger instance.

    Args:
        name: The name of the logger, typically __name__
            from the calling module.

    Returns:
        A configured Logger instance with a standard formatter.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s — %(levelname)s — %(message)s",
    )
    return logging.getLogger(name)
