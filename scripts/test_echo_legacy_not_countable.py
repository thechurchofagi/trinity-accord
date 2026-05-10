#!/usr/bin/env python3
"""Test Echo legacy records are not countable (TA-REDTEAM-2026-012).

Verifies that legacy records in the echo index have the correct lifecycle fields.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    passed = 0
    failed = 0

    echo_index_path = ROOT / "api" / "echo-index.json"
    if not echo_index_path.exists():
        print("  FAIL: echo-index.json not found")
        return 1

    data = json.loads(echo_index_path.read_text(encoding="utf-8"))
    records = data.get("records", [])

    # Find legacy records
    legacy_records = [r for r in records if r.get("record_kind") == "legacy_record"]
    superseded_records = [r for r in records if r.get("archive_status") == "superseded"]

    # 1. Legacy records have do_not_count_as_attestation=true
    for r in legacy_records:
        if r.get("do_not_count_as_attestation") is True:
            passed += 1
            print(f"  PASS: {r['id']} has do_not_count_as_attestation=true")
        else:
            failed += 1
            print(f"  FAIL: {r['id']} missing do_not_count_as_attestation=true")

    # 2. Legacy records have historical_record_only=true
    for r in legacy_records:
        if r.get("historical_record_only") is True:
            passed += 1
            print(f"  PASS: {r['id']} has historical_record_only=true")
        else:
            failed += 1
            print(f"  FAIL: {r['id']} missing historical_record_only=true")

    # 3. Superseded records have superseded_reason
    for r in superseded_records:
        if r.get("superseded_reason"):
            passed += 1
            print(f"  PASS: {r['id']} has superseded_reason")
        else:
            failed += 1
            print(f"  FAIL: {r['id']} missing superseded_reason")

    # 4. Superseded records have superseded_by or successor_status
    for r in superseded_records:
        if r.get("superseded_by") is not None or r.get("successor_status"):
            passed += 1
            print(f"  PASS: {r['id']} has superseded_by or successor_status")
        else:
            failed += 1
            print(f"  FAIL: {r['id']} missing superseded_by or successor_status")

    # 5. Superseded records have historical_record_only=true
    for r in superseded_records:
        if r.get("historical_record_only") is True:
            passed += 1
            print(f"  PASS: {r['id']} has historical_record_only=true")
        else:
            failed += 1
            print(f"  FAIL: {r['id']} missing historical_record_only=true")

    print(f"\n{'=' * 50}")
    print(f"test_echo_legacy_not_countable: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
