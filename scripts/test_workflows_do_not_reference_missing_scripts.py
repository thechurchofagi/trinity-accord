#!/usr/bin/env python3
"""Fail if workflows or run_ci_group reference missing local script files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_PATHS = [ROOT / ".github" / "workflows", ROOT / "scripts" / "run_ci_group.py"]

PY_RE = re.compile(r"(?:python|python3)\s+(scripts/[A-Za-z0-9_./-]+\.py)")
NODE_RE = re.compile(r"node\s+([A-Za-z0-9_./-]+\.mjs)")


def iter_text_files(path: Path):
    if path.is_file():
        yield path
        return
    if path.exists():
        yield from sorted(path.glob("*.yml"))
        yield from sorted(path.glob("*.yaml"))


def main() -> int:
    missing: list[str] = []
    for path in SCAN_PATHS:
        for file_path in iter_text_files(path):
            text = file_path.read_text(encoding="utf-8")
            for pattern in (PY_RE, NODE_RE):
                for match in pattern.finditer(text):
                    rel = match.group(1)
                    if not (ROOT / rel).exists():
                        missing.append(f"{file_path.relative_to(ROOT)} references missing {rel}")

    if missing:
        raise SystemExit("\n".join(missing))
    print("PASS: workflows and run_ci_group do not reference missing scripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
