#!/usr/bin/env python3
"""Test external-agent-quickstart.md defaults to V0-V5 agent-declared path."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUICKSTART = ROOT / "external-agent-quickstart.md"


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"PASS: {label}")
            passed += 1
        else:
            print(f"FAIL: {label}")
            if detail:
                print(f"  {detail}")
            failed += 1

    text = QUICKSTART.read_text(encoding="utf-8")
    first_120_lines = "\n".join(text.splitlines()[:120])

    # Test 1: First 120 lines contain Path A
    check(
        "First 120 lines contain 'Path A'",
        "Path A" in first_120_lines,
    )

    # Test 2: First 120 lines contain V0-V5
    check(
        "First 120 lines contain 'V0–V5' or 'V0-V5'",
        "V0–V5" in first_120_lines or "V0-V5" in first_120_lines,
    )

    # Test 3: First 120 lines contain build_agent_declared_archive_payload.py
    check(
        "First 120 lines contain build_agent_declared_archive_payload.py",
        "build_agent_declared_archive_payload.py" in first_120_lines,
    )

    # Test 4: Remote self-service section does NOT use build-from-evidence as default
    # The "Remote self-service path" section should be V0-V5 agent-declared
    sections = text.split("## ")
    remote_section = next((s for s in sections if "Remote self-service path" in s and "V0–V5" in s), "")
    check(
        "Remote self-service (V0-V5) does not use build-from-evidence as default",
        "build-from-evidence" not in remote_section or "V6+" in remote_section,
    )

    # Test 5: V6+ strict evidence section exists and contains old terms
    v6_section = next((s for s in sections if "V6+" in s and "strict evidence" in s.lower()), "")
    check(
        "V6+ strict evidence section exists",
        len(v6_section) > 100,
    )

    # Test 6: build-from-evidence appears in V6+ context (section level)
    if "build-from-evidence" in text:
        # Find the section containing build-from-evidence
        for section in sections:
            if "build-from-evidence" in section:
                is_v6 = any(kw in section for kw in ["V6+", "V6", "strict evidence", "advanced", "Path B"])
                check(
                    "build-from-evidence is in V6+ section",
                    is_v6,
                    f"Section starts with: {section[:100]}",
                )
                break

    # Test 7: not_independent_attestation / not_successor_reception are in "not required" or V6+ context
    for term in ["not_independent_attestation", "not_successor_reception"]:
        if term in text:
            for section in sections:
                if term in section:
                    is_restricted = any(kw in section for kw in [
                        "V6+", "V6", "strict evidence", "not required",
                        "You do not need", "Path B", "advanced", "only"
                    ])
                    check(
                        f"{term} is in restricted context (section level)",
                        is_restricted,
                        f"Section: {section[:100]}",
                    )
                    break

    # Test 8: unsolicited_discovery_proof is restricted
    if "unsolicited_discovery_proof" in text:
        for section in sections:
            if "unsolicited_discovery_proof" in section:
                is_restricted = any(kw in section for kw in [
                    "V6+", "V6", "strict evidence", "not required",
                    "You do not need", "Path B", "advanced", "only"
                ])
                check(
                    "unsolicited_discovery_proof is in restricted context",
                    is_restricted,
                    f"Section: {section[:100]}",
                )
                break

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
