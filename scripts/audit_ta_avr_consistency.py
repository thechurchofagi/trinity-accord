#!/usr/bin/env python3
"""
TA-AVR Meta-Audit: Unified Entry Point
Run all TA-AVR consistency audits with machine-readable JSON output.

Usage:
    python3 scripts/audit_ta_avr_consistency.py --all
    python3 scripts/audit_ta_avr_consistency.py --quick
    python3 scripts/audit_ta_avr_consistency.py --all --output audit-results/ta-avr-meta-audit.json

Exit codes:
    0 = all selected checks pass
    1 = one or more checks fail
    2 = invalid arguments
    3 = internal audit error
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALL_CHECKS = [
    "test_ta_avr_reference_integrity.py",
    "test_ta_avr_schema_cross_consistency.py",
    "test_ta_avr_data_consistency.py",
    "test_ta_avr_cli_doc_consistency.py",
    "test_ta_avr_output_consistency.py",
    "test_ta_avr_negative_overclaim_matrix.py",
    "test_ta_avr_secret_hygiene.py",
    "test_ta_avr_report_consistency.py",
]

QUICK_CHECKS = [
    "test_ta_avr_reference_integrity.py",
    "test_ta_avr_schema_cross_consistency.py",
    "test_ta_avr_negative_overclaim_matrix.py",
    "test_ta_avr_secret_hygiene.py",
]

CHECK_KEYS = {
    "test_ta_avr_reference_integrity.py": "reference_integrity",
    "test_ta_avr_schema_cross_consistency.py": "schema_cross_consistency",
    "test_ta_avr_data_consistency.py": "data_consistency",
    "test_ta_avr_cli_doc_consistency.py": "cli_doc_consistency",
    "test_ta_avr_output_consistency.py": "output_consistency",
    "test_ta_avr_negative_overclaim_matrix.py": "negative_overclaim_matrix",
    "test_ta_avr_secret_hygiene.py": "secret_hygiene",
    "test_ta_avr_report_consistency.py": "report_consistency",
}


def run_check(script_name):
    """Run a check script and return (status, output)."""
    script_path = ROOT / "scripts" / script_name
    if not script_path.exists():
        return "SKIP", f"script not found: {script_name}"

    try:
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True, text=True, timeout=300, cwd=str(ROOT)
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            return "PASS", output
        else:
            return "FAIL", output
    except subprocess.TimeoutExpired:
        return "FAIL", "timeout after 300s"
    except Exception as e:
        return "ERROR", str(e)


def main():
    parser = argparse.ArgumentParser(description="TA-AVR Meta-Audit")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Run all checks")
    group.add_argument("--quick", action="store_true", help="Run quick checks only")
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument("--test-root", help="Test root for report consistency")
    parser.add_argument("--report", help="Report path for report consistency")
    args = parser.parse_args()

    checks_to_run = ALL_CHECKS if args.all else QUICK_CHECKS

    print(f"TA-AVR Meta-Audit — {'all' if args.all else 'quick'} mode")
    print(f"Running {len(checks_to_run)} checks...\n")

    results = {}
    failures = []
    errors = []

    for script in checks_to_run:
        key = CHECK_KEYS.get(script, script)
        print(f"--- {key} ---")
        status, output = run_check(script)
        results[key] = status

        # Print last few lines of output
        lines = output.strip().split("\n")
        for line in lines[-5:]:
            print(f"  {line}")
        print()

        if status == "FAIL":
            failures.append(key)
        elif status == "ERROR":
            errors.append(key)

    # Determine overall result
    overall = "PASS" if not failures and not errors else "FAIL"

    # Build summary JSON
    summary = {
        "schema": "trinityaccord.ta-avr-meta-audit.v1",
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": "",
        "result": overall,
        "checks": results,
        "failures": failures,
        "errors": errors,
        "does_not_prove": [
            "philosophical truth",
            "formal attestation",
            "physical verification",
            "full-chain verification",
        ],
    }

    # Get git commit
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, cwd=str(ROOT)
        )
        summary["git_commit"] = result.stdout.strip()
    except Exception:
        pass

    # Output JSON
    json_str = json.dumps(summary, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json_str)
        print(f"\nResults written to: {args.output}")
    else:
        print(f"\n{json_str}")

    # Final summary
    print(f"\n{'=' * 50}")
    print(f"RESULT: {overall}")
    if failures:
        print(f"FAILURES: {', '.join(failures)}")
    if errors:
        print(f"ERRORS: {', '.join(errors)}")

    sys.exit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
