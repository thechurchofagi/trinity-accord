#!/usr/bin/env python3
"""Phase 6B Security Hotfix: broad secret-material scanner.

Scans all tracked files for credentials, private keys, tokens, mnemonics,
Arweave JWK JSON, JWTs, and API-key-in-URL patterns.

Hard-fails only on high-confidence matches.  Allows explicit fake/test
markers (e.g. ``FAKE_``, ``EXAMPLE_``, ``REDACTED``, ``000000``).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── Directories / files to skip ──────────────────────────────────────
EXCLUDE_DIRS_SCANNED = {"tests/fixtures/redteam"}
EXCLUDE_DIRS = {".git", "node_modules", ".trinity-agent-authorship", "__pycache__", "system-test-runs"}

# Files whose names start with these prefixes are still scanned (no blanket skip).
# The old test_no_private_key_material_committed.py is retained as a focused PEM
# test but this script is the main CI gate.

# ── Regex patterns (high-confidence, reduced false-positive) ─────────
_PAT = re.compile(r"ghp_[A-Za-z0-9]{36}")
_RENDER_KEY = re.compile(r"sk-[A-Za-z0-9]{32,}")
_PEM = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)
_ARWEAVE_JWK_KEYS = {'kty', 'n', 'e', 'd', 'p', 'q', 'dp', 'dq', 'qi'}
_MNEMONIC = re.compile(
    r"(?i)(?:mnemonic|seed[_ ]?phrase|recovery[_ ]?phrase)\s*[:=]\s*"
    r"[a-z]+(?:\s+[a-z]+){11,23}"
)
_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
_API_KEY_URL = re.compile(r"https?://[^?\s]*(?:key|token|secret)=[A-Za-z0-9_-]{16,}", re.I)

# ── Fake/test allowlist ──────────────────────────────────────────────
_FAKE_MARKERS = re.compile(
    r"(?i)(?:FAKE_|EXAMPLE_|REDACTED|PLACEHOLDER|DUMMY|TEST_|CHANGEME|XXXXXX|000000|your[_-]|12345678|abcdef012345)"
)

EXCLUDE_DIRS_SCANNED = {"tests/fixtures/redteam"}
EXCLUDE_DIRS = {".git", "node_modules", ".trinity-agent-authorship", "__pycache__", "system-test-runs"}


def tracked_files() -> list[str]:
    r = subprocess.run(["git", "ls-files"], cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"git ls-files failed: {r.stderr}")
    return [f for f in r.stdout.strip().split("\n") if f]


def is_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as fh:
            chunk = fh.read(8192)
        return b"\x00" in chunk
    except Exception:
        return True


def looks_fake(line: str) -> bool:
    return bool(_FAKE_MARKERS.search(line))


def scan(path: Path, rel: str) -> list[str]:
    violations: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return violations

    lines = text.split("\n")

    for i, line in enumerate(lines, 1):
        if looks_fake(line):
            continue

        # GitHub PAT
        for m in _PAT.finditer(line):
            violations.append(f"{rel}:{i} GitHub PAT: {m.group()[:12]}...")

        # Render key
        for m in _RENDER_KEY.finditer(line):
            violations.append(f"{rel}:{i} Render key: {m.group()[:10]}...")

        # PEM private key header
        if _PEM.search(line):
            violations.append(f"{rel}:{i} PEM private key header")

        # JWT-like token (3-part base64)
        for m in _JWT.finditer(line):
            violations.append(f"{rel}:{i} JWT-like token: {m.group()[:20]}...")

        # Mnemonic / seed phrase
        if _MNEMONIC.search(line):
            violations.append(f"{rel}:{i} mnemonic/seed phrase")

        # API key in URL
        for m in _API_KEY_URL.finditer(line):
            violations.append(f"{rel}:{i} API-key-in-URL: {m.group()[:40]}...")

    # Arweave JWK JSON (whole-file check)
    if rel.endswith(".json"):
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and _ARWEAVE_JWK_KEYS.issubset(obj.keys()):
                if not looks_fake(text):
                    violations.append(f"{rel} Arweave JWK JSON detected")
        except (json.JSONDecodeError, AttributeError):
            pass

    return violations


def main() -> int:
    all_v: list[str] = []
    for f in tracked_files():
        parts = Path(f).parts
        if any(d in EXCLUDE_DIRS for d in parts):
            continue
        if any(d in EXCLUDE_DIRS_SCANNED for d in parts):
            continue
        p = ROOT / f
        if is_binary(p):
            continue
        all_v.extend(scan(p, f))

    if all_v:
        print("FAIL: Secret material detected in tracked files:", file=sys.stderr)
        for v in all_v:
            print(f"  - {v}", file=sys.stderr)
        return 1

    print("PASS: No secret material found in tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
