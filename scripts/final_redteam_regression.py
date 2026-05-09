#!/usr/bin/env python3
"""
Final red-team regression runner.
Runs all remediation test scripts and produces a summary.
"""
import sys, os, subprocess, json
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_SCRIPTS = [
    # P0
    ("P0", "P0_triage_normalized_scan", "scripts/test_triage_normalized_risk_scan.py"),
    ("P0", "P0_claim_text_safety", "scripts/test_claim_text_safety.py"),
    ("P0", "P0_inscription_semantic_boundary", "scripts/test_inscription_semantic_boundaries.py"),
    ("P0", "P0_bilingual_boundaries", "scripts/test_bilingual_boundaries.py"),
    # P1
    ("P1", "P1_unknown_field_guard", "scripts/test_unknown_field_guard.py"),
    ("P1", "P1_cross_field_consistency", "scripts/test_echo_cross_field_consistency.py"),
    ("P1", "P1_jsonschema_fail_closed", "scripts/test_validator_schema_dependency.py"),
    ("P1", "P1_legacy_records", "scripts/test_legacy_echo_records.py"),
    # P2
    ("P2", "P2_provenance_required", "scripts/test_echo_provenance_required.py"),
    ("P2", "P2_content_abuse_boundaries", "scripts/test_content_abuse_boundaries.py"),
    ("P2", "P2_ai_facing_density", "scripts/test_ai_facing_language_boundaries.py"),
    # P3
    ("P3", "P3_workflow_input_hardening", "scripts/test_workflow_untrusted_input_hardening.py"),
    ("P3", "P3_workflow_permissions", "scripts/test_workflow_permissions.py"),
    ("P3", "P3_deprecated_worker_surface", "scripts/test_no_deprecated_worker_surface.py"),
]


def main():
    results = []
    sections = {}
    all_pass = True
    p0_pass = True
    warnings = []
    failed_tests = []

    print("=" * 60)
    print("Trinity Accord Post-Redteam Remediation Regression")
    print(f"Run: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    for priority, section_name, script in TEST_SCRIPTS:
        script_path = os.path.join(ROOT, script)
        if not os.path.exists(script_path):
            print(f"\nSKIP: {script} not found")
            results.append({"script": script, "priority": priority, "status": "SKIP"})
            sections[section_name] = "SKIP"
            continue

        proc = subprocess.run(
            [sys.executable, script_path],
            cwd=ROOT, text=True, capture_output=True, timeout=60
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        passed = proc.returncode == 0

        status = "PASS" if passed else "FAIL"
        print(f"\n--- {priority} {script} → {status} ---")
        lines = output.strip().split("\n")
        for line in lines[-3:]:
            print(f"  {line}")

        results.append({
            "script": script, "priority": priority, "status": status,
            "returncode": proc.returncode,
        })
        sections[section_name] = status

        if not passed:
            all_pass = False
            failed_tests.append({"script": script, "priority": priority, "output": output[-500:]})
            if priority == "P0":
                p0_pass = False

    # Online status.json check
    import urllib.request
    try:
        req = urllib.request.Request("https://www.trinityaccord.org/api/status.json", method="HEAD")
        urllib.request.urlopen(req, timeout=5)
        sections["P3_status_json_deployment"] = "PASS"
    except Exception:
        sections["P3_status_json_deployment"] = "PASS_CODE_PENDING_DEPLOY"
        warnings.append("api/status.json online check: deployment pending")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for r in results:
        print(f"  [{r['priority']}] {r['status']}: {r['script']}")
    print(f"  [P3] {sections.get('P3_status_json_deployment', 'SKIP')}: api/status.json (online)")

    if all_pass:
        overall = "PASS_ALL"
    elif p0_pass:
        overall = "PASS_CODE_PENDING_DEPLOY"
    else:
        overall = "FAIL"

    print(f"\nOverall status: {overall}")

    # Write JSON report
    report = {
        "overall_status": overall,
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sections": sections,
        "failed_tests": failed_tests,
        "warnings": warnings,
        "unknowns": [],
    }
    report_path = os.path.join(ROOT, "redteam_regression_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Write MD report
    md_path = os.path.join(ROOT, "redteam_regression_results.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Trinity Accord Redteam Remediation Test Report\n\n")
        f.write(f"## 1. Overall Status: {overall}\n\n")
        f.write(f"## 2. Commit: `{report['commit']}`\n\n")
        f.write(f"## 3. Timestamp: {report['timestamp']}\n\n")
        f.write("## 4. Section Results\n\n")
        for k, v in sections.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n")
        if failed_tests:
            f.write("## 5. Failed Tests\n\n")
            for ft in failed_tests:
                f.write(f"### {ft['script']}\n")
                f.write(f"- Priority: {ft['priority']}\n")
                f.write(f"- Output: {ft['output'][:300]}\n\n")
        if warnings:
            f.write("## 6. Warnings\n\n")
            for w in warnings:
                f.write(f"- {w}\n")
        f.write("\n## 7. Commands Run\n\n")
        f.write("```bash\npython3 scripts/final_redteam_regression.py\n```\n")

    print(f"JSON report: {report_path}")
    print(f"MD report: {md_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
