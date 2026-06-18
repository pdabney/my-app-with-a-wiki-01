#!/usr/bin/env python3
"""Tier-1 metadata gate for linkshort (deterministic, stdlib-only).

Verifies each public function's colocated contract against the code:

  * @intent present
  * @param names == the signature's parameters
  * @returns present when the function returns a value
  * @raises types == the exceptions actually raised in the body
  * @flag (if present) names a flag that exists in flags.yml   ← feature-flag drift gate

Stale metadata is a build failure. Usage: python3 tools/check_metadata.py [SRC_DIR]
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from flags_registry import load_flags

TAG_RE = re.compile(r"@(\w+)\b")
REPO = Path(__file__).resolve().parents[2]  # .github/tools/ -> repo root


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


def signature_params(fn) -> set[str]:
    a = fn.args
    names = [arg.arg for arg in (a.posonlyargs + a.args + a.kwonlyargs)]
    if a.vararg:
        names.append(a.vararg.arg)
    if a.kwarg:
        names.append(a.kwarg.arg)
    return {n for n in names if n not in ("self", "cls")}


def documented_params(tags) -> set[str]:
    return {e.split()[0].rstrip(":") for e in tags.get("param", []) if e.split()}


def raised_types(fn) -> set[str]:
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
    return types


def returns_value(fn) -> bool:
    if fn.returns is not None:
        ann = fn.returns
        if isinstance(ann, ast.Constant) and ann.value is None:
            return False
        if isinstance(ann, ast.Name) and ann.id == "None":
            return False
        return True
    return any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(fn))


def check_file(path: Path, known_flags: set[str]) -> list[str]:
    errors: list[str] = []
    tree = ast.parse(path.read_text(), filename=str(path))
    funcs = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append((node, node.name))
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcs.append((sub, f"{node.name}.{sub.name}"))

    for fn, qual in funcs:
        if fn.name.startswith("_"):
            continue
        loc = f"{path}:{fn.lineno} {qual}()"
        doc = ast.get_docstring(fn)
        if not doc:
            errors.append(f"{loc}: public function has no docstring/contract")
            continue
        tags = parse_tags(doc)
        if not tags.get("intent"):
            errors.append(f"{loc}: missing @intent")
        sig, documented = signature_params(fn), documented_params(tags)
        if sig - documented:
            errors.append(f"{loc}: @param missing for {sorted(sig - documented)}")
        if documented - sig:
            errors.append(f"{loc}: @param documents unknown {sorted(documented - sig)}")
        if returns_value(fn) and not tags.get("returns"):
            errors.append(f"{loc}: returns a value but has no @returns")
        # Tier-1 only enforces the direction it can verify without false positives:
        # every exception raised *lexically* in this body must be documented. The
        # reverse ("is a declared exception actually raised?") can't be checked here
        # because exceptions are often propagated from callees (e.g. store._get());
        # confirming those is Tier-2's (semantic) job.
        raised = raised_types(fn)
        declared = {e.split()[0] for e in tags.get("raises", []) if e.split()}
        if raised - declared:
            errors.append(f"{loc}: raises {sorted(raised - declared)} not in @raises")
        for flag in (e.split()[0] for e in tags.get("flag", []) if e.split()):
            if flag not in known_flags:
                errors.append(f"{loc}: @flag {flag!r} is not defined in flags.yml")
    return errors


def main(argv: list[str]) -> int:
    src_root = Path(argv[1]) if len(argv) > 1 else REPO / "src"
    known_flags = set(load_flags(REPO / "flags.yml"))
    errors: list[str] = []
    files = sorted(src_root.rglob("*.py"))
    for f in files:
        errors.extend(check_file(f, known_flags))

    if errors:
        print("Metadata contract check FAILED:\n")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\n{len(errors)} problem(s). Stale metadata is a build failure.")
        return 1
    print(f"Metadata contract check passed ✓  ({len(files)} file(s), {len(known_flags)} flag(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
