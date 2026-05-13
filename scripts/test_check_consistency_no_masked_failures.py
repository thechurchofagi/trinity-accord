#!/usr/bin/env python3
"""
Verify check_consistency.py does not mask child FAIL outputs.
Any non-legacy child check that prints FAIL must cause overall FAIL.

Usage:
    python3 scripts/test_check_consistency_no_masked_failures.py
"""
import json
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ok = True

    # 1. Run check_consistency.py and verify it passes
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_consistency.py")],
        cwd=ROOT, text=True, capture_output=True, timeout=180
    )
    combined = (proc.stdout or "") + (proc.stderr or "")

    # 2. Check that no FAIL appears in output without overall FAILURE
    has_fail_in_output = False
    fail_lines = []
    for line in combined.splitlines():
        line_stripped = line.strip()
        # Skip INFO lines and expected-fail patterns
        if line_stripped.startswith("INFO:") or line_stripped.startswith("SKIP"):
            continue
        if "FAIL" in line_stripped and "ALL CHECKS PASSED" not in line_stripped:
            # Check if it's a check() output (starts with "FAIL:")
            if line_stripped.startswith("FAIL:"):
                has_fail_in_output = True
                fail_lines.append(line_stripped)

    # 3. If there are FAIL lines in check() output, overall must fail
    if has_fail_in_output:
        if proc.returncode == 0:
            print(f"FAIL: check_consistency.py has masked failures:")
            for fl in fail_lines:
                print(f"      {fl}")
            print(f"      But overall returned exit code 0")
            ok = False
        else:
            print(f"PASS: check_consistency.py correctly fails when child checks fail")
    else:
        if proc.returncode == 0:
            print(f"PASS: check_consistency.py passes with no child failures")
        else:
            print(f"FAIL: check_consistency.py fails but no FAIL lines found in output")
            ok = False

    # 4. Verify the check() function signature is correct (label, condition, detail)
    check_src = (ROOT / "scripts" / "check_consistency.py").read_text()
    # Verify no swapped arguments pattern: check(proc.returncode == 0, "label")
    import re
    swapped = re.findall(r'check\(\w+\.returncode\s*==\s*0\s*,\s*"', check_src)
    if swapped:
        print(f"FAIL: check_consistency.py has swapped check() arguments:")
        for s in swapped:
            print(f"      {s}")
        ok = False
    else:
        print(f"PASS: check_consistency.py check() arguments are correctly ordered")

    print(f"\n{'='*60}")
    if ok:
        print("FINAL: PASS — no masked failures detected.")
    else:
        print("FINAL: FAIL — masked failures detected.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
