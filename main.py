"""Entry point for cogbase: ``python main.py``.

Startup failures print one plain sentence and exit with a distinct
code, so a deploy log tells you what went wrong without scrolling
through a traceback. Exit codes: 0 ok, 2 bad config, 3 login failure,
4 missing dependency, 130 interrupted by the user.
"""

from __future__ import annotations

import asyncio
import sys

from bot.config import Config, ConfigError
from bot.logging_setup import setup_logging

try:
    # Optional: if python-dotenv is installed, .env is loaded before
    # config is read, so `cp .env.example .env` just works.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

EXIT_OK = 0
EXIT_CONFIG = 2
EXIT_LOGIN = 3
EXIT_DEPS = 4
EXIT_INTERRUPTED = 130


def main() -> int:
    """Build the config, start the bot, and translate failures."""
    try:
        config = Config.from_env()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    log = setup_logging(config.log_level)
    log.info("Starting cogbase (%s)", config.safe_summary())
    try:
        # Imported here, not at the top, so a missing discord.py
        # becomes a plain sentence instead of a traceback.
        from bot.bot import CogBaseBot
    except ImportError:
        print(
            "error: discord.py is not installed. Run: pip install -r requirements.txt",
            file=sys.stderr,
        )
        return EXIT_DEPS
    bot = CogBaseBot(config)
    try:
        asyncio.run(bot.start(config.token))
    except KeyboardInterrupt:
        log.info("Shutting down.")
        return EXIT_INTERRUPTED
    except Exception as exc:  # LoginFailure, HTTP 429s, bad gateway, etc.
        # Deliberately broad: at this point the bot is dead either way,
        # and the user needs the reason, not a stack trace.
        print(f"error: could not log in or stay connected: {exc}", file=sys.stderr)
        return EXIT_LOGIN
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
