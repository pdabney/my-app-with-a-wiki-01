#!/usr/bin/env python3
"""Graph extractor for linkshort (materializer Stage 2 — EXTRACT).

Deterministic, stdlib-only. Emits {"nodes": [...], "edges": [...]} JSON:
  * function/method nodes with intent + facts (params/returns/raises/feature/flag)
  * flag nodes read from flags.yml
  * `gated-by` edges from a function to the flag that guards it
  * `raises` edges from a function to each exception type

Usage: python3 tools/extract.py [SRC_DIR]
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

from flags_registry import load_flags

LANG = "python"
TAG_RE = re.compile(r"@(\w+)\b")
REPO = Path(__file__).resolve().parent.parent


def parse_tags(docstring: str) -> dict[str, list[str]]:
    tags: dict[str, list[str]] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if current is not None:
            tags.setdefault(current, []).append(" ".join(buffer).strip())
        buffer = []

    for raw in docstring.splitlines():
        line = raw.strip()
        m = TAG_RE.match(line)
        if m:
            flush()
            current = m.group(1)
            buffer = [line[m.end():].strip()]
        elif current is not None:
            buffer.append(line)
    flush()
    return tags


def signature_params(fn) -> list[str]:
    a = fn.args
    names = [arg.arg for arg in (a.posonlyargs + a.args + a.kwonlyargs)]
    if a.vararg:
        names.append(a.vararg.arg)
    if a.kwarg:
        names.append(a.kwarg.arg)
    return [n for n in names if n not in ("self", "cls")]


def raised_types(fn) -> list[str]:
    types: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Raise) and node.exc is not None:
            exc = node.exc
            if isinstance(exc, ast.Call):
                exc = exc.func
            if isinstance(exc, ast.Name):
                types.add(exc.id)
            elif isinstance(exc, ast.Attribute):
                types.add(exc.attr)
    return sorted(types)


def returns_type(fn) -> str | None:
    if fn.returns is not None:
        text = ast.unparse(fn.returns)
        return None if text == "None" else text
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and node.value is not None:
            return "<value>"
    return None


def first(tags, key):
    return tags.get(key, [None])[0] and tags[key][0].split()[0] if tags.get(key) else None


def extract_file(path: Path) -> tuple[list[dict], list[dict]]:
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))
    nodes: list[dict] = []
    edges: list[dict] = []
    rel = path.relative_to(REPO)  # repo-relative → stable ids across machines/CI
    subsystem = f"{LANG}:{path.stem}"

    def handle(fn, qual: str, kind: str) -> None:
        if fn.name.startswith("_"):
            return
        doc = ast.get_docstring(fn)
        tags = parse_tags(doc) if doc else {}
        # The canonical raises list is the authored @raises (it includes exceptions
        # propagated from callees, which a lexical scan misses); the Tier-1 gate has
        # already verified every lexical raise appears here.
        raises = sorted({e.split()[0] for e in tags.get("raises", []) if e.split()})
        flag = first(tags, "flag")
        feature = first(tags, "feature")
        segment = ast.get_source_segment(source, fn) or ""
        node_id = f"{rel}#{qual}"
        nodes.append({
            "id": node_id,
            "type": kind,
            "title": qual,
            "intent": tags.get("intent", [None])[0],
            "facts": {
                "params": signature_params(fn),
                "returns": returns_type(fn),
                "raises": raises,
                "feature": feature,
                "flag": flag,
            },
            "subsystem": subsystem,
            "provenance": {
                "source_path": str(rel),
                "source_sha": hashlib.sha1(segment.encode()).hexdigest()[:12],
                "status": "verified",
                "extracted_by": "py-extractor@1",
            },
        })
        for exc in raises:
            edges.append({"from": node_id, "to": f"exception:{exc}", "type": "raises", "origin": "derived"})
        if flag:
            edges.append({"from": node_id, "to": f"flag:{flag}", "type": "gated-by", "origin": "authored"})

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            handle(node, node.name, "function")
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    handle(sub, f"{node.name}.{sub.name}", "method")
    return nodes, edges


def flag_nodes() -> list[dict]:
    nodes = []
    for name, meta in load_flags(REPO / "flags.yml").items():
        blob = json.dumps(meta, sort_keys=True)
        nodes.append({
            "id": f"flag:{name}",
            "type": "flag",
            "title": name,
            "intent": meta.get("description"),
            "facts": {"default": meta.get("default"), "owner": meta.get("owner")},
            "subsystem": "flags",
            "provenance": {
                "source_path": "flags.yml",
                "source_sha": hashlib.sha1(blob.encode()).hexdigest()[:12],
                "status": "verified",
                "extracted_by": "flags@1",
            },
        })
    return nodes


def main(argv: list[str]) -> int:
    src_root = Path(argv[1]) if len(argv) > 1 else REPO / "src"
    nodes: list[dict] = list(flag_nodes())
    edges: list[dict] = []
    for f in sorted(src_root.rglob("*.py")):
        n, e = extract_file(f)
        nodes.extend(n)
        edges.extend(e)
    print(json.dumps({"nodes": nodes, "edges": edges}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
