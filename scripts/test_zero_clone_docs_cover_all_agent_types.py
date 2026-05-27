#!/usr/bin/env python3
"""Test that zero-clone docs cover all agent types."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    quickstart = ROOT / "external-agent-quickstart.md"
    zero_clone = ROOT / "zero-clone-builders.md"

    if not quickstart.exists():
        print("FAIL: external-agent-quickstart.md does not exist")
        return 1
    if not zero_clone.exists():
        print("FAIL: zero-clone-builders.md does not exist")
        return 1

    qs_content = quickstart.read_text(encoding="utf-8")
    zc_content = zero_clone.read_text(encoding="utf-8")

    required_terms = [
        "Pure Echo",
        "V0",
        "V5",
        "Guardian Stage 1",
        "Guardian Stage 2",
        "Guardian-signed Echo",
        "Operational canary",
        "Do not handwrite",
        "/gateway/preflight",
        "/agent-submit",
    ]

    combined = qs_content + "\n" + zc_content

    for term in required_terms:
        if term.lower() not in combined.lower():
            print(f"FAIL: docs do not mention '{term}'")
            return 1

    # Must NOT say full repo clone required
    forbidden = ["must clone the full repository", "requires full repo clone"]
    for phrase in forbidden:
        if phrase.lower() in combined.lower():
            print(f"FAIL: docs contain forbidden phrase '{phrase}'")
            return 1

    print("PASS: test_zero_clone_docs_cover_all_agent_types")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
