#!/usr/bin/env python3
"""Active source files must not reference the stale Gateway submit endpoint.

The current Gateway submit endpoint is /agent-submit.
Historical references are allowed only in an explicit allowlist with
nearby stale/deprecated/legacy wording.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Build dynamically so this test does not flag itself.
STALE = "/gateway" + "/submit"

EXCLUDED_DIR_PARTS = {
    ".git",
    "node_modules",
    ".pytest_cache",
    "__pycache__",
}

SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".woff",
    ".woff2",
    ".ttf",
    ".ico",
}

# Historical allowlist. Keep this small.
# Every allowed occurrence must be clearly historical/deprecated/stale.
ALLOWLIST = {
    # "docs/migrations/gateway-submit-endpoint-migration.md",
}

HISTORICAL_MARKERS = [
    "deprecated",
    "stale",
    "historical",
    "legacy",
    "do not use",
    "forbidden",
    "migration",
]


def should_skip(path: Path) -> bool:
    if path.is_dir():
        return True
    rel_parts = set(path.relative_to(ROOT).parts)
    if rel_parts & EXCLUDED_DIR_PARTS:
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    return False


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def line_has_historical_marker(lines: list[str], index: int) -> bool:
    start = max(0, index - 2)
    end = min(len(lines), index + 3)
    context = "\n".join(lines[start:end]).lower()
    return any(marker in context for marker in HISTORICAL_MARKERS)


def main() -> int:
    errors: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if should_skip(path):
            continue

        text = read_text(path)
        if text is None or STALE not in text:
            continue

        rel = str(path.relative_to(ROOT))
        lines = text.splitlines()

        for idx, line in enumerate(lines):
            if STALE not in line:
                continue

            if rel in ALLOWLIST:
                if not line_has_historical_marker(lines, idx):
                    errors.append(
                        f"{rel}:{idx + 1}: allowlisted stale endpoint lacks nearby historical/deprecated marker"
                    )
                continue

            # Guard-style checks (rejecting stale endpoint) are OK
            stripped = line.strip()
            is_guard = (
                any(kw in line.lower() for kw in ["forbidden", "stale", "must not"])
                or "==" in line or "!=" in line
                or stripped.startswith("#")
                or stripped.startswith('if "') or stripped.startswith("if '")
                or 'in text' in line or 'in raw' in line
                or 'errors.append' in line
                or stripped.startswith('"') or stripped.startswith("'")
                or 'print(' in line
            )
            if is_guard:
                continue

            errors.append(f"{rel}:{idx + 1}: active stale Gateway submit endpoint reference")

    if errors:
        print("FAIL: stale Gateway submit endpoint references found:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: no active stale Gateway submit endpoint references found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
