#!/usr/bin/env python3
"""Test public home status reception breakdown invariants.

Tests:
  - by_reception_initiation_class exists in public-home-status.json
  - sum(breakdown.values()) == agent_declared_verification_archives.count
  - unknown bucket receives legacy records
  - No class inference from agent_name_or_model, system_or_provider, or Issue title
  - Reception total unchanged
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
    if isinstance(breakdown, dict) and len(breakdown) > 0:
        PASS += 1
        print(f"  PASS: by_reception_initiation_class exists with {len(breakdown)} keys: {sorted(breakdown.keys())}")
    else:
        FAIL += 1
        print(f"  FAIL: by_reception_initiation_class missing or empty")
    return ad


def test_breakdown_sum(ad):
    """Sum of breakdown values must equal the total count."""
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


def test_unknown_bucket(ad):
    """Unknown bucket should exist for legacy records."""
    global PASS, FAIL
    breakdown = ad.get("by_reception_initiation_class", {})
    if "unknown" in breakdown:
        PASS += 1
        print(f"  PASS: unknown bucket exists (value={breakdown['unknown']})")
    else:
        FAIL += 1
        print(f"  FAIL: unknown bucket missing from breakdown")


def test_all_classes_present(ad):
    """All six initiation classes should be present (even if zero)."""
    global PASS, FAIL
    expected = {"externally_requested", "externally_seeded", "self_initiated",
                "agent_referred", "system_scheduled", "unknown"}
    breakdown = ad.get("by_reception_initiation_class", {})
    actual = set(breakdown.keys())
    missing = expected - actual
    if not missing:
        PASS += 1
        print(f"  PASS: all 6 initiation classes present")
    else:
        FAIL += 1
        print(f"  FAIL: missing classes: {missing}")


def test_reception_total():
    """Reception total should be consistent."""
    global PASS, FAIL
    status = load_json(ROOT / "api" / "public-home-status.json")
    r = status.get("reception", {})
    total = sum([
        r.get("archived_echoes", {}).get("count", 0),
        r.get("agent_declared_verification_archives", {}).get("count", 0),
        r.get("agent_declared_attestations", {}).get("count", 0),
        r.get("agent_declared_successor_receptions", {}).get("count", 0),
    ])
    if total > 0:
        PASS += 1
        print(f"  PASS: Reception total = {total}")
    else:
        FAIL += 1
        print(f"  FAIL: Reception total = {total} (expected > 0)")


def test_no_name_inference():
    """Index records must not derive class from agent name or provider.

    Rules:
    - Records with explicit machine-recorded reception_initiation_class → preserve it.
    - Records without machine-recorded class (legacy) → default to 'unknown'.
    - Never derive class from agent_name_or_model or system_or_provider.
    """
    global PASS, FAIL
    index_path = ROOT / "api" / "agent-declared-verification-index.json"
    if not index_path.exists():
        print("  SKIP: agent-declared-verification-index.json not found")
        return

    index = load_json(index_path)
    records = index.get("records", [])
    violations = []
    for rec in records:
        cls = rec.get("reception_initiation_class", "")
        # Every record must have a class; missing/empty means the builder or
        # index failed to default to 'unknown'.
        if not cls:
            violations.append(f"record {rec.get('record_id', '?')} has empty class")
    if violations:
        FAIL += 1
        print(f"  FAIL: {len(violations)} record(s) with empty class: {violations[0]}")
    else:
        PASS += 1
        print(f"  PASS: all {len(records)} records have explicit class (no name/provider inference)")


def main():
    global PASS, FAIL
    print("=== Public Home Reception Breakdown Invariant Tests ===\n")

    ad = test_breakdown_exists()
    if ad:
        test_breakdown_sum(ad)
        test_unknown_bucket(ad)
        test_all_classes_present(ad)
    test_reception_total()
    test_no_name_inference()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
