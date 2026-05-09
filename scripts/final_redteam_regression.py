#!/usr/bin/env python3
"""
Final red-team regression runner.
Runs all remediation test scripts and produces a summary.
"""
import sys
import os
import subprocess
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEST_SCRIPTS = [
    # P0
    ("P0", "scripts/test_triage_normalized_risk_scan.py"),
    ("P0", "scripts/test_inscription_semantic_boundaries.py"),
    # P1
    ("P1", "scripts/test_unknown_field_guard.py"),
    ("P1", "scripts/test_echo_cross_field_consistency.py"),
    ("P1", "scripts/test_validator_schema_dependency.py"),
    # P2
    ("P2", "scripts/test_content_abuse_boundaries.py"),
    # P3
    ("P3", "scripts/test_workflow_untrusted_input_hardening.py"),
    ("P3", "scripts/test_no_deprecated_worker_surface.py"),
]


def main():
    results = []
    all_pass = True
    p0_pass = True

    print("=" * 60)
    print("Trinity Accord Post-Redteam Remediation Regression")
    print(f"Run: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    for priority, script in TEST_SCRIPTS:
        script_path = os.path.join(ROOT, script)
        if not os.path.exists(script_path):
            print(f"\nSKIP: {script} not found")
            results.append({"script": script, "priority": priority, "status": "SKIP"})
            continue

        proc = subprocess.run(
            [sys.executable, script_path],
            cwd=ROOT, text=True, capture_output=True, timeout=60
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        passed = proc.returncode == 0

        status = "PASS" if passed else "FAIL"
        print(f"\n--- {priority} {script} → {status} ---")
        # Print last 5 lines
        lines = output.strip().split("\n")
        for line in lines[-5:]:
            print(f"  {line}")

        results.append({
            "script": script,
            "priority": priority,
            "status": status,
            "returncode": proc.returncode,
        })

        if not passed:
            all_pass = False
            if priority == "P0":
                p0_pass = False

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for r in results:
        print(f"  [{r['priority']}] {r['status']}: {r['script']}")

    if all_pass:
        overall = "PASS_ALL"
    elif p0_pass:
        overall = "PASS_CODE_PENDING_DEPLOY"
    else:
        overall = "FAIL"

    print(f"\nOverall status: {overall}")
    print(f"P0: {'PASS' if p0_pass else 'FAIL'}")
    print(f"P1: {'PASS' if all(r['status'] == 'PASS' for r in results if r['priority'] == 'P1') else 'FAIL'}")
    print(f"P2: {'PASS' if all(r['status'] == 'PASS' for r in results if r['priority'] == 'P2') else 'FAIL'}")
    print(f"P3: {'PASS' if all(r['status'] == 'PASS' for r in results if r['priority'] == 'P3') else 'FAIL'}")

    # Write JSON report
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "overall": overall,
        "results": results,
    }
    report_path = os.path.join(ROOT, "redteam_regression_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written to: {report_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
