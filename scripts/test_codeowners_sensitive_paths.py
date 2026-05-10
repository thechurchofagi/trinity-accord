#!/usr/bin/env python3
"""
Test: CODEOWNERS covers sensitive paths.
TA-REDTEAM-2026-004 — GOV-001 regression test.

Ensures CODEOWNERS exists and covers all critical paths for
formal attestation, workflows, homepage, and core scripts.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main():
    # Find CODEOWNERS
    candidates = [ROOT / "CODEOWNERS", ROOT / ".github" / "CODEOWNERS"]
    path = next((p for p in candidates if p.exists()), None)

    if path is None:
        fail("missing CODEOWNERS (checked root and .github/)")

    text = path.read_text(encoding="utf-8")

    # Required sensitive paths
    required_patterns = [
        ".github/workflows/",
        "api/independent-attestation-index.json",
        "api/independent-attestation-record-schema.v1.json",
        "scripts/validate_independent_attestation_index.py",
        "scripts/generate_public_home_status.py",
        "scripts/claim_gate.py",
        "scripts/build_verification_report_from_evidence.py",
        "scripts/validate_agent_submission.py",
        "scripts/archive_echo_issue.py",
        "scripts/triage_echo_issue.py",
        "index.md",
    ]

    missing = [p for p in required_patterns if p not in text]
    if missing:
        print("FAIL: CODEOWNERS missing sensitive paths:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)

    # Every non-comment non-empty line must have an owner
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 2:
            fail(f"CODEOWNERS line {lineno} has no owner: {line}")

    print("CODEOWNERS_SENSITIVE_PATHS_OK")


if __name__ == "__main__":
    main()
