"""Logging setup for cogbase.

One function, one format, no surprises. discord.py is chatty at DEBUG
level, so this module keeps the library loggers at the chosen level
too instead of letting them spam the console while yours stays quiet.
"""

from __future__ import annotations

import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
DATE_FORMAT = "%H:%M:%S"


def setup_logging(level: str) -> logging.Logger:
    """Configure the root logger and return the bot's logger.

    Calling this twice does not stack duplicate handlers: existing
    handlers are cleared first. That matters because tests and
    reloads call it more than once.
    """
    numeric = getattr(logging, level.upper(), None)
    if not isinstance(numeric, int):
        raise ValueError(f"Unknown log level: {level!r}")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(numeric)
    # Keep discord.py's own loggers in step with ours.
    for name in ("discord", "discord.http"):
        logging.getLogger(name).setLevel(numeric)
    return logging.getLogger("cogbase")
