"""Help cog: a plain, readable replacement for the default help.

discord.py's built-in help is fine, but every bot ends up replacing
it anyway, so this template ships the replacement up front. It lists
commands grouped by cog, and ``!help <command>`` shows one command's
usage. No embeds with ten fields — just text a user can actually read.
"""

from __future__ import annotations

from discord.ext import commands


class Help(commands.Cog):
    """A small custom help command."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # Take over from the built-in help so there is exactly one.
        self.bot.remove_command("help")

    def format_command_list(self) -> str:
        """Render every visible command, grouped by cog name."""
        lines = ["Commands:"]
        for cog_name, cog in self.bot.cogs.items():
            visible = [c for c in cog.get_commands() if not c.hidden]
            if not visible:
                continue
            lines.append(f"\n{cog_name}:")
            for command in visible:
                brief = (command.short_doc or "").strip()
                lines.append(f"  {self.bot.command_prefix}{command.name} - {brief}")
        return "\n".join(lines)

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context, *, name: str = "") -> None:
        """Show all commands, or details for one command.

        Usage: ``!help`` or ``!help ping``.
        """
        if not name:
            await ctx.send(f"```\n{self.format_command_list()}\n```")
            return
        command = self.bot.get_command(name)
        if command is None:
            await ctx.send(f"No command named {name!r}. Try `!help` for the list.")
            return
        usage = f"{self.bot.command_prefix}{command.qualified_name} {command.signature}"
        await ctx.send(f"```\n{usage}\n{(command.help or '').strip()}\n```")


async def setup(bot: commands.Bot) -> None:
    """Entry point discord.py calls when loading this cog."""
    await bot.add_cog(Help(bot))
