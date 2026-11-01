"""User-friendly error messages for command failures.

This module deliberately does NOT import discord.py. The mapping works
on exception attributes and class names (duck typing), so the text a
user sees can be unit-tested without a gateway connection, and so a
new discord.py release renaming an exception class degrades to the
generic message instead of crashing the error handler itself.
"""

from __future__ import annotations

# Error class names we translate, keyed by the discord.py name.
# UnknownCommand is intentionally absent: silently ignoring a typo'd
# command is kinder than replying "unknown command" to every chat typo.
_KNOWN_MESSAGES: dict[str, str] = {
    "MissingPermissions": "You don't have permission to use that command.",
    "BotMissingPermissions": "I don't have permission to do that here.",
    "CheckFailure": "You can't use that command here.",
    "NotOwner": "Only the bot owner can use that command.",
    "MissingRequiredArgument": "You're missing an argument. Check the usage and try again.",
    "BadArgument": "One of those arguments doesn't look right. Check it and try again.",
    "CommandInvokeError": "That command hit an error on my side. I've logged it.",
}

_GENERIC_MESSAGE = "Something went wrong running that command. Try again in a bit."


def describe_error(exc: BaseException) -> str | None:
    """Return the message to send to the user, or None to stay silent.

    Returns None for errors that should never produce a reply (unknown
    commands, and cooldowns are handled separately because they carry a
    retry delay). Cooldowns return a message with the wait time rounded
    up to whole seconds.
    """
    name = type(exc).__name__
    if name == "CommandNotFound":
        return None
    if name == "CommandOnCooldown":
        retry_after = getattr(exc, "retry_after", 0.0)
        try:
            seconds = max(1, int(float(retry_after)) + 1)
        except (TypeError, ValueError):
            seconds = 1
        return f"Slow down — try that again in {seconds}s."
    # Some errors wrap the real one (CommandInvokeError carries it as
    # .original); report the inner cause when we know it, since that
    # is the message the user can actually act on.
    original = getattr(exc, "original", None)
    if original is not None and type(original).__name__ in _KNOWN_MESSAGES:
        return _KNOWN_MESSAGES[type(original).__name__]
    return _KNOWN_MESSAGES.get(name, _GENERIC_MESSAGE)
