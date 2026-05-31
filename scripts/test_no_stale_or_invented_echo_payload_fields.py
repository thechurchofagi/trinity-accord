#!/usr/bin/env python3
"""Forbid stale or invented Gateway payload fields and echo_type values."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = {
    "E1_read_oriented_echo",
    "read_oriented_echo",
    "agentreadbacksha256",
    "agent_readback_hash",
    "readback_sha256",
    "readback_hash_sha256",
    "agent_readback_digest",
}

ALLOWLIST = {
    # Safety docs (v30.6 first-contact surfaces)
    "scripts/test_no_stale_or_invented_echo_payload_fields.py",
    "scripts/test_first_contact_forces_copy_paste_or_route_selector.py",
    "scripts/test_runtime_and_route_selector_forbid_invented_values.py",
    "api/gateway-error-diagnostics.v1.json",
    "api/gateway-runtime-contract.v1.json",
    "api/agent-first-contact.json",
    "api/route-selector.v1.json",
    "external-agent-copy-paste-examples.md",
    "external-agent-quickstart.md",
    "agent-start.md",
    "llms.txt",
    "ai.txt",
    "index.md",
    "CHANGELOG.md",
}

# Directories whose contents are test fixtures, echo records, or build scripts
# that legitimately reference forbidden tokens for validation/data purposes.
ALLOW_PREFIXES = (
    "scripts/",
    "fixtures/",
    "tests/",
    "echoes/",
    "examples/",
    "api/",
    "verification-reports/",
    "repair-spec.md",
    "gateway-workflows.md",
    "agent-submit.md",
    "echo-payload-real.json",
    "runbook.md",
)

SCAN_SUFFIXES = {
    ".py",
    ".js",
    ".mjs",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
}

def main() -> int:
    errors: list[str] = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(ROOT).as_posix()

        if rel.startswith(".git/"):
            continue
        if rel.startswith("node_modules/"):
            continue
        if rel.startswith(".venv/"):
            continue
        if rel.startswith("vendor/"):
            continue
        if path.suffix not in SCAN_SUFFIXES:
            continue
        if rel in ALLOWLIST:
            continue
        if any(rel.startswith(prefix) for prefix in ALLOW_PREFIXES):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for token in FORBIDDEN:
            if token in text:
                errors.append(f"{rel}: forbidden invented/stale token {token}")

    if errors:
        print("FAIL: stale or invented echo payload fields found:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: no stale or invented echo payload fields outside allowlisted safety docs")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
