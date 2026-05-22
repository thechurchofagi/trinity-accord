#!/usr/bin/env python3
"""Test ordinary Guardian daily listing cap is enforced consistently."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    auto_reg = (ROOT / "scripts" / "auto_register_guardian_from_gateway_issues.py").read_text(encoding="utf-8")
    prepare = (ROOT / "scripts" / "prepare_guardian_active_listing.py").read_text(encoding="utf-8")

    # Both paths must use the shared daily cap helper
    require("count_ordinary_auto_listings_on_day" in auto_reg, "auto_register missing count_ordinary_auto_listings_on_day import")
    require("count_ordinary_auto_listings_on_day" in prepare, "prepare_guardian missing count_ordinary_auto_listings_on_day import")

    # Both must check DAILY_LISTING_LIMIT
    require("DAILY_LISTING_LIMIT" in auto_reg, "auto_register missing DAILY_LISTING_LIMIT")
    require("E_DAILY_LISTING_LIMIT" in prepare, "prepare_guardian missing E_DAILY_LISTING_LIMIT")

    # Policy file must exist
    policy_path = ROOT / "api" / "guardian-active-listing-policy.v1.json"
    require(policy_path.exists(), "guardian-active-listing-policy.v1.json must exist")

    import json
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    require("max_new_active_listings_per_utc_day" in policy, "policy missing max_new_active_listings_per_utc_day")
    require(policy["max_new_active_listings_per_utc_day"] >= 1, "daily cap must be >= 1")

    print("GUARDIAN_DAILY_CAP_POLICY_OK")


if __name__ == "__main__":
    main()
