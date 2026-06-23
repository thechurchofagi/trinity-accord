#!/usr/bin/env python3
"""Fail if workflow fetch/rebase commands are folded into one shell line."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def iter_run_steps(node):
    if isinstance(node, dict):
        if isinstance(node.get("run"), str):
            yield node["run"]
        for value in node.values():
            yield from iter_run_steps(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_run_steps(value)


def main() -> int:
    errors: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for run in iter_run_steps(data):
            compact = " ".join(line.strip() for line in run.splitlines() if line.strip())
            if "git fetch origin main --prune git rebase origin/main" in compact:
                errors.append(f"{path.relative_to(ROOT)}: fetch/rebase folded into one invalid command")
            if "git fetch origin main --prune" in run and "git rebase origin/main" in run and "\n" not in run:
                errors.append(f"{path.relative_to(ROOT)}: fetch/rebase must be a multiline run block")

    if errors:
        raise SystemExit("\n".join(errors))
    print("PASS: workflow fetch/rebase run blocks are not folded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
