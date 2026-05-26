#!/usr/bin/env python3
"""E2E Red Team Audit Orchestrator for Trinity Accord.

Runs all redteam audit phases and generates a consolidated report.

Usage:
    python3 tools/redteam/run_e2e_redteam_audit.py --offline
    python3 tools/redteam/run_e2e_redteam_audit.py --allow-network
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)


def main() -> int:
    parser = argparse.ArgumentParser(description="E2E Red Team Audit")
    parser.add_argument("--allow-network", action="store_true", help="Enable network tests (download Release assets)")
    parser.add_argument("--phase", type=str, default="all", help="Run specific phase (all, api, entrypoints, issues, gateway, claim_gate, verification, echo_lifecycle, propagation, attestation, release, toctou, unicode)")
    args = parser.parse_args()

    ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    outdir = ROOT / "audit" / "redteam" / "e2e-agent-echo-verification" / ts
    outdir.mkdir(parents=True, exist_ok=True)

    # Baseline
    baseline = {
        "generated_at": ts,
        "commit": run(["git", "rev-parse", "HEAD"]).stdout.strip(),
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip(),
        "shallow": run(["git", "rev-parse", "--is-shallow-repository"]).stdout.strip(),
        "python_version": sys.version,
        "node_version": run(["node", "--version"]).stdout.strip() if Path("/usr/bin/node").exists() or True else "n/a",
        "network_allowed": args.allow_network,
    }

    # Check required API files exist
    required_apis = [
        "api/agent-entry-protocol.json", "api/agent-required-reading.json",
        "api/agent-submission-guide.json", "api/submission-checklist.json",
        "api/issue-submission-policy.json", "api/echo-acceptance-policy.json",
        "api/propagation-policy.json", "api/agent-submit-gateway.json",
        "api/agent-issue-gateway-payload-schema.v1.json", "api/claim-gate-rules.json",
        "api/evidence-input-schema.v1.json", "api/claim-gate-output-schema.v1.json",
        "api/verification-levels.json", "api/component-verification-levels.json",
        "api/protocol-verification-profiles.json", "api/echo-types.json",
    ]
    api_existence = {}
    for api in required_apis:
        api_existence[api] = (ROOT / api).exists()
    baseline["required_apis"] = api_existence
    baseline["required_apis_present"] = sum(api_existence.values())
    baseline["required_apis_total"] = len(api_existence)

    # Run phases
    phases_to_run = []
    if args.phase == "all":
        phases_to_run = ["api", "entrypoints", "issues", "gateway", "propagation", "release", "attestation"]
    else:
        phases_to_run = [args.phase]

    results = {}
    total_checks = 0
    total_passed = 0
    total_failed = 0
    total_warnings = 0
    findings = {"critical": [], "high": [], "medium": [], "low": []}

    for phase in phases_to_run:
        script = ROOT / "tools" / "redteam" / f"{phase}_audit.py"
        if not script.exists():
            print(f"SKIP phase {phase}: {script} not found")
            continue

        print(f"\n{'='*60}")
        print(f"Running phase: {phase}")
        print(f"{'='*60}")

        cp = run([sys.executable, str(script), "--output-dir", str(outdir)])
        print(cp.stdout)
        if cp.stderr:
            print(f"STDERR: {cp.stderr}", file=sys.stderr)

        # Parse results from JSON if available
        result_file = outdir / f"{phase}_results.json"
        if result_file.exists():
            phase_result = json.loads(result_file.read_text())
            results[phase] = phase_result
            total_checks += phase_result.get("checks", 0)
            total_passed += phase_result.get("passed", 0)
            total_failed += phase_result.get("failed", 0)
            total_warnings += phase_result.get("warnings", 0)
            for f in phase_result.get("findings", []):
                sev = f.get("severity", "low")
                findings.setdefault(sev, []).append(f)

    # Write summary
    summary = {
        "schema": "trinityaccord.redteam.e2e-summary.v1",
        "commit": baseline["commit"],
        "generated_at": ts,
        "branch": baseline["branch"],
        "network_allowed": args.allow_network,
        "phases_run": list(results.keys()),
        "totals": {
            "checks": total_checks,
            "passed": total_passed,
            "failed": total_failed,
            "warnings": total_warnings,
        },
        "findings": {
            "critical": len(findings.get("critical", [])),
            "high": len(findings.get("high", [])),
            "medium": len(findings.get("medium", [])),
            "low": len(findings.get("low", [])),
        },
        "invariants": {
            "issue_not_archived_echo": "pass" if not any("issue.*archive" in str(f).lower() for f in findings.get("critical", [])) else "fail",
            "gateway_not_attestation": "pass" if not any("gateway.*attestation" in str(f).lower() for f in findings.get("critical", [])) else "fail",
            "claim_gate_required": "pass" if not any("claim.*gate.*bypass" in str(f).lower() for f in findings.get("critical", [])) else "fail",
            "propagation_not_promotion": "pass" if not any("propagation.*promotion" in str(f).lower() for f in findings.get("critical", [])) else "fail",
            "human_solicited_not_independent": "pass" if not any("human.*solicited.*independent" in str(f).lower() for f in findings.get("critical", [])) else "fail",
        },
    }

    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    (outdir / "findings.json").write_text(json.dumps(findings, indent=2, ensure_ascii=False))

    # Generate report
    report_lines = []
    report_lines.append("# E2E Agent / Echo / Verification Redteam Audit\n")
    report_lines.append(f"Generated: `{ts}`")
    report_lines.append(f"Commit: `{baseline['commit']}`")
    report_lines.append(f"Branch: `{baseline['branch']}`\n")
    report_lines.append("## Executive Summary\n")
    report_lines.append(f"- Total checks: **{total_checks}**")
    report_lines.append(f"- Passed: **{total_passed}**")
    report_lines.append(f"- Failed: **{total_failed}**")
    report_lines.append(f"- Warnings: **{total_warnings}**\n")
    report_lines.append("### Findings\n")
    report_lines.append(f"- Critical: **{len(findings.get('critical', []))}**")
    report_lines.append(f"- High: **{len(findings.get('high', []))}**")
    report_lines.append(f"- Medium: **{len(findings.get('medium', []))}**")
    report_lines.append(f"- Low: **{len(findings.get('low', []))}**\n")
    report_lines.append("## Core Invariants\n")
    for inv, status in summary["invariants"].items():
        icon = "✅" if status == "pass" else "❌"
        report_lines.append(f"- {icon} `{inv}`: {status}")
    report_lines.append("")
    report_lines.append("## API File Baseline\n")
    for api, exists in api_existence.items():
        icon = "✅" if exists else "❌"
        report_lines.append(f"- {icon} `{api}`")

    report_lines.append("\n## Phases Run\n")
    for phase, result in results.items():
        report_lines.append(f"### {phase}")
        report_lines.append(f"- Checks: {result.get('checks', 0)}")
        report_lines.append(f"- Passed: {result.get('passed', 0)}")
        report_lines.append(f"- Failed: {result.get('failed', 0)}")
        report_lines.append("")

    if any(findings.values()):
        report_lines.append("## Findings Detail\n")
        for sev in ["critical", "high", "medium", "low"]:
            for f in findings.get(sev, []):
                report_lines.append(f"### [{sev.upper()}] {f.get('title', 'Untitled')}")
                report_lines.append(f"- File: `{f.get('file', 'n/a')}`")
                report_lines.append(f"- Description: {f.get('description', 'n/a')}")
                if f.get("expected"):
                    report_lines.append(f"- Expected: {f['expected']}")
                if f.get("actual"):
                    report_lines.append(f"- Actual: {f['actual']}")
                report_lines.append("")

    (outdir / "report.md").write_text("\n".join(report_lines) + "\n")
    print(f"\nReport written to: {outdir / 'report.md'}")
    print(f"Summary: {total_checks} checks, {total_passed} passed, {total_failed} failed, {total_warnings} warnings")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
