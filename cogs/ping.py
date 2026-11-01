"""Ping cog: the smoke test every bot needs.

``!ping`` answers with the gateway latency, and ``/ping`` does the
same as a slash command. If this cog loads and answers, your token,
intents, and prefix all work — everything else is your own code.
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class Ping(commands.Cog):
    """Latency check, as both a prefix and a slash command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="ping")
    async def ping_prefix(self, ctx: commands.Context) -> None:
        """Reply with the current gateway latency."""
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping_slash(self, interaction: discord.Interaction) -> None:
        """Slash version of the same check."""
        await interaction.response.send_message(
            f"Pong! {round(self.bot.latency * 1000)}ms"
        )


async def setup(bot: commands.Bot) -> None:
    """Entry point discord.py calls when loading this cog."""
    await bot.add_cog(Ping(bot))
