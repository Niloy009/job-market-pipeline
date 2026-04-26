"""Shared logging configuration."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a logger with a standard formatter.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        Configured :class:`logging.Logger` instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s — %(levelname)s — %(message)s",
    )
    return logging.getLogger(name)
