#!/usr/bin/env python3
"""Test Guardian daily cap configuration."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_policy_daily_cap():
    policy = json.loads((ROOT / "api" / "guardian-active-listing-policy.v1.json").read_text())
    assert policy["max_new_active_listings_per_utc_day"] == 100, (
        f"Expected daily cap 100, got {policy['max_new_active_listings_per_utc_day']}"
    )
    assert policy["max_new_active_listings_per_run"] == 20, (
        f"Expected per-run cap 20, got {policy['max_new_active_listings_per_run']}"
    )
    print("PASS: test_policy_daily_cap")


def test_auto_register_fallback_cap():
    """Verify the auto-registration script fallback daily cap is 100."""
    src = (ROOT / "scripts" / "auto_register_guardian_from_gateway_issues.py").read_text()
    assert "max_new_active_listings_per_utc_day\", 100)" in src, (
        "auto_register fallback daily cap should be 100"
    )
    print("PASS: test_auto_register_fallback_cap")


if __name__ == "__main__":
    test_policy_daily_cap()
    test_auto_register_fallback_cap()
