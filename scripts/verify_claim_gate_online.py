#!/usr/bin/env python3
"""
Online verification for Claim Gate — checks live availability of claim gate resources.

Usage:
    python3 scripts/verify_claim_gate_online.py [--base-url URL]
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BASE = "https://www.trinityaccord.org"


def check_url(base, path):
    """Check if a URL is accessible."""
    url = f"{base.rstrip('/')}{path}"
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False


def check_json_valid(path):
    """Check if a local JSON file is valid."""
    try:
        with open(path) as f:
            json.load(f)
        return True
    except Exception:
        return False


def main():
    base = DEFAULT_BASE
    if "--base-url" in sys.argv:
        idx = sys.argv.index("--base-url")
        if idx + 1 < len(sys.argv):
            base = sys.argv[idx + 1]

    checks = []
    passed = 0
    failed = 0

    # 1. Local JSON validity
    local_checks = [
        ("api/claim-gate-rules.json", "Claim gate rules JSON valid"),
        ("api/evidence-input-schema.v1.json", "Evidence input schema JSON valid"),
        ("api/claim-gate-output-schema.v1.json", "Claim gate output schema JSON valid"),
        ("api/report-builder-policy.json", "Report builder policy JSON valid"),
    ]
    for path, desc in local_checks:
        full = ROOT / path
        ok = full.exists() and check_json_valid(full)
        checks.append((desc, ok))
        if ok:
            passed += 1
        else:
            failed += 1

    # 2. Online availability
    online_checks = [
        ("/api/claim-gate-rules.json", "Claim gate rules online"),
        ("/api/evidence-input-schema.v1.json", "Evidence input schema online"),
        ("/api/claim-gate-output-schema.v1.json", "Claim gate output schema online"),
        ("/api/report-builder-policy.json", "Report builder policy online"),
        ("/llms.txt", "llms.txt accessible"),
    ]
    for path, desc in online_checks:
        ok = check_url(base, path)
        checks.append((desc, ok))
        if ok:
            passed += 1
        else:
            failed += 1

    # 3. Content checks
    llms_path = ROOT / "llms.txt"
    if llms_path.exists():
        content = llms_path.read_text()
        has_claim_gate = "claim gate" in content.lower() or "claim-gate" in content.lower()
        checks.append(("llms.txt mentions Claim Gate", has_claim_gate))
        if has_claim_gate:
            passed += 1
        else:
            failed += 1

    agent_verify = ROOT / "agent-verify.md"
    if agent_verify.exists():
        content = agent_verify.read_text()
        has_gate = "claim gate" in content.lower() or "claim-gate" in content.lower()
        checks.append(("agent-verify.md mentions Claim Gate", has_gate))
        if has_gate:
            passed += 1
        else:
            failed += 1

    # Print results
    print("=== Claim Gate Online Verification ===\n")
    for desc, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {desc}")

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{passed + failed} passed, {failed}/{passed + failed} failed")
    if failed == 0:
        print("FINAL: PASS — claim gate online verification passed.")
    else:
        print("FINAL: FAIL — some online checks failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
