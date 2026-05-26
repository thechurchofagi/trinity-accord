#!/usr/bin/env python3
"""Phase 9: Attestation Claims Audit.

Tests attestation fixtures for proper type classification.
Human-solicited ≠ Independent, self-reported ≠ institutional, etc.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTDIR = ROOT / "audit" / "redteam" / "e2e-agent-echo-verification"


def check_attestation_fixture(data: dict, fixture_name: str) -> dict:
    result = {"fixture": fixture_name, "checks": 0, "passed": 0, "failed": 0, "flags": []}
    att_type = data.get("attestation_type", "unknown")
    claimed = data.get("claimed_status", "unknown")

    # Rule: human_solicited never counts as independent
    if att_type == "human_solicited":
        result["checks"] += 1
        if claimed in ("independent", "independent_attestation", "accepted_independent"):
            result["failed"] += 1
            result["flags"].append({"type": "human_solicited_claims_independent"})
        else:
            result["passed"] += 1

    # Rule: self_reported never counts as institutional
    if att_type == "self_reported":
        result["checks"] += 1
        if claimed in ("institutional", "accepted_institutional"):
            result["failed"] += 1
            result["flags"].append({"type": "self_reported_claims_institutional"})
        else:
            result["passed"] += 1

    # Rule: gateway intake ≠ attestation
    if att_type == "gateway_intake":
        result["checks"] += 1
        if claimed in ("attestation", "accepted_attestation", "independent"):
            result["failed"] += 1
            result["flags"].append({"type": "gateway_claims_attestation"})
        else:
            result["passed"] += 1

    # Rule: custody notice ≠ verification
    if att_type == "custody_notice":
        result["checks"] += 1
        if claimed in ("verified", "physical_verification", "forensic"):
            result["failed"] += 1
            result["flags"].append({"type": "custody_claims_verification"})
        else:
            result["passed"] += 1

    # Rule: test_record ≠ accepted
    if att_type == "test_record":
        result["checks"] += 1
        if claimed in ("accepted", "accepted_echo", "accepted_independent"):
            result["failed"] += 1
            result["flags"].append({"type": "test_record_claims_accepted"})
        else:
            result["passed"] += 1

    # Rule: NFT ownership ≠ governance authority
    if att_type == "nft_owner":
        result["checks"] += 1
        if claimed in ("governance", "authority", "interpretation_authority"):
            result["failed"] += 1
            result["flags"].append({"type": "nft_claims_governance"})
        else:
            result["passed"] += 1

    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTDIR))
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    attest_dir = ROOT / "tests" / "fixtures" / "redteam" / "attestation"
    findings = []
    total_checks = 0
    total_passed = 0
    total_failed = 0

    if attest_dir.exists():
        for fixture in sorted(attest_dir.glob("*.json")):
            try:
                data = json.loads(fixture.read_text())
            except json.JSONDecodeError:
                findings.append({"severity": "medium", "title": f"Invalid JSON: {fixture.name}", "file": str(fixture.relative_to(ROOT))})
                total_checks += 1
                total_failed += 1
                continue

            result = check_attestation_fixture(data, fixture.name)
            total_checks += result["checks"]
            total_passed += result["passed"]
            total_failed += result["failed"]

            if result["failed"] > 0:
                findings.append({
                    "severity": "critical",
                    "title": f"Attestation boundary violation: {fixture.name}",
                    "file": str(fixture.relative_to(ROOT)),
                    "description": f"Flags: {[f['type'] for f in result['flags']]}",
                })

    result = {
        "phase": "attestation",
        "checks": total_checks,
        "passed": total_passed,
        "failed": total_failed,
        "warnings": 0,
        "findings": findings,
    }
    (outdir / "attestation_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"Attestation Audit: {total_checks} checks, {total_passed} passed, {total_failed} failed")
    for f in findings:
        print(f"  [{f['severity'].upper()}] {f['title']}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
