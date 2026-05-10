#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR5: Echo index includes AI verification aggregation counts.

Verifies that the echo index generation script:
1. Includes record_class and verification_origin_class in records
2. Produces records_by_record_class aggregation
3. Produces records_by_verification_origin_class aggregation
4. Includes AI verification boundary notes
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test(label, passed):
    if passed:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label}")
    return passed


def main():
    passed = 0
    failed = 0

    # ── Test 1: Generate echo index and check output ──
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_echo_index.py")],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    if result.returncode != 0:
        print(f"  FAIL: generate_echo_index.py failed: {result.stderr}")
        return 1

    index_path = ROOT / "api" / "echo-index.json"
    if not index_path.exists():
        print("  FAIL: echo-index.json not generated")
        return 1

    index = json.loads(index_path.read_text(encoding="utf-8"))

    # ── Test 2: Records have record_class field ──
    records = index.get("records", [])
    has_record_class = all("record_class" in r for r in records)
    if test("All records have record_class field", has_record_class):
        passed += 1
    else:
        failed += 1

    # ── Test 3: Records have verification_origin_class field ──
    has_origin_class = all("verification_origin_class" in r for r in records)
    if test("All records have verification_origin_class field", has_origin_class):
        passed += 1
    else:
        failed += 1

    # ── Test 4: records_by_record_class aggregation exists ──
    has_record_class_agg = "records_by_record_class" in index
    if test("records_by_record_class aggregation exists", has_record_class_agg):
        passed += 1
    else:
        failed += 1

    # ── Test 5: records_by_verification_origin_class aggregation exists ──
    has_origin_agg = "records_by_verification_origin_class" in index
    if test("records_by_verification_origin_class aggregation exists", has_origin_agg):
        passed += 1
    else:
        failed += 1

    # ── Test 6: Notes include AI verification boundary ──
    notes = index.get("notes", [])
    has_ai_note = any("AI independent verification" in n for n in notes)
    if test("Notes include AI verification boundary", has_ai_note):
        passed += 1
    else:
        failed += 1

    # ── Test 7: Notes include external human authorization boundary ──
    has_auth_note = any("External human authorization" in n for n in notes)
    if test("Notes include external human authorization boundary", has_auth_note):
        passed += 1
    else:
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
