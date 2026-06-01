#!/usr/bin/env python3
"""Scan active current tree for obvious private key / token patterns.

Do not print secret values. Fail on real-looking secrets.
Historical archive may contain fixture text - allow only fixture-labeled dummy values.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = [
    re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
    re.compile(r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----"),
    re.compile(r"-----BEGIN\s+EC\s+PRIVATE\s+KEY-----"),
    re.compile(r"PINATA_JWT\s*=\s*\S+"),
    re.compile(r"WEB3_STORAGE_TOKEN\s*=\s*\S+"),
    re.compile(r"LIGHTHOUSE_API_KEY\s*=\s*\S+"),
    re.compile(r"ARWEAVE_PRIVATE_KEY\s*=\s*\S+"),
]

# Directories to skip (historical archive, git internals)
SKIP_DIRS = {
    ".git",
    "legacy",
    "node_modules",
    "__pycache__",
}

# Extensions to scan
SCAN_EXTENSIONS = {
    ".py", ".js", ".mjs", ".ts", ".json", ".yml", ".yaml",
    ".md", ".txt", ".env", ".sh", ".bash", ".cfg", ".toml",
    ".ini", ".conf",
}

# Fixture indicators - if found near a match, it's a dummy value
FIXTURE_INDICATORS = [
    "fixture",
    "dummy",
    "example",
    "test",
    "mock",
    "fake",
    "sample",
    "placeholder",
    "REDACTED",
    "xxx",
    "CHANGEME",
]


def is_fixture_context(line: str) -> bool:
    lower = line.lower()
    return any(ind.lower() in lower for ind in FIXTURE_INDICATORS)


def scan_file(path: Path) -> list[str]:
    """Return list of violation messages (without leaking content)."""
    violations = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    for i, line in enumerate(text.splitlines(), 1):
        for pattern in PATTERNS:
            if pattern.search(line):
                if is_fixture_context(line):
                    continue
                violations.append(
                    f"{path.relative_to(ROOT)}:{i} - potential secret pattern: {pattern.pattern[:60]}..."
                )
    return violations


def should_skip(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    return any(p in SKIP_DIRS for p in parts)


def main() -> int:
    all_violations = []

    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if should_skip(p):
            continue
        if p.suffix not in SCAN_EXTENSIONS and p.suffix != "":
            continue
        violations = scan_file(p)
        all_violations.extend(violations)

    if all_violations:
        print("FAIL: Potential secrets found in repository:")
        for v in all_violations:
            print(f"  {v}")
        return 1

    print("PASS: No private keys or tokens found in active tree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
