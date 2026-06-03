#!/usr/bin/env python3
"""Phase 6B Security Hotfix: broad secret-material scanner.

Scans all tracked files for credentials, private keys, tokens, mnemonics,
Arweave JWK JSON, JWTs, and API-key-in-URL patterns.

High-confidence matches only.  Allows explicit fake/test markers.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDE_DIRS = {".git", "node_modules", ".trinity-agent-authorship", "__pycache__", "system-test-runs"}

# Skip test/validation files that intentionally contain PEM patterns or secrets
SKIP_PREFIXES = (
    "test_authorship_", "test_no_private_key", "validate_gateway_payload",
    "test_gateway_", "test_agent_declared_", "test_build_", "test_echo_authorship",
    "test_agent_verification_receipt_authorship",
)

# Directories that contain intentional test fixtures
FIXTURE_DIRS = {"tests/fixtures", "tests/fixtures/redteam", "legacy/gateway-v1/scripts"}

_PAT = re.compile(r"ghp_[A-Za-z0-9]{36}")
_GITHUB_PAT = re.compile(r"github_pat_[A-Za-z0-9_]{20,}")
_RND = re.compile(r"rnd_[A-Za-z0-9_]{16,}")
_RENDER_KEY = re.compile(r"sk-[A-Za-z0-9]{32,}")
_PEM_BLOCK = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----\n"
    r"[A-Za-z0-9+/=\n]{40,}\n"
    r"-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)
_ARWEAVE_JWK_KEYS = {"kty", "n", "e", "d", "p", "q", "dp", "dq", "qi"}
_MNEMONIC = re.compile(
    r"(?i)(?:mnemonic|seed[_ ]?phrase|recovery[_ ]?phrase)\s*[:=]\s*"
    r"[a-z]+(?:\s+[a-z]+){11,23}"
)
_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
_API_KEY_URL = re.compile(r"https?://[^?\s]*(?:key|token|secret)=[A-Za-z0-9_-]{16,}", re.I)

_FAKE_MARKERS = re.compile(
    r"(?i)(?:FAKE_|EXAMPLE_|REDACTED|PLACEHOLDER|DUMMY|TEST_|CHANGEME|XXXXXX|000000|your[_-]|12345678)"
)


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


def looks_fake(text: str) -> bool:
    return bool(_FAKE_MARKERS.search(text))


def _in_fixture_dir(rel: str) -> bool:
    """Check if rel is under any FIXTURE_DIRS prefix."""
    for prefix in FIXTURE_DIRS:
        if rel.startswith(prefix + "/") or rel == prefix:
            return True
    return False


def scan(path: Path, rel: str) -> tuple[list[str], list[str]]:
    """Return (hard_fails, warnings)."""
    hard: list[str] = []
    warn: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return hard, warn

    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if looks_fake(line):
            continue
        for m in _PAT.finditer(line):
            warn.append(f"{rel}:{i} GitHub PAT: {m.group()[:12]}...")
        for m in _GITHUB_PAT.finditer(line):
            warn.append(f"{rel}:{i} GitHub PAT (fine-grained): {m.group()[:20]}...")
        for m in _RND.finditer(line):
            warn.append(f"{rel}:{i} rnd_ token: {m.group()[:12]}...")
        for m in _RENDER_KEY.finditer(line):
            warn.append(f"{rel}:{i} Render key: {m.group()[:10]}...")
        if _MNEMONIC.search(line):
            warn.append(f"{rel}:{i} mnemonic/seed phrase")
        for m in _JWT.finditer(line):
            warn.append(f"{rel}:{i} JWT-like token: {m.group()[:20]}...")
        for m in _API_KEY_URL.finditer(line):
            warn.append(f"{rel}:{i} API-key-in-URL: {m.group()[:40]}...")

    # Multi-line PEM block (actual key material, not just a header string reference)
    pem_match = _PEM_BLOCK.search(text)
    if pem_match:
        start = max(0, pem_match.start() - 200)
        end = min(len(text), pem_match.end() + 200)
        context = text[start:end]
        if not looks_fake(context):
            warn.append(f"{rel} PEM private key block detected")

    # Arweave JWK JSON — always hard fail (real key material is catastrophic)
    if rel.endswith(".json"):
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and _ARWEAVE_JWK_KEYS.issubset(obj.keys()):
                if not looks_fake(text):
                    hard.append(f"{rel} Arweave JWK JSON detected")
        except (json.JSONDecodeError, AttributeError):
            pass

    return hard, warn


def main() -> int:
    all_hard: list[str] = []
    all_warn: list[str] = []
    for f in tracked_files():
        parts = Path(f).parts
        if any(d in EXCLUDE_DIRS for d in parts):
            continue
        # Skip fixture directories (prefix match)
        if _in_fixture_dir(f):
            continue
        # Skip test files that intentionally contain secret patterns
        basename = Path(f).name
        if any(basename.startswith(p) for p in SKIP_PREFIXES):
            continue
        p = ROOT / f
        if is_binary(p):
            continue
        h, w = scan(p, f)
        all_hard.extend(h)
        all_warn.extend(w)

    # Print warnings (non-blocking)
    if all_warn:
        print("WARNING: Possible secret material detected (review recommended):", file=sys.stderr)
        for v in all_warn:
            print(f"  ⚠ {v}", file=sys.stderr)

    # Hard fails block CI
    if all_hard:
        print("FAIL: Hard secret material violations:", file=sys.stderr)
        for v in all_hard:
            print(f"  ✘ {v}", file=sys.stderr)
        return 1

    if all_warn:
        print("PASS with warnings ({} warning(s)).".format(len(all_warn)))
        return 0

    print("PASS: No secret material found in tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
