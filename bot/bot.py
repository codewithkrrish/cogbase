"""The bot itself: a thin discord.py subclass, nothing more.

All real decisions live in the small modules next to this file
(config, logging, error text, cog discovery). This class just wires
them together, so reading it top to bottom tells you the whole
startup story.
"""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

from bot.cogs_loader import discover_extensions
from bot.config import Config
from bot.errors import describe_error

log = logging.getLogger("cogbase")


class CogBaseBot(commands.Bot):
    """A commands.Bot with cog auto-loading and a friendly error handler."""

    def __init__(self, config: Config) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=config.prefix, intents=intents)
        self.config = config

    async def setup_hook(self) -> None:
        """Load every discovered cog before the bot connects."""
        extensions = self.config.extensions or discover_extensions("cogs")
        for extension in extensions:
            try:
                await self.load_extension(extension)
                log.info("Loaded %s", extension)
            except Exception:
                # One broken cog must not kill the whole bot at startup,
                # but it must not fail silently either.
                log.exception("Failed to load %s", extension)
        if self.config.sync_commands:
            synced = await self.tree.sync()
            log.info("Synced %d slash command(s)", len(synced))

    async def on_ready(self) -> None:
        """Log a plain startup line once the gateway is up."""
        assert self.user is not None
        log.info("Logged in as %s (id %s)", self.user, self.user.id)

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Reply with a human message instead of a traceback in chat."""
        message = describe_error(error)
        if message is None:
            return
        try:
            await ctx.send(message)
        except discord.HTTPException:
            # The channel may be gone or the bot muted; log and move on.
            log.warning("Could not send error reply in %s", ctx.channel)
        if type(error).__name__ not in (
            "CommandNotFound",
            "MissingPermissions",
            "CheckFailure",
            "CommandOnCooldown",
            "MissingRequiredArgument",
            "BadArgument",
        ):
            log.exception("Unhandled command error in %s", ctx.command)
