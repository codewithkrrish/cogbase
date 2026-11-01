"""Configuration for cogbase.

Everything comes from the environment, nothing is hardcoded. The bot
refuses to start with a clear message when something required is
missing, instead of dying halfway through connecting to Discord.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

DEFAULT_PREFIX = "!"
DEFAULT_LOG_LEVEL = "INFO"
VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class ConfigError(ValueError):
    """Raised when the environment does not hold a usable configuration."""


@dataclass(frozen=True)
class Config:
    """A validated, ready-to-use bot configuration.

    Attributes:
        token: Discord bot token. Never logged, never printed.
        prefix: Command prefix, e.g. ``!``.
        log_level: One of the standard logging level names.
        sync_commands: When true, slash commands are synced on startup.
        extensions: Cog module names to load, in order.
    """

    token: str
    prefix: str = DEFAULT_PREFIX
    log_level: str = DEFAULT_LOG_LEVEL
    sync_commands: bool = False
    extensions: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Config":
        """Build a Config from environment variables.

        Args:
            env: Mapping to read from; defaults to ``os.environ``. Tests
                pass a plain dict so they never touch the real environment.

        Raises:
            ConfigError: If the token is missing/blank, the prefix is
                empty, or the log level is not a known level.
        """
        source = os.environ if env is None else env
        token = (source.get("DISCORD_TOKEN") or "").strip()
        if not token:
            raise ConfigError(
                "DISCORD_TOKEN is not set. Copy .env.example to .env "
                "and paste your bot token there."
            )
        prefix = (source.get("BOT_PREFIX") or DEFAULT_PREFIX).strip()
        if not prefix:
            raise ConfigError("BOT_PREFIX must not be blank.")
        log_level = (source.get("LOG_LEVEL") or DEFAULT_LOG_LEVEL).strip().upper()
        if log_level not in VALID_LOG_LEVELS:
            raise ConfigError(
                f"LOG_LEVEL must be one of {', '.join(VALID_LOG_LEVELS)}, "
                f"got {log_level!r}."
            )
        sync_commands = _parse_bool(source.get("SYNC_COMMANDS", "0"))
        raw_extensions = (source.get("COGS") or "").strip()
        extensions = tuple(
            part.strip() for part in raw_extensions.split(",") if part.strip()
        )
        return cls(
            token=token,
            prefix=prefix,
            log_level=log_level,
            sync_commands=sync_commands,
            extensions=extensions,
        )

    def safe_summary(self) -> str:
        """A log-safe one-line summary. The token is never included."""
        return (
            f"prefix={self.prefix!r} log_level={self.log_level} "
            f"sync_commands={self.sync_commands} cogs={len(self.extensions)}"
        )


def _parse_bool(value: str) -> bool:
    """Parse a loose boolean env value (1/true/yes/on, case-insensitive)."""
    return value.strip().lower() in ("1", "true", "yes", "on")
