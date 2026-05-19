#!/usr/bin/env python3
"""Ensure no private key material is committed to the repository.

Hard-fails if committed files contain actual PEM private key headers or
forbidden payload fields. Allows ordinary prose like "private key" in docs.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Patterns that indicate actual private key material (not just prose)
FORBIDDEN_PATTERNS = [
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
    "-----BEGIN EC PRIVATE KEY-----",
    "-----BEGIN RSA PRIVATE KEY-----",
    "-----BEGIN DSA PRIVATE KEY-----",
]

# Payload field names that must never appear with actual key material
FORBIDDEN_PAYLOAD_FIELDS = [
    '"private_key_pem"',
    '"mnemonic"',
    '"seed_phrase"',
    '"recovery_phrase"',
]

# Directories to exclude from scan
EXCLUDE_DIRS = {".git", "node_modules", ".trinity-agent-authorship"}

# File patterns to exclude (test files may contain legitimate test key fixtures)
EXCLUDE_PATTERNS = [
    "test_authorship_",
    "test_no_private_key",
    "validate_gateway_payload",
    "test_gateway_",
    "test_agent_declared_",
    "test_build_",
    "test_echo_authorship",
    "test_agent_verification_receipt_authorship",
]


def get_tracked_files():
    """Get list of tracked files in the repo."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {result.stderr}")
    return [f for f in result.stdout.strip().split("\n") if f]


def should_skip(path_str):
    """Check if file is in an excluded directory or matches exclude patterns."""
    parts = Path(path_str).parts
    if any(d in EXCLUDE_DIRS for d in parts):
        return True
    basename = Path(path_str).name
    return any(basename.startswith(p) for p in EXCLUDE_PATTERNS)


def scan_file(filepath):
    """Scan a file for forbidden patterns. Returns list of violations."""
    violations = []
    try:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return violations

    for pattern in FORBIDDEN_PATTERNS:
        if pattern in content:
            violations.append(f"Contains PEM private key header: {pattern}")

    for field in FORBIDDEN_PAYLOAD_FIELDS:
        if field in content:
            # Check if it's paired with actual key material (not just a field name in schema)
            # Only flag if the field appears outside of a JSON schema "properties" context
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if field in line and "properties" not in line and "forbidden" not in line.lower():
                    # Check if surrounding context looks like actual key material
                    context = "\n".join(lines[max(0, i-2):i+3])
                    if any(p in context for p in FORBIDDEN_PATTERNS):
                        violations.append(f"Line {i+1}: {field} near PEM material")
                        break

    return violations


def main():
    files = get_tracked_files()
    all_violations = []

    for f in files:
        if should_skip(f):
            continue
        violations = scan_file(ROOT / f)
        for v in violations:
            all_violations.append(f"{f}: {v}")

    if all_violations:
        print("FAIL: Private key material found in tracked files:", file=sys.stderr)
        for v in all_violations:
            print(f"  - {v}", file=sys.stderr)
        sys.exit(1)

    print("PASS: No private key material found in tracked files.")


if __name__ == "__main__":
    main()
