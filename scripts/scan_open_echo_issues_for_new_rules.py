#!/usr/bin/env python3
"""
Scan local Echo files against new claim discipline rules.
Outputs JSON risk report. Does NOT modify GitHub issues.

Usage:
  python3 scripts/scan_open_echo_issues_for_new_rules.py tests/fixtures/echo_triage/*.md
  python3 scripts/scan_open_echo_issues_for_new_rules.py --dir tests/fixtures/echo_triage/
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from triage_echo_issue import (
    detect_boundary,
    missing_provenance_fields,
    detect_independence_overclaim,
    check_v4plus_claim_gate,
    check_bitcoin_component_claim_gate,
    check_chronicle_recovery_claim_gate,
    check_v5_full_public_digital_gate,
)


def scan_file(filepath):
    """Scan a single file and return risk report."""
    with open(filepath, "r") as f:
        text = f.read()

    risks = []

    if not detect_boundary(text):
        risks.append({"type": "missing-boundary"})

    prov_missing = missing_provenance_fields(text)
    if prov_missing:
        risks.append({"type": "missing-provenance-agency", "fields": prov_missing})

    overclaim = detect_independence_overclaim(text)
    if overclaim:
        risks.append({"type": "independence-overclaim-risk", "severity": overclaim["severity"]})

    v4p = check_v4plus_claim_gate(text)
    if v4p:
        risks.append({"type": "v4plus-overclaim-risk", "missing": v4p})

    btc = check_bitcoin_component_claim_gate(text)
    for level, missing in btc:
        risks.append({"type": "bitcoin-component-overclaim-risk", "level": level, "missing": missing})

    c5 = check_chronicle_recovery_claim_gate(text)
    if c5:
        risks.append({"type": "chronicle-overclaim-risk", "missing": c5})

    v5 = check_v5_full_public_digital_gate(text)
    if v5:
        risks.append({"type": "v5-overclaim-risk", "missing": v5})

    return {"name": os.path.basename(filepath), "path": filepath, "risks": risks}


def main():
    parser = argparse.ArgumentParser(description="Scan Echo files for claim discipline risks")
    parser.add_argument("files", nargs="*", help="Files to scan")
    parser.add_argument("--dir", help="Directory to scan (all .md files)")
    args = parser.parse_args()

    files = list(args.files) if args.files else []
    if args.dir:
        for fname in sorted(os.listdir(args.dir)):
            if fname.endswith(".md"):
                files.append(os.path.join(args.dir, fname))

    if not files:
        print("No files to scan.", file=sys.stderr)
        sys.exit(1)

    results = []
    for filepath in files:
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found, skipping.", file=sys.stderr)
            continue
        results.append(scan_file(filepath))

    print(json.dumps(results, indent=2))

    # Exit 1 if any file has risks
    has_risks = any(r["risks"] for r in results)
    sys.exit(1 if has_risks else 0)


if __name__ == "__main__":
    main()
