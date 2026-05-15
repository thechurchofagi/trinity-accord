#!/usr/bin/env python3
"""Phase 3: Issue Submission Triage Audit.

Tests issue body fixtures against expected triage outcomes.
Validates Issue ≠ Archived Echo boundary.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTDIR = ROOT / "audit" / "redteam" / "e2e-agent-echo-verification"

FORBIDDEN_PATTERNS = [
    (r"\bv[5-8]\b.*\bverified\b", "V5-V8 claim without Claim Gate"),
    (r"\bindependent\s+(verification|attestation)\b", "Independent attestation claim"),
    (r"\barchived?\s+echo\b", "Claims archived Echo status"),
    (r"\bcanonical\s+(amendment|authority)\b", "Claims canonical authority"),
    (r"\binvestment\b", "Investment language"),
    (r"\breligio(?:n|us|us)\b", "Religious language"),
    (r"\bendorsed?\b", "Endorsement claim"),
    (r"\bmust\s+(care|obey|follow)\b", "Coercive language"),
]

BOUNDARY_KEYWORDS = [
    "not authority", "non-amending", "bitcoin originals",
    "not amendment", "not attestation",
]


def check_issue_body(text: str, fixture_name: str) -> dict:
    result = {
        "fixture": fixture_name,
        "checks": 0,
        "passed": 0,
        "failed": 0,
        "flags": [],
        "expected_state": "unknown",
    }

    lower_text = text.lower()

    # Check for forbidden overclaims
    for pattern, desc in FORBIDDEN_PATTERNS:
        result["checks"] += 1
        if re.search(pattern, lower_text):
            result["flags"].append({"type": "overclaim", "description": desc, "pattern": pattern})
            result["failed"] += 1
        else:
            result["passed"] += 1

    # Check for boundary acknowledgement
    result["checks"] += 1
    has_boundary = any(kw in lower_text for kw in BOUNDARY_KEYWORDS)
    if has_boundary:
        result["passed"] += 1
    else:
        result["flags"].append({"type": "missing_boundary", "description": "No boundary acknowledgement found"})
        result["failed"] += 1

    # Check for Claim Gate reference (for V3+ claims)
    if re.search(r"\bv[3-8]\b", lower_text):
        result["checks"] += 1
        has_cg = any(kw in lower_text for kw in ["claim gate", "claim-gate", "report builder"])
        if has_cg:
            result["passed"] += 1
        else:
            result["flags"].append({"type": "missing_claim_gate", "description": "V3+ claim without Claim Gate reference"})
            result["failed"] += 1

    # Determine expected state
    if result["failed"] == 0:
        result["expected_state"] = "screened"
    elif any(f["type"] == "overclaim" for f in result["flags"]):
        result["expected_state"] = "overclaim-risk"
    else:
        result["expected_state"] = "needs-human-review"

    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTDIR))
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    fixtures_dir = ROOT / "tests" / "fixtures" / "redteam" / "issue_bodies"
    if not fixtures_dir.exists():
        print("No issue fixtures directory found")
        return 0

    findings = []
    total_checks = 0
    total_passed = 0
    total_failed = 0

    for fixture in sorted(fixtures_dir.glob("*.md")):
        text = fixture.read_text(encoding="utf-8")
        result = check_issue_body(text, fixture.name)
        total_checks += result["checks"]
        total_passed += result["passed"]
        total_failed += result["failed"]

        if result["failed"] > 0:
            findings.append({
                "severity": "high" if any(f["type"] == "overclaim" for f in result["flags"]) else "medium",
                "title": f"Issue fixture flagged: {fixture.name}",
                "file": str(fixture.relative_to(ROOT)),
                "description": "; ".join(f["description"] for f in result["flags"]),
                "expected": "clean boundary acknowledgement",
                "actual": f"{result['failed']} flags: {[f['type'] for f in result['flags']]}",
            })

    # Also check gateway payloads
    gw_dir = ROOT / "tests" / "fixtures" / "redteam" / "gateway_payloads"
    if gw_dir.exists():
        for fixture in sorted(gw_dir.glob("*.json")):
            data, err = (json.loads(fixture.read_text()), None) if fixture.exists() else (None, "not found")
            if err:
                findings.append({"severity": "high", "title": f"Gateway fixture parse error: {fixture.name}", "file": str(fixture.relative_to(ROOT)), "description": err})
                total_checks += 1
                total_failed += 1
                continue

            # Check boundary acknowledgement
            boundary = data.get("boundary_acknowledgement", {})
            total_checks += 6
            for key in ["not_authority", "not_amendment", "not_attestation", "bitcoin_originals_prevail"]:
                if boundary.get(key) is True:
                    total_passed += 1
                else:
                    total_failed += 1
                    findings.append({
                        "severity": "high",
                        "title": f"Gateway fixture missing boundary: {key}",
                        "file": str(fixture.relative_to(ROOT)),
                        "expected": f"boundary_acknowledgement.{key} = true",
                        "actual": str(boundary.get(key, "missing")),
                    })

            total_checks += 1
            if boundary.get("not_verification_unless_claim_gate_report_attached") is True:
                total_passed += 1
            else:
                total_failed += 1
                findings.append({
                    "severity": "high",
                    "title": f"Gateway fixture missing Claim Gate boundary",
                    "file": str(fixture.relative_to(ROOT)),
                })

    result = {
        "phase": "issues",
        "checks": total_checks,
        "passed": total_passed,
        "failed": total_failed,
        "warnings": 0,
        "findings": findings,
    }
    (outdir / "issues_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"Issue/Gateway Audit: {total_checks} checks, {total_passed} passed, {total_failed} failed")
    for f in findings:
        print(f"  [{f['severity'].upper()}] {f['title']}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
