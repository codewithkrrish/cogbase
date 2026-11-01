"""Template cog — copy this file to start a new cog.

This file is NEVER loaded: the loader skips every file starting with
an underscore, which is exactly why this one is named ``_template.py``.
Copy it to ``cogs/mycog.py``, rename the class, and you are done.

Checklist when you copy it:
  1. Rename ``Template`` and the file.
  2. Keep the ``setup`` function at the bottom — discord.py needs it.
  3. Add a short docstring to each command; the help cog shows it.
"""

from __future__ import annotations

from discord.ext import commands


class Template(commands.Cog):
    """Replace this with your cog's purpose."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context) -> None:
        """Say hello. Delete this once your real commands exist."""
        await ctx.send(f"Hello, {ctx.author.display_name}!")


async def setup(bot: commands.Bot) -> None:
    """Entry point discord.py calls when loading this cog."""
    await bot.add_cog(Template(bot))
