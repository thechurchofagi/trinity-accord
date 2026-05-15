#!/usr/bin/env python3
"""Phase 4: Gateway Payload Schema Audit.

Validates gateway payloads against schema rules and boundary requirements.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTDIR = ROOT / "audit" / "redteam" / "e2e-agent-echo-verification"


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTDIR))
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Load the gateway payload schema
    schema_path = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
    findings = []
    total_checks = 0
    total_passed = 0
    total_failed = 0

    if schema_path.exists():
        schema = json.loads(schema_path.read_text())
        total_checks += 1
        if schema.get("additionalProperties") is False:
            total_passed += 1
        else:
            total_failed += 1
            findings.append({
                "severity": "high",
                "title": "Gateway schema allows additionalProperties",
                "file": "api/agent-issue-gateway-payload-schema.v1.json",
                "description": "Schema should have additionalProperties: false for strict validation",
            })

        # Check required fields
        required = schema.get("required", [])
        total_checks += 1
        critical_fields = ["schema", "submission_type", "title", "body", "boundary_acknowledgement"]
        missing = [f for f in critical_fields if f not in required]
        if not missing:
            total_passed += 1
        else:
            total_failed += 1
            findings.append({
                "severity": "high",
                "title": "Gateway schema missing required fields",
                "file": "api/agent-issue-gateway-payload-schema.v1.json",
                "description": f"Missing required: {missing}",
            })
    else:
        findings.append({"severity": "critical", "title": "Gateway schema file not found", "file": "api/agent-issue-gateway-payload-schema.v1.json"})
        total_checks += 1
        total_failed += 1

    # Validate fixture payloads
    gw_dir = ROOT / "tests" / "fixtures" / "redteam" / "gateway_payloads"
    if gw_dir.exists():
        for fixture in sorted(gw_dir.glob("*.json")):
            try:
                data = json.loads(fixture.read_text())
            except json.JSONDecodeError as e:
                findings.append({"severity": "high", "title": f"Invalid JSON: {fixture.name}", "file": str(fixture.relative_to(ROOT)), "description": str(e)})
                total_checks += 1
                total_failed += 1
                continue

            # Check boundary_acknowledgement
            boundary = data.get("boundary_acknowledgement", {})
            for key in ["not_authority", "not_amendment", "not_attestation", "bitcoin_originals_prevail"]:
                total_checks += 1
                if boundary.get(key) is True:
                    total_passed += 1
                else:
                    total_failed += 1
                    findings.append({
                        "severity": "high",
                        "title": f"Missing/false boundary: {key} in {fixture.name}",
                        "file": str(fixture.relative_to(ROOT)),
                        "expected": f"{key} = true",
                        "actual": str(boundary.get(key, "missing")),
                    })

            # Check for secret-like patterns in body
            body = data.get("body", "")
            total_checks += 1
            secret_patterns = [r"ghp_[a-zA-Z0-9]{36}", r"github_pat_", r"sk-[a-zA-Z0-9]{20,}", r"Bearer [a-zA-Z0-9]{20,}"]
            has_secret = any(re.search(p, body) for p in secret_patterns)
            if not has_secret:
                total_passed += 1
            else:
                total_failed += 1
                findings.append({
                    "severity": "critical",
                    "title": f"Secret-like pattern in body: {fixture.name}",
                    "file": str(fixture.relative_to(ROOT)),
                    "description": "Body contains what looks like a secret/token",
                })

            # Check body length
            total_checks += 1
            if 20 <= len(body) <= 60000:
                total_passed += 1
            else:
                total_failed += 1
                findings.append({
                    "severity": "medium",
                    "title": f"Body length out of bounds: {fixture.name}",
                    "file": str(fixture.relative_to(ROOT)),
                    "description": f"Body length: {len(body)} (expected 20-60000)",
                })

    result = {
        "phase": "gateway",
        "checks": total_checks,
        "passed": total_passed,
        "failed": total_failed,
        "warnings": 0,
        "findings": findings,
    }
    (outdir / "gateway_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"Gateway Audit: {total_checks} checks, {total_passed} passed, {total_failed} failed")
    for f in findings:
        print(f"  [{f['severity'].upper()}] {f['title']}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
