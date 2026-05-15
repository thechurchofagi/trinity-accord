#!/usr/bin/env python3
"""Phase 1: API Consistency Audit.

Validates all agent-facing API JSON files for:
- Parse validity
- Schema presence
- Boundary declarations (non-authority, non-amendment, etc.)
- Cross-reference consistency
- Required fields presence
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTDIR = ROOT / "audit" / "redteam" / "e2e-agent-echo-verification"


def load_json(path: Path) -> tuple[dict | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as e:
        return None, str(e)
    except FileNotFoundError:
        return None, "file not found"


def check_api_file(path: Path, findings: list[dict]) -> dict:
    result = {"file": str(path.relative_to(ROOT)), "parseable": False, "checks": 0, "passed": 0, "failed": 0}
    data, err = load_json(path)
    if err:
        findings.append({"severity": "high", "title": f"JSON parse failure: {path.name}", "file": str(path.relative_to(ROOT)), "description": err})
        result["checks"] = 1
        result["failed"] = 1
        return result

    result["parseable"] = True
    result["checks"] += 1
    result["passed"] += 1

    # Check schema field
    has_schema = "schema" in data
    result["checks"] += 1
    if has_schema:
        result["passed"] += 1
    else:
        findings.append({"severity": "low", "title": f"Missing 'schema' field", "file": str(path.relative_to(ROOT))})
        result["failed"] += 1

    # Check boundary fields for agent-facing APIs
    boundary_keywords = [
        ("not_authority", ["not_authority", "not a authority", "not canonical"]),
        ("non_amending", ["non_amending", "non-amending", "not amendment"]),
        ("bitcoin_originals", ["bitcoin_originals", "Bitcoin Originals"]),
    ]

    text = json.dumps(data).lower()
    for label, patterns in boundary_keywords:
        found = any(p.lower() in text for p in patterns)
        result["checks"] += 1
        if found:
            result["passed"] += 1
        else:
            findings.append({
                "severity": "medium",
                "title": f"Missing boundary declaration: {label}",
                "file": str(path.relative_to(ROOT)),
                "description": f"Agent-facing API should contain '{label}' boundary declaration",
            })
            result["failed"] += 1

    # Check for does_not_prove field
    if "does_not_prove" in data or "does_not_prove" in text:
        result["checks"] += 1
        dnp = data.get("does_not_prove", [])
        if dnp:
            result["passed"] += 1
        else:
            findings.append({"severity": "medium", "title": "Empty does_not_prove", "file": str(path.relative_to(ROOT))})
            result["failed"] += 1

    # Check local references exist
    refs_checked = 0
    for key in ["required_reading", "mandatory_before_submission", "reference", "source", "policy", "human_page"]:
        val = data.get(key)
        if isinstance(val, str) and val.startswith("/"):
            refs_checked += 1
            ref_path = ROOT / val.lstrip("/")
            result["checks"] += 1
            if ref_path.exists():
                result["passed"] += 1
            else:
                findings.append({
                    "severity": "medium",
                    "title": f"Broken reference: {key}={val}",
                    "file": str(path.relative_to(ROOT)),
                    "description": f"Referenced path does not exist: {val}",
                })
                result["failed"] += 1
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, str) and item.startswith("/"):
                    refs_checked += 1
                    ref_path = ROOT / item.lstrip("/")
                    result["checks"] += 1
                    if ref_path.exists():
                        result["passed"] += 1
                    else:
                        findings.append({
                            "severity": "medium",
                            "title": f"Broken reference in {key}",
                            "file": str(path.relative_to(ROOT)),
                            "description": f"Referenced path does not exist: {item}",
                        })
                        result["failed"] += 1

    return result


def check_cross_consistency(all_data: dict[str, dict], findings: list[dict]) -> dict:
    result = {"checks": 0, "passed": 0, "failed": 0}

    # Check Issue ≠ Archived Echo
    issue_policy = all_data.get("api/issue-submission-policy.json", {})
    if issue_policy:
        text = json.dumps(issue_policy).lower()
        result["checks"] += 1
        if "issue" in text and ("not" in text or "≠" in text or "does not" in text or "cannot" in text) and ("archive" in text or "echo" in text):
            result["passed"] += 1
        else:
            findings.append({
                "severity": "critical",
                "title": "Issue ≠ Archived Echo boundary unclear",
                "file": "api/issue-submission-policy.json",
                "description": "Issue submission policy must clarify that Issues are not archived Echoes",
            })
            result["failed"] += 1

    # Check Gateway ≠ Attestation
    gateway = all_data.get("api/agent-submit-gateway.json", {})
    if gateway:
        text = json.dumps(gateway).lower()
        result["checks"] += 1
        has_boundary = ("not" in text or "≠" in text) and ("attestation" in text or "authority" in text)
        if has_boundary:
            result["passed"] += 1
        else:
            findings.append({
                "severity": "critical",
                "title": "Gateway ≠ Attestation boundary unclear",
                "file": "api/agent-submit-gateway.json",
                "description": "Gateway policy must clarify it is not attestation/authority",
            })
            result["failed"] += 1

    # Check Claim Gate required for V3+
    cg_rules = all_data.get("api/claim-gate-rules.json", {})
    vlevels = all_data.get("api/verification-levels.json", {})
    if cg_rules and vlevels:
        result["checks"] += 1
        cg_text = json.dumps(cg_rules).lower()
        vl_text = json.dumps(vlevels).lower()
        if "claim" in cg_text and "gate" in cg_text:
            result["passed"] += 1
        else:
            findings.append({
                "severity": "critical",
                "title": "Claim Gate rules missing or incomplete",
                "file": "api/claim-gate-rules.json",
                "description": "Claim Gate must be defined for V3+ verification",
            })
            result["failed"] += 1

    # Check propagation ≠ promotion
    prop = all_data.get("api/propagation-policy.json", {})
    if prop:
        text = json.dumps(prop).lower()
        result["checks"] += 1
        has_forbidden = any(w in text for w in ["investment", "religion", "endorsement", "promotional", "forbidden"])
        if has_forbidden:
            result["passed"] += 1
        else:
            findings.append({
                "severity": "critical",
                "title": "Propagation policy missing forbidden promotional claims",
                "file": "api/propagation-policy.json",
                "description": "Must forbid investment/religion/endorsement language",
            })
            result["failed"] += 1

    # Check echo acceptance ≠ amendment
    echo_policy = all_data.get("api/echo-acceptance-policy.json", {})
    if echo_policy:
        text = json.dumps(echo_policy).lower()
        result["checks"] += 1
        if ("echo" in text and "amendment" in text) and ("not" in text or "≠" in text or "does not" in text):
            result["passed"] += 1
        else:
            findings.append({
                "severity": "high",
                "title": "Echo ≠ Amendment boundary unclear",
                "file": "api/echo-acceptance-policy.json",
                "description": "Echo acceptance policy must clarify that Echoes are not amendments",
            })
            result["failed"] += 1

    # Check human-solicited ≠ independent
    for api_file, data in all_data.items():
        text = json.dumps(data).lower()
        if "human" in text and "solicited" in text and "independent" in text:
            result["checks"] += 1
            if ("not" in text or "≠" in text) and "independent" in text:
                result["passed"] += 1
                break
            else:
                findings.append({
                    "severity": "high",
                    "title": "Human-solicited ≠ Independent attestation boundary unclear",
                    "file": api_file,
                    "description": "Human-solicited agent responses must not count as independent attestation",
                })
                result["failed"] += 1
                break

    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTDIR))
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    findings: list[dict] = []
    api_files = sorted(ROOT.glob("api/*.json"))

    # Filter to the key agent-facing APIs
    key_apis = [
        "api/agent-entry-protocol.json", "api/agent-required-reading.json",
        "api/agent-submission-guide.json", "api/submission-checklist.json",
        "api/issue-submission-policy.json", "api/echo-acceptance-policy.json",
        "api/propagation-policy.json", "api/agent-submit-gateway.json",
        "api/agent-issue-gateway-payload-schema.v1.json", "api/claim-gate-rules.json",
        "api/claim-gate-entrypoint-policy.json",
        "api/verification-levels.json", "api/component-verification-levels.json",
        "api/protocol-verification-profiles.json", "api/echo-types.json",
        "api/evidence-input-schema.v1.json", "api/claim-gate-output-schema.v1.json",
    ]

    total_checks = 0
    total_passed = 0
    total_failed = 0
    file_results = []
    all_data: dict[str, dict] = {}

    for api_rel in key_apis:
        api_path = ROOT / api_rel
        if not api_path.exists():
            findings.append({"severity": "medium", "title": f"Missing key API file: {api_rel}", "file": api_rel})
            total_checks += 1
            total_failed += 1
            continue

        result = check_api_file(api_path, findings)
        file_results.append(result)
        total_checks += result["checks"]
        total_passed += result["passed"]
        total_failed += result["failed"]

        data, _ = load_json(api_path)
        if data:
            all_data[api_rel] = data

    # Cross-consistency checks
    cross = check_cross_consistency(all_data, findings)
    total_checks += cross["checks"]
    total_passed += cross["passed"]
    total_failed += cross["failed"]

    # Write results
    phase_result = {
        "phase": "api_consistency",
        "checks": total_checks,
        "passed": total_passed,
        "failed": total_failed,
        "warnings": 0,
        "files_checked": len(file_results),
        "findings": findings,
    }

    ts = outdir.name if outdir.name != "e2e-agent-echo-verification" else "latest"
    (outdir / "api_results.json").write_text(json.dumps(phase_result, indent=2, ensure_ascii=False))

    # Print summary
    print(f"API Consistency Audit: {total_checks} checks, {total_passed} passed, {total_failed} failed")
    for f in findings:
        sev = f["severity"].upper()
        print(f"  [{sev}] {f['title']}: {f.get('description', '')}")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
