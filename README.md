# cogbase

Every Discord bot I start begins with the same three files: config from
the environment, logging that isn't a mess, and an error handler that
doesn't dump tracebacks into chat. I kept rewriting them, so I finally
pulled them into one template I can clone and actually start from.

cogbase is an opinionated discord.py starter: cogs that load themselves
from a folder, env-based config that fails fast with a plain message,
a readable custom help command, and error replies a normal user can
understand. No database, no dashboard, no framework on top of the
framework — just the boring parts, done once.

## Quickstart

You need Python 3.10 or newer and a bot token from the
[Discord developer portal](https://discord.com/developers/applications)
(with the Message Content intent enabled).

```bash
git clone https://github.com/codewithkrrish/cogbase.git
cd cogbase
pip install -r requirements.txt
cp .env.example .env
# open .env and paste your token
python main.py
```

If it works, `!ping` answers with the latency and `!help` lists the
commands. If it doesn't, you get one sentence saying why — usually a
missing token — instead of a traceback.

## Adding a cog

Copy `cogs/_template.py` to a new file in `cogs/`, rename the class,
write your commands. That's it. The loader picks up every `.py` file in
`cogs/` on startup, in sorted order, so there is no list to update and
nothing to forget. Files starting with an underscore are never loaded,
which is why the template itself lives as `_template.py`.

Want a fixed load order or to disable a cog without deleting it? Set
`COGS` in `.env` to a comma-separated list — when it's set, only those
cogs load:

```
COGS=cogs.ping,cogs.help
```

## Slash commands

The ping cog ships both `!ping` and `/ping`. Slash commands only sync
when you ask for them, because syncing on every restart burns your
hourly rate limit for nothing:

```
SYNC_COMMANDS=1
```

Run once with that set, then turn it back off.

## Configuration

Everything lives in `.env`. Nothing secret is ever printed to the log —
the startup line shows the prefix and cog count, never the token.

| Variable        | Default | What it does                                    |
| --------------- | ------- | ----------------------------------------------- |
| `DISCORD_TOKEN` | —       | Your bot token. Required, no default.           |
| `BOT_PREFIX`    | `!`     | Prefix for text commands.                       |
| `LOG_LEVEL`     | `INFO`  | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `SYNC_COMMANDS` | `0`     | Set to `1` to sync slash commands on startup.  |
| `COGS`          | —       | Comma-separated cog list; unset means auto-load. |

## Project structure

```
main.py               entry point, exit codes for startup failures
bot/
  bot.py              the Bot subclass: wiring, nothing else
  config.py           env parsing + validation (ConfigError on bad input)
  logging_setup.py    one format, no duplicate handlers
  errors.py           command errors -> plain user-facing messages
  cogs_loader.py      discovers cogs/*.py, skips _-prefixed files
cogs/
  ping.py             !ping and /ping, the smoke test
  help.py             custom !help, grouped by cog
  _template.py        copy this to start a new cog (never loaded)
tests/                pytest, runs without discord.py installed
```

## Running the tests

```bash
python -m pytest
```

The tests cover config parsing, error messages, cog discovery, and a
compile check over every file. They deliberately don't import
discord.py: the error text works off exception names and attributes,
so the messages users see can be tested without a gateway connection.
The bot and cog files themselves are covered by the compile + AST
check in `test_cogs_loader.py`.

## Limitations, honestly

- No database layer. If your bot needs to remember things, add one —
  I didn't want to pick your database for you.
- Prefix commands plus a couple of slash commands, not a slash-first
  design. The template cog is prefix-based; the ping cog shows the
  slash pattern when you need it.
- One process, no sharding. Fine for the small servers this template
  is for, wrong for a bot in thousands of guilds.
- The error handler only knows the common discord.py failures. Weird
  new ones fall back to a generic message and a log entry, which is
  still better than a traceback in chat.

## TODOs I haven't got to yet

- An example cog showing a background task loop.
- A `docker-compose.yml` for people who deploy that way.

## License

MIT — see [LICENSE](LICENSE). Built by
[Krrish](https://github.com/codewithkrrish).
