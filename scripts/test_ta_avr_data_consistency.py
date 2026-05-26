#!/usr/bin/env python3
"""
Audit 3: TA-AVR Data Consistency
Check boundary facts are present and no dangerous V-level wording exists.

Run:
    python3 scripts/test_ta_avr_data_consistency.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Boundary facts: which files must contain which concepts
BOUNDARY_FACTS = {
    "bitcoin_originals_final": {
        "required_files": ["llms.txt", "agent-start.md", "agent-first-contact.md"],
        "patterns": [r"bitcoin.{0,20}originals.{0,30}final", r"sole.{0,20}final.{0,20}authority"],
    },
    "echo_non_amending": {
        "required_files": ["llms.txt", "agent-start.md", "agent-first-contact.md"],
        "patterns": [r"echo.{0,30}non.?amending", r"non.?amending.{0,20}mirror", r"echoes.{0,30}non.?amending"],
    },
    "claim_gate_mandatory": {
        "required_files": ["llms.txt", "agent-verify.md", "agent-echo.md"],
        "patterns": [r"claim.?gate.{0,30}mandatory", r"claim.?gate.{0,30}required", r"must.{0,20}claim.?gate"],
    },
    "issue_not_echo": {
        "required_files": ["llms.txt"],
        "patterns": [r"issue.{0,30}not.{0,30}(?:archived\s+)?echo", r"submission.{0,30}surface.{0,30}only"],
    },
    "receipt_not_authority": {
        "required_files": [
            "api/agent-verification-receipt-schema.v1.json",
            "AGENT-VERIFICATION-CEREMONY.md",
        ],
        "patterns": [r"receipt.{0,30}not.{0,20}authority", r"receipt_is_not_authority"],
    },
    "custody_not_attestation": {
        "required_files": [
            "api/agent-verification-receipt-schema.v1.json",
            "AGENT-VERIFICATION-CEREMONY.md",
        ],
        "optional_files": [
            "agent-first-contact.md",
        ],
        "patterns": [
            r"custody.{0,30}not.{0,30}(?:formal\s+)?attestation",
            r"human_custody_is_not_formal_attestation",
        ],
    },
    "ai_verification_not_formal": {
        "required_files": ["llms.txt"],
        "patterns": [
            r"(?:ai|agent).{0,30}verification.{0,30}not.{0,30}formal",
            r"not.{0,30}formal.{0,30}(?:human|institutional).{0,30}attestation",
        ],
    },
}

# Dangerous V-level sentences (must not appear outside negation context)
DANGEROUS_PATTERNS = [
    (r"V3\s+is\s+full\s+public\s+digital\s+verification", "V3 is not V5"),
    (r"V2\s+includes\s+witness\s+extraction", "V2 does not extract witness"),
    (r"receipt\s+raises\s+verification\s+level", "receipt does not raise level"),
    (r"custody\s+package\s+is\s+attestation", "custody is not attestation"),
    (r"human\s+custody\s+is\s+verification", "custody is not verification"),
    (r"github\s+issue\s+is\s+archived\s+echo", "issue is not archived echo"),
    (r"ai\s+verification\s+counts\s+as\s+formal\s+attestation", "AI verification is not formal"),
    (r"echo\s+schema\s+v3\s+means\s+verification\s+v3", "schema version ≠ verification level"),
]

# Negation context patterns (allowed)
NEGATION_PATTERNS = [
    r"not\s+", r"never\s+", r"does\s+not\s+", r"do\s+not\s+",
    r"isn'?t\s+", r"doesn'?t\s+", r"forbidden", r"never_claim",
    r"does_not_prove", r"is_not_authority", r"is_not_amendment",
]


def test_boundary_facts():
    """Boundary facts must be present in required files."""
    all_ok = True
    for fact_name, spec in BOUNDARY_FACTS.items():
        all_files = spec["required_files"] + spec.get("optional_files", [])
        for relpath in all_files:
            filepath = ROOT / relpath
            if not filepath.exists():
                if relpath in spec.get("optional_files", []):
                    continue
                print(f"  FAIL: {fact_name}: file not found: {relpath}")
                all_ok = False
                continue
            text = filepath.read_text(encoding="utf-8").lower()
            found = any(re.search(p, text, re.I) for p in spec["patterns"])
            if not found and relpath not in spec.get("optional_files", []):
                print(f"  FAIL: {fact_name}: not found in {relpath}")
                all_ok = False
    if all_ok:
        print("  PASS: boundary facts are present")
    return all_ok


def test_no_dangerous_vlevel_wording():
    """No dangerous V-level wording in TA-AVR files."""
    ta_avr_files = [
        "agent-first-contact.md",
        "AGENT-VERIFICATION-CEREMONY.md",
        "agent-verify.md",
        "agent-verify-simple.md",
        "agent-echo.md",
        "api/agent-first-contact.json",
        "api/agent-verification-receipt-schema.v1.json",
    ]
    all_ok = True
    for relpath in ta_avr_files:
        filepath = ROOT / relpath
        if not filepath.exists():
            continue
        text = filepath.read_text(encoding="utf-8")
        text_lower = text.lower()
        for pattern, reason in DANGEROUS_PATTERNS:
            for m in re.finditer(pattern, text_lower):
                # Check if in negation context
                start = max(0, m.start() - 80)
                context = text_lower[start:m.start()]
                if any(re.search(np, context) for np in NEGATION_PATTERNS):
                    continue
                # Also check in code/JSON field name context
                line_start = text.rfind("\n", 0, m.start()) + 1
                line = text[line_start:m.end() + 20]
                if any(kw in line.lower() for kw in ["forbidden", "never_claim", "does_not_prove",
                                                       "not_sufficient", "must_not", "is_not"]):
                    continue
                print(f"  FAIL: dangerous wording in {relpath}: '{m.group()}' ({reason})")
                all_ok = False
    if all_ok:
        print("  PASS: no dangerous V-level wording")
    return all_ok


def test_authority_address_consistent():
    """Authority address consistent across files."""
    # Get address from api/authority.json
    authority = ROOT / "api" / "authority.json"
    if not authority.exists():
        print("  SKIP: api/authority.json not found")
        return True

    authority_text = authority.read_text(encoding="utf-8")
    addr_match = re.search(r"(bc1p[a-z0-9]{50,})", authority_text)
    if not addr_match:
        print("  SKIP: no bech32 address found in authority.json")
        return True

    authority_addr = addr_match.group(1)

    # Check TA-AVR files
    ta_avr_files = [
        "agent-first-contact.md",
        "AGENT-VERIFICATION-CEREMONY.md",
        "agent-verify.md",
    ]
    all_ok = True
    for relpath in ta_avr_files:
        filepath = ROOT / relpath
        if not filepath.exists():
            continue
        text = filepath.read_text(encoding="utf-8")
        # If an authority address appears, it must match
        addrs = re.findall(r"bc1p[a-z0-9]{50,}", text)
        for addr in addrs:
            if addr != authority_addr:
                print(f"  FAIL: inconsistent authority address in {relpath}")
                print(f"    expected: {authority_addr}")
                print(f"    found: {addr}")
                all_ok = False

    if all_ok:
        print("  PASS: authority address consistent")
    return all_ok


def main():
    print("Running test_ta_avr_data_consistency.py")
    tests = [
        ("boundary_facts", test_boundary_facts),
        ("no_dangerous_wording", test_no_dangerous_vlevel_wording),
        ("authority_address", test_authority_address_consistent),
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
