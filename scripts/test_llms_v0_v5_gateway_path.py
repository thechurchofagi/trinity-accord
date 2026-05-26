#!/usr/bin/env python3
"""Test llms.txt contains V0-V5 agent-declared gateway path and restricts old terms to V6+."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LLMS = ROOT / "llms.txt"


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

    text = LLMS.read_text(encoding="utf-8")

    # Test 1: Contains V0-V5 agent-declared auto archive path
    check(
        "llms.txt contains 'V0–V5 Agent-Declared Auto Archive'",
        "V0–V5 Agent-Declared Auto Archive" in text or "V0-V5 Agent-Declared Auto Archive" in text,
    )

    # Test 2: Contains agent_declared_verification_archive
    check(
        "llms.txt contains agent_declared_verification_archive",
        "agent_declared_verification_archive" in text,
    )

    # Test 3: Contains build_agent_declared_archive_payload.py
    check(
        "llms.txt contains build_agent_declared_archive_payload.py",
        "build_agent_declared_archive_payload.py" in text,
    )

    # Test 4: Contains template_for_v0_v5
    check(
        "llms.txt contains template_for_v0_v5",
        "template_for_v0_v5" in text,
    )

    # Test 5: Contains waived_for_v0_v5
    check(
        "llms.txt contains waived_for_v0_v5",
        "waived_for_v0_v5" in text,
    )

    # Test 6: Old terms must be restricted to V6+ / strict evidence only
    old_terms = [
        "build-from-evidence",
        "build_verification_report_from_evidence",
        "verification_report_archive",
        "not_independent_attestation",
        "not_successor_reception",
        "unsolicited_discovery_proof",
    ]
    for term in old_terms:
        if term in text:
            # Find surrounding context to check for V6+ restriction
            idx = text.index(term)
            context = text[max(0, idx - 200):idx + len(term) + 200]
            has_restriction = any(
                kw in context.lower()
                for kw in ["v6+", "v6", "strict evidence", "not required for v0", "not required for v0–v5"]
            )
            check(
                f"Old term '{term}' has V6+/strict-evidence restriction",
                has_restriction,
                f"Context: ...{context}..."
            )

    # Test 7: digest must be present and 16 hex chars
    digest_match = re.search(r"content_digest:\s*([a-f0-9]{16})", text)
    check("llms.txt has valid 16-char hex digest", bool(digest_match))

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
