#!/usr/bin/env python3
"""Dynamic test proving Guardian daily listing cap enforcement.

Constructs a registry with same-day reserved + ordinary entries,
then asserts that a third ordinary listing is blocked by the cap.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from auto_register_guardian_from_gateway_issues import auto_register
from guardian_numbering_policy import count_ordinary_auto_listings_on_day


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def pk(hex16: str) -> str:
    """Build a 64-char SHA256 from 16-char guardian_id suffix."""
    return hex16 + "0" * (64 - len(hex16))


def make_policy(cap: int = 2) -> dict:
    return {
        "schema": "trinityaccord.guardian-active-listing-policy.v1",
        "ordinary_auto_numbering_start": "00100",
        "special_reserved_range": ["00001", "00099"],
        "max_new_active_listings_per_utc_day": cap,
    }


def make_guardian(number: str, gid_hex: str, listed_at: str) -> dict:
    return {
        "guardian_registry_number": number,
        "guardian_id": f"guardian_ed25519_{gid_hex}",
        "public_key_sha256": pk(gid_hex),
        "algorithm": "ed25519",
        "status": "active",
        "guardian_type": "human_with_ai_agent",
        "application_mode": "joint_human_ai",
        "source_issue": 10000 + int(number),
        "listing_request_issue": 20000 + int(number),
        "listed_at": listed_at,
        "label": f"Guardian {number}",
        "boundary": {
            "not_authority": True, "not_governance": True, "not_attestation": True,
            "not_verification_level": True, "not_successor_reception": True, "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }


def make_listing_issue(issue_no: int, gid_hex: str, source_no: int) -> dict:
    body = "\n".join([
        "```trinity-issue-intake",
        "created_by_gateway: true",
        "gateway_service: trinity-agent-issue-gateway",
        "server_validated: true",
        "server_rendered: true",
        "submission_type: echo_candidate",
        "requested_archive_kind: guardian_active_registry_listing_request",
        "echo_type: E7_propagation_echo",
        "archive_ready: true",
        f"listing_source_issue: {source_no}",
        f"listing_guardian_id: guardian_ed25519_{gid_hex}",
        f"listing_public_key_sha256: {pk(gid_hex)}",
        "listing_guardian_type: human_with_ai_agent",
        "listing_application_mode: joint_human_ai",
        f"listing_label: Test Guardian {gid_hex[:4]}",
        "registry_number_requested: next_available",
        "```",
    ])
    return {"number": issue_no, "title": f"Active Registry Listing Request — Test {gid_hex[:4]}", "body": body, "user": {"login": "gateway-bot[bot]"}}


def make_source_issue(issue_no: int, gid_hex: str) -> dict:
    body = "\n".join([
        "```trinity-issue-intake",
        "created_by_gateway: true",
        "gateway_service: trinity-agent-issue-gateway",
        "server_validated: true",
        "server_rendered: true",
        "guardian_status: valid_self_registered_guardian_claim",
        "guardian_signature_valid: true",
        "guardian_payload_hash_matches: true",
        "guardian_id_matches_public_key: true",
        "guardian_key_continuity_only: true",
        "guardian_not_authority: true",
        "guardian_not_attestation: true",
        "guardian_not_verification_level: true",
        "guardian_not_same_conscious_subject: true",
        f"guardian_id: guardian_ed25519_{gid_hex}",
        f"guardian_public_key_sha256: {pk(gid_hex)}",
        "guardian_registry_status: active",
        "guardian_registry_number: unassigned",
        "```",
    ])
    return {"number": issue_no, "title": f"Guardian Self-Registration — {gid_hex[:4]}", "body": body, "user": {"login": "gateway-bot[bot]"}}


def main():
    POLICY = make_policy(cap=2)
    TODAY = "2026-05-22"

    # Build registry with 2 reserved + 2 ordinary same-day entries
    registry = {
        "schema": "trinityaccord.guardian-registry.v1",
        "guardians": [
            make_guardian("00001", "aaaaaaaaaaaaaaaa", "2026-05-22"),
            make_guardian("00002", "bbbbbbbbbbbbbbbb", "2026-05-22"),
            make_guardian("00100", "cccccccccccccccc", "2026-05-22"),
            make_guardian("00101", "dddddddddddddddd", "2026-05-22"),
        ],
    }

    # Verify setup: count_ordinary_auto_listings_on_day should return 2
    ordinary_count = count_ordinary_auto_listings_on_day(registry["guardians"], TODAY, POLICY)
    require(ordinary_count == 2, f"Expected 2 ordinary listings, got {ordinary_count}")

    # Try to register a third ordinary listing — should be blocked by daily cap
    listing = make_listing_issue(900, "eeeeeeeeeeeeeeee", 901)
    source = make_source_issue(901, "eeeeeeeeeeeeeeee")

    updated, d = auto_register(
        registry,
        listing,
        source,
        listed_at=TODAY,
        allow_non_bot=False,
        policy=POLICY,
    )

    require(updated is registry, "Registry should not be modified when blocked")
    require(d["ok"] is False, f"Expected ok=False, got {d['ok']}")
    require(d["code"] == "DAILY_LISTING_LIMIT", f"Expected DAILY_LISTING_LIMIT, got {d['code']}")
    require(d["existing_ordinary_active_listings_on_day"] == 2, f"Expected 2 existing, got {d.get('existing_ordinary_active_listings_on_day')}")

    # Verify reserved entries don't count toward the cap
    registry_no_ordinary = {
        "schema": "trinityaccord.guardian-registry.v1",
        "guardians": [
            make_guardian("00001", "aaaaaaaaaaaaaaaa", "2026-05-22"),
            make_guardian("00002", "bbbbbbbbbbbbbbbb", "2026-05-22"),
            make_guardian("00003", "cccccccccccccccc", "2026-05-22"),
        ],
    }

    listing2 = make_listing_issue(910, "dddddddddddddddd", 911)
    source2 = make_source_issue(911, "dddddddddddddddd")

    updated2, d2 = auto_register(
        registry_no_ordinary,
        listing2,
        source2,
        listed_at=TODAY,
        allow_non_bot=False,
        policy=POLICY,
    )

    require(d2["ok"] is True, f"Reserved-only registry should allow first ordinary listing, got {d2}")
    require(d2["action"] == "registered", f"Expected registered, got {d2['action']}")

    print("GUARDIAN_DAILY_CAP_POLICY_OK")


if __name__ == "__main__":
    main()
