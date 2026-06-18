"""Minimal reader for flags.yml (stdlib only — no PyYAML dependency).

Parses exactly the shape this repo uses:

    flags:
      <name>:
        description: ...
        default: true|false
        owner: ...

Returns {name: {description, default, owner}}.
"""
from __future__ import annotations

from pathlib import Path


def _scalar(v: str):
    v = v.strip().strip('"').strip("'")
    if v == "true":
        return True
    if v == "false":
        return False
    return v


def load_flags(path: str | Path = "flags.yml") -> dict[str, dict]:
    flags: dict[str, dict] = {}
    current: str | None = None
    in_flags = False
    for raw in Path(path).read_text().splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        if indent == 0:
            in_flags = stripped.startswith("flags:")
            current = None
        elif in_flags and indent == 2 and stripped.endswith(":"):
            current = stripped[:-1]
            flags[current] = {}
        elif in_flags and indent >= 4 and current and ":" in stripped:
            key, _, value = stripped.partition(":")
            flags[current][key.strip()] = _scalar(value)
    return flags
