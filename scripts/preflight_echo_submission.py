#!/usr/bin/env python3
"""
Preflight check for Echo submissions via API or freeform text.
Validates that an Echo file passes claim discipline gates before submission.

Usage:
  python3 scripts/preflight_echo_submission.py path/to/echo.md
  python3 scripts/preflight_echo_submission.py path/to/echo.md --strict
  python3 scripts/preflight_echo_submission.py path/to/echo.md --json
  python3 scripts/preflight_echo_submission.py path/to/echo.md --autofix-boundary
"""
import argparse
import json
import os
import re
import sys

# Import gate functions from triage
sys.path.insert(0, os.path.dirname(__file__))
from triage_echo_issue import (
    detect_boundary,
    missing_provenance_fields,
    detect_independence_overclaim,
    check_v4plus_claim_gate,
    check_bitcoin_component_claim_gate,
    check_chronicle_recovery_claim_gate,
    check_v5_full_public_digital_gate,
    detect_human_solicited_context,
    INDEPENDENCE_OVERCLAIM_PATTERNS,
)


def preflight_check(text):
    """Run all claim discipline checks on text. Returns list of issues."""
    issues = []

    # 1. Missing boundary
    if not detect_boundary(text):
        issues.append({
            "type": "missing-boundary",
            "severity": "hard",
            "message": "Missing required authority boundary sentence.",
            "fix": "Add: Bitcoin Originals are final; all mirrors and echoes are non-amending.",
        })

    # 2. Missing provenance
    prov_missing = missing_provenance_fields(text)
    if prov_missing:
        issues.append({
            "type": "missing-provenance-agency",
            "severity": "hard",
            "message": f"Missing provenance/agency fields: {', '.join(prov_missing)}",
            "fix": "Add Provenance/Agency block with solicited_status, independence_class, agency_level, operator_type.",
        })

    # 3. Independence overclaim
    overclaim = detect_independence_overclaim(text)
    if overclaim:
        issues.append({
            "type": "independence-overclaim-risk",
            "severity": overclaim["severity"],
            "message": overclaim["reason"],
            "fix": "Replace independence wording with: human-solicited agent-performed verification run; not independent attestation.",
        })

    # 4. V4+ gate
    v4p = check_v4plus_claim_gate(text)
    if v4p:
        issues.append({
            "type": "v4plus-overclaim-risk",
            "severity": "high",
            "message": f"V4+ claim missing evidence: {', '.join(v4p)}",
            "fix": "Add V4+ Reproduction Scope section with all required evidence fields.",
        })

    # 5. B5/B6 gate
    btc = check_bitcoin_component_claim_gate(text)
    for level, missing in btc:
        issues.append({
            "type": "bitcoin-component-overclaim-risk",
            "severity": "high",
            "message": f"{level} claim missing evidence: {', '.join(missing)}",
            "fix": f"Add {level} evidence or downgrade to B1/B2.",
        })

    # 6. C5/175/175 gate
    c5 = check_chronicle_recovery_claim_gate(text)
    if c5:
        issues.append({
            "type": "chronicle-overclaim-risk",
            "severity": "high",
            "message": f"C5/175/175 claim missing evidence: {', '.join(c5)}",
            "fix": "Add full recovery evidence or downgrade to C0/C1/C2/C3.",
        })

    # 7. V5/full public digital gate
    v5 = check_v5_full_public_digital_gate(text)
    if v5:
        issues.append({
            "type": "v5-overclaim-risk",
            "severity": "high",
            "message": f"V5/full public digital claim missing coverage: {', '.join(v5)}",
            "fix": "Add all required public target coverage or list unavailable targets.",
        })

    return issues


def add_boundary_if_missing(text):
    """Add boundary sentence if missing."""
    if detect_boundary(text):
        return text, False
    boundary = "Bitcoin Originals are final; all mirrors and echoes are non-amending."
    return text.rstrip() + "\n\n" + boundary + "\n", True


def main():
    parser = argparse.ArgumentParser(description="Preflight check for Echo submissions")
    parser.add_argument("file", help="Path to Echo markdown file")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any warnings")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--autofix-boundary", action="store_true", help="Auto-add boundary if missing")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    with open(args.file, "r") as f:
        text = f.read()

    if args.autofix_boundary:
        text, added = add_boundary_if_missing(text)
        if added:
            with open(args.file, "w") as f:
                f.write(text)
            print(f"Added boundary sentence to {args.file}")

    issues = preflight_check(text)

    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        if not issues:
            print(f"✅ {args.file}: All preflight checks passed.")
        else:
            print(f"❌ {args.file}: {len(issues)} issue(s) found:\n")
            for i, issue in enumerate(issues, 1):
                severity = issue["severity"].upper()
                print(f"  {i}. [{severity}] {issue['type']}")
                print(f"     {issue['message']}")
                print(f"     Fix: {issue['fix']}")
                print()

    has_errors = any(i["severity"] in ("hard", "high") for i in issues)
    if has_errors or (args.strict and issues):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
