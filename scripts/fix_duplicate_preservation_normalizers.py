#!/usr/bin/env python3
"""Remove duplicate repository-preservation normalizer definitions safely."""
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts/repository_preservation_refresh.py"
TARGET_NAMES = {"baseline_tree_limitation", "normalize_limitations"}


def top_level_definitions(source: str) -> dict[str, list[ast.FunctionDef]]:
    tree = ast.parse(source, filename=str(TARGET))
    result: dict[str, list[ast.FunctionDef]] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            result.setdefault(node.name, []).append(node)
    return result


def main() -> int:
    source = TARGET.read_text(encoding="utf-8")
    definitions = top_level_definitions(source)
    removals: list[ast.FunctionDef] = []
    for name in sorted(TARGET_NAMES):
        nodes = definitions.get(name, [])
        if len(nodes) == 1:
            continue
        if len(nodes) != 2:
            raise SystemExit(
                f"unexpected top-level definition count for {name}: {len(nodes)}"
            )
        removals.append(nodes[0])

    if removals:
        lines = source.splitlines(keepends=True)
        for node in sorted(removals, key=lambda item: item.lineno, reverse=True):
            if node.end_lineno is None:
                raise SystemExit(f"missing end line for {node.name}")
            start = node.lineno - 1
            end = node.end_lineno
            while end < len(lines) and not lines[end].strip():
                end += 1
            del lines[start:end]
        source = "".join(lines)
        compile(source, str(TARGET), "exec")
        TARGET.write_text(source, encoding="utf-8")

    verified = top_level_definitions(TARGET.read_text(encoding="utf-8"))
    for name in sorted(TARGET_NAMES):
        if len(verified.get(name, [])) != 1:
            raise SystemExit(f"duplicate normalizer remains: {name}")
    print("PRESERVATION_NORMALIZER_DEFINITIONS_UNIQUE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
