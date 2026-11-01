"""Tests for bot.cogs_loader, plus a sanity pass over the whole tree.

The sanity test compiles every .py file and checks each cog defines
an async ``setup`` function — the two things that break a template
most often, and both checkable without discord.py installed.
"""

import ast
import py_compile
from pathlib import Path

import pytest

from bot.cogs_loader import discover_extensions

ROOT = Path(__file__).resolve().parent.parent


def test_discovers_real_cogs_sorted():
    found = discover_extensions(ROOT / "cogs")
    assert found == ["cogs.help", "cogs.ping"]


def test_underscore_files_and_init_skipped(tmp_path):
    (tmp_path / "__init__.py").write_text("")
    (tmp_path / "_template.py").write_text("")
    (tmp_path / "notes.txt").write_text("not a cog")
    (tmp_path / "music.py").write_text("")
    assert discover_extensions(tmp_path) == ["cogs.music"]


def test_missing_directory_is_empty_not_an_error(tmp_path):
    assert discover_extensions(tmp_path / "nope") == []


def test_empty_directory_is_empty(tmp_path):
    assert discover_extensions(tmp_path) == []


def test_all_python_files_compile():
    failures = []
    for path in sorted(ROOT.rglob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"{path}: {exc}")
    assert not failures, "\n".join(failures)


def test_every_cog_defines_async_setup():
    for path in sorted((ROOT / "cogs").glob("*.py")):
        if path.stem == "__init__":
            continue
        tree = ast.parse(path.read_text())
        setups = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "setup"
        ]
        assert setups, f"{path.name} has no async setup() — discord.py can't load it"
