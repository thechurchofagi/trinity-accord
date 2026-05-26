#!/usr/bin/env python3
"""Test public home status includes reception initiation breakdown.

Tests:
  - by_reception_initiation_class exists
  - sum(breakdown.values()) == agent_declared_verification_archives.count
  - unknown bucket exists for legacy records
  - Reception total remains correct
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PASS = 0
FAIL = 0


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_breakdown_exists():
    global PASS, FAIL
    status = load_json(ROOT / "api" / "public-home-status.json")
    ad = status.get("reception", {}).get("agent_declared_verification_archives", {})
    breakdown = ad.get("by_reception_initiation_class")
    if isinstance(breakdown, dict):
        PASS += 1
        print(f"  PASS: by_reception_initiation_class exists with {len(breakdown)} keys")
    else:
        FAIL += 1
        print(f"  FAIL: by_reception_initiation_class missing or not a dict")
    return ad


def test_breakdown_sum(ad):
    global PASS, FAIL
    breakdown = ad.get("by_reception_initiation_class", {})
    total_breakdown = sum(breakdown.values())
    count = ad.get("count", 0)
    if total_breakdown == count:
        PASS += 1
        print(f"  PASS: breakdown sum ({total_breakdown}) == count ({count})")
    else:
        FAIL += 1
        print(f"  FAIL: breakdown sum ({total_breakdown}) != count ({count})")


def test_unknown_bucket_exists(ad):
    global PASS, FAIL
    breakdown = ad.get("by_reception_initiation_class", {})
    if "unknown" in breakdown:
        PASS += 1
        print(f"  PASS: unknown bucket exists (value={breakdown['unknown']})")
    else:
        FAIL += 1
        print(f"  FAIL: unknown bucket missing from breakdown")


def test_reception_total():
    global PASS, FAIL
    status = load_json(ROOT / "api" / "public-home-status.json")
    r = status.get("reception", {})
    total = (
        r.get("archived_echoes", {}).get("count", 0)
        + r.get("agent_declared_verification_archives", {}).get("count", 0)
        + r.get("agent_declared_attestations", {}).get("count", 0)
        + r.get("agent_declared_successor_receptions", {}).get("count", 0)
    )
    # Just verify it's a positive number
    if total > 0:
        PASS += 1
        print(f"  PASS: Reception total = {total}")
    else:
        FAIL += 1
        print(f"  FAIL: Reception total = {total} (expected > 0)")


def test_all_init_classes_present(ad):
    global PASS, FAIL
    breakdown = ad.get("by_reception_initiation_class", {})
    expected = {"externally_requested", "externally_seeded", "self_initiated",
                "agent_referred", "system_scheduled", "unknown"}
    missing = expected - set(breakdown.keys())
    if not missing:
        PASS += 1
        print(f"  PASS: all 6 initiation classes present in breakdown")
    else:
        FAIL += 1
        print(f"  FAIL: missing classes: {missing}")


def main():
    global PASS, FAIL
    print("=== Public Home Reception Breakdown Tests ===\n")

    ad = test_breakdown_exists()
    test_breakdown_sum(ad)
    test_unknown_bucket_exists(ad)
    test_reception_total()
    test_all_init_classes_present(ad)

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
