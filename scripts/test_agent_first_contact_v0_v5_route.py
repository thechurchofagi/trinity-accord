#!/usr/bin/env python3
"""Test agent-first-contact JSON and Markdown keep V0-V5 route guidance in sync."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRST_CONTACT = ROOT / "api" / "agent-first-contact.json"
FIRST_CONTACT_MD = ROOT / "agent-first-contact.md"


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

    data = json.loads(FIRST_CONTACT.read_text(encoding="utf-8"))
    md = FIRST_CONTACT_MD.read_text(encoding="utf-8")

    choose_one = data.get("choose_one", [])
    intents = [c.get("intent", "") for c in choose_one]

    # Test 1: choose_one contains V0-V5 agent-declared verify route
    check(
        "choose_one contains 'verify_v0_v5_agent_declared' intent",
        "verify_v0_v5_agent_declared" in intents,
    )

    # Test 2: V0-V5 route contains required keywords
    v0_v5_route = next((c for c in choose_one if c.get("intent") == "verify_v0_v5_agent_declared"), None)
    if v0_v5_route:
        route_text = json.dumps(v0_v5_route)
        for kw in ["agent_declared_verification_archive", "waived_for_v0_v5", "template_for_v0_v5", "verification_oath_readback"]:
            check(
                f"V0-V5 JSON route contains '{kw}'",
                kw in route_text,
            )

        # Test 3: V0-V5 route not_required contains expected items
        not_req = v0_v5_route.get("not_required", [])
        for item in ["evidence_input", "build_from_evidence", "unsolicited_discovery_proof", "not_independent_attestation", "not_successor_reception"]:
            check(
                f"V0-V5 route not_required contains '{item}'",
                item in not_req,
            )
    else:
        check("V0-V5 route exists", False, "verify_v0_v5_agent_declared not found")

    # Test 4: Old evidence pipeline is restricted to V6+
    v6_route = next((c for c in choose_one if c.get("intent") == "verify_v6_plus_strict_evidence"), None)
    check(
        "choose_one contains 'verify_v6_plus_strict_evidence' intent",
        v6_route is not None,
    )
    if v6_route:
        v6_text = json.dumps(v6_route)
        check(
            "V6+ route contains 'evidence_input' pipeline",
            "evidence_input" in v6_text,
        )
        check(
            "V6+ route contains 'strict_claim_gate'",
            "strict_claim_gate" in v6_text,
        )

    # Test 5: Human-readable first-contact page mirrors the V0-V5 route.
    for kw in [
        "build_agent_declared_archive_payload.py",
        "agent_declared_verification_archive",
        "waived_for_v0_v5",
        "template_for_v0_v5",
        "gateway/preflight",
        "agent-submit",
    ]:
        check(f"Markdown V0-V5 route contains '{kw}'", kw in md)

    for forbidden in [
        "python3 scripts/agent_verify_ceremony.py --mode v1",
        "For V2/V3 minimal modes, provide required evidence flags",
    ]:
        check(
            f"Markdown no longer routes V0-V5 through stale strict-evidence text: {forbidden}",
            forbidden not in md,
        )

    # Ensure strict evidence wording is scoped to V6/V7/V8.
    strict_heading = "### 6. VERIFY — V6/V7/V8 strict evidence"
    strict_idx = md.find(strict_heading)
    evidence_idx = md.find("Evidence Input")
    check(
        "Markdown Evidence Input appears only after V6/V7/V8 strict heading",
        strict_idx != -1 and evidence_idx != -1 and evidence_idx > strict_idx,
    )

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
