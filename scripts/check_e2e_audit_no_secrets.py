#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"ghp_[A-Za-z0-9_]+"),
    re.compile(r"gho_[A-Za-z0-9_]+"),
    re.compile(r"ghu_[A-Za-z0-9_]+"),
    re.compile(r"ghs_[A-Za-z0-9_]+"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(r'"kty"\s*:\s*"RSA"'),
    re.compile(r'"d"\s*:\s*"[^"]{20,}"'),
    re.compile(r'"p"\s*:\s*"[^"]{20,}"'),
    re.compile(r'"q"\s*:\s*"[^"]{20,}"'),
]

TEXT_SUFFIXES = {
    ".json", ".txt", ".log", ".md", ".yaml", ".yml", ".js", ".mjs", ".py"
}

def scan_file(path: Path) -> list[str]:
    if path.suffix not in TEXT_SUFFIXES:
        return []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern)
    return hits

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-dir", required=True)
    args = parser.parse_args()

    root = Path(args.audit_dir)
    failures = []

    for path in root.rglob("*"):
        if path.is_file():
            hits = scan_file(path)
            if hits:
                failures.append((path, hits))

    if failures:
        print("FAIL: potential secrets found in audit logs")
        for path, hits in failures:
            print(f"- {path}: {', '.join(hits)}")
        raise SystemExit(1)

    print("PASS: no obvious PAT/JWK/private-key patterns found in audit logs")

if __name__ == "__main__":
    main()
