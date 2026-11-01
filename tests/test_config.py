"""Tests for bot.config. No discord.py needed: config is pure stdlib."""

import pytest

from bot.config import Config, ConfigError


def test_defaults_applied():
    config = Config.from_env({"DISCORD_TOKEN": "abc"})
    assert config.prefix == "!"
    assert config.log_level == "INFO"
    assert config.sync_commands is False
    assert config.extensions == ()


def test_full_environment_parsed():
    config = Config.from_env(
        {
            "DISCORD_TOKEN": "  token123  ",
            "BOT_PREFIX": "?",
            "LOG_LEVEL": "debug",
            "SYNC_COMMANDS": "true",
            "COGS": "cogs.ping, cogs.help ",
        }
    )
    assert config.token == "token123"
    assert config.prefix == "?"
    assert config.log_level == "DEBUG"
    assert config.sync_commands is True
    assert config.extensions == ("cogs.ping", "cogs.help")


def test_missing_token_rejected():
    with pytest.raises(ConfigError, match="DISCORD_TOKEN"):
        Config.from_env({})


def test_blank_token_rejected():
    with pytest.raises(ConfigError, match="DISCORD_TOKEN"):
        Config.from_env({"DISCORD_TOKEN": "   "})


def test_blank_prefix_rejected():
    with pytest.raises(ConfigError, match="BOT_PREFIX"):
        Config.from_env({"DISCORD_TOKEN": "x", "BOT_PREFIX": "  "})


def test_bad_log_level_rejected():
    with pytest.raises(ConfigError, match="LOG_LEVEL"):
        Config.from_env({"DISCORD_TOKEN": "x", "LOG_LEVEL": "VERBOSE"})


def test_safe_summary_never_contains_token():
    config = Config.from_env({"DISCORD_TOKEN": "super-secret-token"})
    assert "super-secret-token" not in config.safe_summary()
    assert "prefix='!'" in config.safe_summary()


@pytest.mark.parametrize("value,expected", [("1", True), ("yes", True), ("on", True), ("0", False), ("no", False), ("", False)])
def test_bool_parsing(value, expected):
    config = Config.from_env({"DISCORD_TOKEN": "x", "SYNC_COMMANDS": value})
    assert config.sync_commands is expected
