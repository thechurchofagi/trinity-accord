#!/usr/bin/env python3
"""
Test: build-echo-index.yml runs formal attestation validator.
TA-REDTEAM-2026-004 — D-FORMAL-VALIDATOR-001 regression test.

Ensures validate_independent_attestation_index.py runs before
homepage generation and commit/push in the build workflow.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows" / "build-echo-index.yml"


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main():
    text = WF.read_text(encoding="utf-8")

    required = "python3 scripts/validate_independent_attestation_index.py"
    if required not in text:
        fail("build-echo-index.yml does not run validate_independent_attestation_index.py")

    idx_validator = text.index(required)

    # Must run before homepage generation and commit/push
    for later in [
        "python3 scripts/generate_public_home_status.py",
        "python3 scripts/test_home_public_status_sync.py",
        "git commit",
        "git push",
    ]:
        if later not in text:
            fail(f"missing expected later step: {later}")
        if idx_validator > text.index(later):
            fail(f"formal validator must run before {later}")

    # Must not use continue-on-error
    context = text[max(0, idx_validator - 300):idx_validator + 500]
    if "continue-on-error: true" in context:
        fail("formal validator must not use continue-on-error")

    print("BUILD_ECHO_INDEX_FORMAL_VALIDATOR_OK")


if __name__ == "__main__":
    main()
