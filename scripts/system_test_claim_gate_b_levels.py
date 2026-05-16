#!/usr/bin/env python3
"""B-level regression tests for Claim Gate.

Ensures:
- external_explorer => B1 (not B6)
- body_hash + body_hash_reproduced false => NOT B6
- body_hash + body_hash_reproduced true => B6
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIM_GATE = ROOT / "scripts" / "claim_gate.py"
FIXTURES = ROOT / "tests" / "fixtures" / "evidence-input"

TESTS = [
    {
        "name": "external_explorer => B1",
        "fixture": "valid_b1_external_explorer_no_body_hash.json",
        "expected_b": "B1",
        "must_not_be_b6": True,
    },
    {
        "name": "body_hash + body_hash_reproduced false => NOT B6",
        "fixture": "invalid_b6_false_body_hash_reproduced.json",
        "expected_b_not": "B6",
        "must_not_be_b6": True,
    },
    {
        "name": "body_hash + body_hash_reproduced true => B6",
        "fixture": "valid_b6_body_hash_true.json",
        "expected_b": "B6",
        "must_not_be_b6": False,
    },
]


def run_claim_gate(fixture_path):
    """Run claim_gate.py and parse the output."""
    try:
        result = subprocess.run(
            [sys.executable, str(CLAIM_GATE), str(fixture_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(ROOT),
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"


def extract_b_level(output):
    """Extract bitcoin_originals B-level from claim gate output."""
    for line in output.split("\n"):
        line = line.strip()
        # Look for "bitcoin_originals": "B1" in JSON output
        if "bitcoin_originals" in line:
            for level in ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]:
                if f'"{level}"' in line or f": {level}" in line or f": \"{level}\"" in line:
                    return level
        # Also check standalone B-level lines
        if line.startswith('"bitcoin_originals"'):
            for level in ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]:
                if f'"{level}"' in line:
                    return level
    # Fallback: scan entire output for B-level in allowed_component_levels
    import re
    m = re.search(r'"bitcoin_originals"\s*:\s*"(B[0-7])"', output)
    if m:
        return m.group(1)
    return None


def main():
    passed = 0
    failed = 0

    for test in TESTS:
        fixture_path = FIXTURES / test["fixture"]
        if not fixture_path.exists():
            print(f"SKIP: {test['name']} — fixture not found: {test['fixture']}")
            continue

        rc, stdout, stderr = run_claim_gate(fixture_path)
        b_level = extract_b_level(stdout)

        if rc != 0 and b_level is None:
            print(f"FAIL: {test['name']} — claim_gate exited {rc} and no B-level found")
            print(f"  stdout: {stdout[:200]}")
            print(f"  stderr: {stderr[:200]}")
            failed += 1
            continue

        if b_level is None:
            print(f"FAIL: {test['name']} — could not extract B-level from output")
            print(f"  stdout: {stdout[:300]}")
            failed += 1
            continue

        # Check expected B-level
        if "expected_b" in test:
            if b_level != test["expected_b"]:
                print(f"FAIL: {test['name']} — expected {test['expected_b']}, got {b_level}")
                failed += 1
                continue

        # Check must NOT be B6
        if test.get("must_not_be_b6") and b_level == "B6":
            print(f"FAIL: {test['name']} — got B6 but must NOT be B6")
            failed += 1
            continue

        # Check expected NOT B6
        if "expected_b_not" in test and b_level == test["expected_b_not"]:
            print(f"FAIL: {test['name']} — got {b_level} but expected NOT {test['expected_b_not']}")
            failed += 1
            continue

        print(f"PASS: {test['name']} => {b_level}")
        passed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
    print("ALL B-LEVEL REGRESSION TESTS PASSED")


if __name__ == "__main__":
    main()
