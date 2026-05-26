#!/usr/bin/env python3
"""Test that validator scripts work from both repo root and scripts/ directory."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def main():
    ok = True

    scripts_to_test = [
        "scripts/check_consistency.py",
        "scripts/verify_link_hygiene.py",
        "scripts/validate_echo_records.py",
        "scripts/verify_echo_index_completeness.py",
        "scripts/validate_agent_submission.py",
    ]

    for script in scripts_to_test:
        script_path = ROOT / script
        if not script_path.exists():
            print(f"SKIP: {script} not found")
            continue

        # Test from repo root
        proc_root = subprocess.run(
            [sys.executable, script],
            cwd=ROOT, text=True, capture_output=True, timeout=60
        )
        ok &= check(
            proc_root.returncode in (0, 1),
            f"{script} runs from repo root (exit {proc_root.returncode})"
        )

        # Test from scripts directory
        proc_scripts = subprocess.run(
            [sys.executable, Path(script).name],
            cwd=ROOT / "scripts", text=True, capture_output=True, timeout=60
        )
        ok &= check(
            proc_scripts.returncode in (0, 1),
            f"{script} runs from scripts/ (exit {proc_scripts.returncode})"
        )

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — validator cwd independence tests passed.")
        return 0
    print("FINAL: FAIL — validator cwd independence tests failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
