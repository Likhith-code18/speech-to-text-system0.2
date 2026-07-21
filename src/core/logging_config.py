"""
Logging configuration for the Speech-to-Text subsystem.

Called once, at application startup, so every module can simply do
`logging.getLogger(__name__)` and rely on consistent formatting/level.
"""

import logging


def setup_logging(level: str = "INFO") -> None:
    """
    Configure the root logger for the application.

    Args:
        level: Logging level name (e.g. "DEBUG", "INFO", "WARNING").
            Falls back to INFO if the value is not a recognized level.
    """
    resolved_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
