"""Cog discovery for cogbase.

The loader reads the ``cogs/`` directory instead of a hardcoded list,
so adding a cog is just adding a file. Files starting with an
underscore (like ``_template.py``) are skipped on purpose: they are
examples to copy, not cogs to load.
"""

from __future__ import annotations

from pathlib import Path

SKIP_PREFIX = "_"


def discover_extensions(cogs_dir: str | Path) -> list[str]:
    """Return sorted ``cogs.<module>`` names found in ``cogs_dir``.

    Only ``.py`` files are considered. ``__init__.py`` and
    underscore-prefixed files are skipped. The result is sorted so
    load order is stable across machines and filesystems.
    """
    directory = Path(cogs_dir)
    if not directory.is_dir():
        return []
    names: list[str] = []
    for path in directory.iterdir():
        if path.suffix != ".py":
            continue
        if path.stem == "__init__" or path.stem.startswith(SKIP_PREFIX):
            continue
        names.append(f"cogs.{path.stem}")
    return sorted(names)
