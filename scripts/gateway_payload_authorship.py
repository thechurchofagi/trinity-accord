#!/usr/bin/env python3
"""Gateway payload authorship proof utilities.

Provides authorship proof closure verification for zero-clone builder bundles.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTACH_SCRIPT = ROOT / "scripts" / "attach_agent_authorship_proof.mjs"

AUTHORSHIP_CLOSURE_FILES = [
    "scripts/generate_agent_authorship_keypair.mjs",
    "scripts/attach_agent_authorship_proof.mjs",
    "scripts/build_agent_authorship_message.py",
    "scripts/agent_authorship_common.py",
]


def assert_authorship_closure_present():
    """Verify all authorship proof closure files exist.

    Raises SystemExit if any required file is missing.
    """
    missing = []
    for rel in AUTHORSHIP_CLOSURE_FILES:
        if not (ROOT / rel).exists():
            missing.append(rel)

    if missing:
        print(f"FAIL: authorship proof closure incomplete. Missing: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    assert_authorship_closure_present()
    print("PASS: authorship proof closure is complete")
