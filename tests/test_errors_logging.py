"""Tests for bot.errors and bot.logging_setup (both discord-free)."""

import logging

import pytest

from bot.errors import describe_error
from bot.logging_setup import setup_logging


def _named(name, **attrs):
    cls = type(name, (Exception,), {})
    exc = cls(name)
    for key, value in attrs.items():
        setattr(exc, key, value)
    return exc


def test_unknown_command_stays_silent():
    assert describe_error(_named("CommandNotFound")) is None


def test_cooldown_message_rounds_up():
    message = describe_error(_named("CommandOnCooldown", retry_after=4.2))
    assert message == "Slow down — try that again in 5s."


def test_cooldown_with_bad_delay_still_answers():
    message = describe_error(_named("CommandOnCooldown", retry_after="nope"))
    assert message == "Slow down — try that again in 1s."


def test_known_errors_get_plain_messages():
    assert "permission" in describe_error(_named("MissingPermissions")).lower()
    assert "owner" in describe_error(_named("NotOwner")).lower()


def test_wrapped_error_reports_inner_cause():
    inner = _named("MissingPermissions")
    outer = _named("CommandInvokeError")
    outer.original = inner
    assert "permission" in describe_error(outer).lower()


def test_unknown_error_gets_generic_message():
    message = describe_error(_named("SomethingWeird"))
    assert "went wrong" in message


def test_setup_logging_sets_level_and_is_idempotent():
    logger = setup_logging("WARNING")
    assert logging.getLogger().level == logging.WARNING
    first_count = len(logging.getLogger().handlers)
    setup_logging("WARNING")
    # No duplicate handlers stacked on the second call.
    assert len(logging.getLogger().handlers) == first_count
    assert logger.name == "cogbase"


def test_setup_logging_rejects_bad_level():
    with pytest.raises(ValueError, match="Unknown log level"):
        setup_logging("VERBOSE")
