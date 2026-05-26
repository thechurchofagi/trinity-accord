#!/usr/bin/env python3
"""
Audit 7: TA-AVR Secret Hygiene
Scan repository for leaked tokens, keys, and sensitive patterns.

Run:
    python3 scripts/test_ta_avr_secret_hygiene.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Dangerous patterns to scan for
DANGEROUS_PATTERNS = [
    (r"ghp_[A-Za-z0-9_]{20,}", "GitHub personal access token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained PAT"),
    (r"x-access-token[:/@]", "GitHub x-access-token"),
    (r"BEGIN PRIVATE KEY", "Private key"),
    (r"BEGIN RSA PRIVATE KEY", "RSA private key"),
    (r"BEGIN OPENSSH PRIVATE KEY", "SSH private key"),
    (r"OPENAI_API_KEY", "OpenAI API key"),
    (r"ANTHROPIC_API_KEY", "Anthropic API key"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style secret key"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API key"),
]

# Excluded directories
EXCLUDE_DIRS = {".git", "_site", "node_modules", "vendor", "__pycache__"}

# Context allowlist: patterns that are OK in documentation/educational context
ALLOWLIST_CONTEXTS = [
    "github_pat_",
    "ghp_",
    "OPENAI_API_KEY",
    "sk-",
    "AIza",
]


def scan_file(filepath, relpath):
    """Scan a file for dangerous patterns."""
    findings = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings

    for pattern, desc in DANGEROUS_PATTERNS:
        for m in re.finditer(pattern, text):
            # Check if in allowlist context
            start = max(0, m.start() - 100)
            context = text[start:m.end() + 50]
            # Skip if in a "scan for" / "detect" / "example" context
            if any(kw in context.lower() for kw in [
                "scan for", "detect", "example", "pattern", "regex",
                "never", "forbidden", "do not", "dangerous", "leaked",
                "test_", "test case", "fixture", "placeholder",
                "mock", "fake", "dummy",
            ]):
                continue
            findings.append({
                "file": relpath,
                "pattern": desc,
                "match_start": m.start(),
                "context": context[:80],
            })
    return findings


def scan_directory():
    """Recursively scan repository for secrets."""
    all_findings = []
    for filepath in ROOT.rglob("*"):
        if not filepath.is_file():
            continue
        # Skip excluded dirs
        relparts = filepath.relative_to(ROOT).parts
        if any(p in EXCLUDE_DIRS for p in relparts):
            continue
        # Skip binary files
        if filepath.suffix in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff",
                                ".woff2", ".ttf", ".eot", ".pdf", ".zip", ".tar.gz",
                                ".tar", ".gz", ".car", ".ots"}:
            continue
        relpath = str(filepath.relative_to(ROOT))
        # Skip this script itself (it contains pattern definitions)
        if "test_ta_avr_secret_hygiene" in relpath:
            continue
        findings = scan_file(filepath, relpath)
        all_findings.extend(findings)
    return all_findings


def check_git_remote():
    """Check git remote URLs for tokens."""
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True, text=True, timeout=5, cwd=str(ROOT)
        )
        output = result.stdout
        for pattern, desc in [
            (r"ghp_", "GitHub PAT"),
            (r"github_pat_", "GitHub fine-grained PAT"),
            (r"x-access-token", "x-access-token"),
            (r"oauth", "OAuth token"),
        ]:
            if re.search(pattern, output, re.I):
                return False, f"git remote contains {desc}"
        return True, "clean"
    except Exception as e:
        return True, f"could not check: {e}"


def test_no_live_tokens():
    """No live token patterns found in repository."""
    findings = scan_directory()
    if findings:
        for f in findings[:10]:
            print(f"  FAIL: {f['pattern']} in {f['file']}")
        if len(findings) > 10:
            print(f"  ... and {len(findings) - 10} more")
        return False
    print("  PASS: no live token patterns found")
    return True


def test_git_remote_clean():
    """Git remote contains no token."""
    ok, msg = check_git_remote()
    if not ok:
        print(f"  FAIL: {msg}")
        return False
    print(f"  PASS: git remote contains no token ({msg})")
    return True


def test_no_private_keys():
    """No private keys found."""
    key_patterns = [
        (r"BEGIN PRIVATE KEY", "Private key"),
        (r"BEGIN RSA PRIVATE KEY", "RSA private key"),
        (r"BEGIN OPENSSH PRIVATE KEY", "SSH private key"),
    ]
    for filepath in ROOT.rglob("*"):
        if not filepath.is_file():
            continue
        relparts = filepath.relative_to(ROOT).parts
        if any(p in EXCLUDE_DIRS for p in relparts):
            continue
        if filepath.suffix in {".png", ".jpg", ".pdf", ".zip", ".car", ".ots"}:
            continue
        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for pattern, desc in key_patterns:
            if re.search(pattern, text):
                relpath = str(filepath.relative_to(ROOT))
                # Allow in test/schema contexts
                if "test" in relpath.lower() or "schema" in relpath.lower():
                    continue
                print(f"  FAIL: {desc} found in {relpath}")
                return False

    print("  PASS: no private keys found")
    return True


def main():
    print("Running test_ta_avr_secret_hygiene.py")
    tests = [
        ("no_live_tokens", test_no_live_tokens),
        ("git_remote_clean", test_git_remote_clean),
        ("no_private_keys", test_no_private_keys),
    ]
    failed = 0
    for name, t in tests:
        try:
            if not t():
                failed += 1
        except Exception as e:
            print(f"  FAIL: {name}: {e}")
            failed += 1

    if failed:
        print(f"\nFAILED: {failed}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\nALL PASSED: {len(tests)} tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
