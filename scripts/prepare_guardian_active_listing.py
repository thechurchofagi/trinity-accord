#!/usr/bin/env python3
"""Prepare a Guardian active registry listing from a valid self-registered Guardian payload.

This writes an updated guardian-registry.json to --out-registry.
It does not push, merge, or touch private keys.
"""

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_guardian_status import verify_guardian_status


def fail(error_code, message, details=None, exit_code=2):
    print(json.dumps({
        "ok": False,
        "error_code": error_code,
        "message": message,
        "details": details or {},
    }, indent=2, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(exit_code)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def positive_issue(value, name):
    try:
        n = int(value)
    except Exception:
        fail("E_BAD_ISSUE_NUMBER", f"{name} must be a positive integer", {name: value})
    if n <= 0:
        fail("E_BAD_ISSUE_NUMBER", f"{name} must be a positive integer", {name: value})
    return n


def parse_date(value):
    if value:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            fail("E_BAD_LISTED_AT", "--listed-at must be YYYY-MM-DD", {"listed_at": value})
        return value
    return datetime.now(timezone.utc).date().isoformat()


def next_registry_number(guardians):
    numbers = []
    for entry in guardians:
        number = entry.get("guardian_registry_number")
        if not isinstance(number, str) or not re.fullmatch(r"[0-9]{5}", number):
            fail("E_BAD_EXISTING_REGISTRY_NUMBER", "Existing registry number is invalid", {"entry": entry})
        numbers.append(int(number))

    if not numbers:
        return "00001"

    got = sorted(numbers)
    expected = list(range(1, max(got) + 1))
    if got != expected:
        fail("E_REGISTRY_NUMBER_GAP", "Existing registry numbers have gaps", {
            "got": got,
            "expected": expected,
        })

    return f"{max(got) + 1:05d}"


def existing_by(guardians, key, value):
    return [g for g in guardians if g.get(key) == value]


def count_listings_on_day(guardians, listed_at):
    return sum(1 for g in guardians if g.get("listed_at") == listed_at and g.get("status") == "active")


def main():
    parser = argparse.ArgumentParser(description="Prepare Guardian active listing registry update.")
    parser.add_argument("--payload", required=True)
    parser.add_argument("--registry", default=str(ROOT / "api" / "guardian-registry.json"))
    parser.add_argument("--policy", default=str(ROOT / "api" / "guardian-active-listing-policy.v1.json"))
    parser.add_argument("--source-issue", required=True)
    parser.add_argument("--listing-request-issue", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--listed-at", default=None)
    parser.add_argument("--out-registry", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    source_issue = positive_issue(args.source_issue, "source_issue")
    listing_request_issue = positive_issue(args.listing_request_issue, "listing_request_issue")
    listed_at = parse_date(args.listed_at)

    payload = load_json(args.payload)
    registry = load_json(args.registry)
    policy = load_json(args.policy)

    if policy.get("automation_mode") != "create_pr_only":
        fail("E_UNSUPPORTED_AUTOMATION_MODE", "Policy automation_mode must be create_pr_only")

    guardians = registry.get("guardians")
    if not isinstance(guardians, list):
        fail("E_BAD_REGISTRY", "guardian-registry.json must contain guardians array")

    verification = verify_guardian_status(payload, args.registry)
    status = verification.get("guardian_status")
    guardian_id = verification.get("guardian_id")

    if status == "active_registered_guardian":
        print(json.dumps({
            "ok": True,
            "changed": False,
            "reason": "already_active",
            "guardian_id": guardian_id,
            "guardian_registry_number": verification.get("guardian_registry_number"),
        }, indent=2, ensure_ascii=False))
        return

    if status != "valid_self_registered_guardian_claim":
        fail("E_NOT_VALID_SELF_REGISTERED_CLAIM", "Payload must verify as valid_self_registered_guardian_claim", {
            "guardian_status": status,
            "verification": verification,
        })

    proof = payload.get("guardian_presence_proof") or {}
    registration = payload.get("guardian_registration") or {}
    public_key_sha256 = proof.get("public_key_sha256")

    if not isinstance(guardian_id, str) or not guardian_id.startswith("guardian_ed25519_"):
        fail("E_BAD_GUARDIAN_ID", "guardian_id from proof is invalid", {"guardian_id": guardian_id})

    if not isinstance(public_key_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", public_key_sha256):
        fail("E_BAD_PUBLIC_KEY_SHA256", "public_key_sha256 from proof is invalid", {
            "public_key_sha256": public_key_sha256
        })

    if existing_by(guardians, "guardian_id", guardian_id):
        fail("E_DUPLICATE_GUARDIAN_ID", "guardian_id already exists in registry", {"guardian_id": guardian_id})

    if existing_by(guardians, "public_key_sha256", public_key_sha256):
        fail("E_DUPLICATE_PUBLIC_KEY_SHA256", "public_key_sha256 already exists in registry", {
            "public_key_sha256": public_key_sha256
        })

    if existing_by(guardians, "source_issue", source_issue):
        fail("E_DUPLICATE_SOURCE_ISSUE", "source_issue already used", {"source_issue": source_issue})

    if existing_by(guardians, "listing_request_issue", listing_request_issue):
        fail("E_DUPLICATE_LISTING_REQUEST_ISSUE", "listing_request_issue already used", {
            "listing_request_issue": listing_request_issue
        })

    max_per_run = int(policy.get("max_new_active_listings_per_run", 1))
    if max_per_run != 1:
        fail("E_BAD_POLICY", "This script supports exactly one new listing per run", {
            "max_new_active_listings_per_run": max_per_run
        })

    max_per_day = int(policy.get("max_new_active_listings_per_utc_day", 3))
    if max_per_day < 1:
        fail("E_BAD_POLICY", "max_new_active_listings_per_utc_day must be >= 1")

    today_count = count_listings_on_day(guardians, listed_at)
    if today_count >= max_per_day:
        fail("E_DAILY_LISTING_LIMIT", "Daily active Guardian listing limit reached", {
            "listed_at": listed_at,
            "existing_active_listings_on_day": today_count,
            "max_new_active_listings_per_utc_day": max_per_day,
        })

    number = next_registry_number(guardians)

    new_entry = {
        "guardian_registry_number": number,
        "guardian_id": guardian_id,
        "public_key_sha256": public_key_sha256,
        "algorithm": "ed25519",
        "status": "active",
        "guardian_type": registration.get("guardian_type", "unknown"),
        "application_mode": registration.get("application_mode", "unknown"),
        "source_issue": source_issue,
        "listing_request_issue": listing_request_issue,
        "listed_at": listed_at,
        "label": args.label,
        "boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_verification_level": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True
        }
    }

    updated = deepcopy(registry)
    updated.setdefault("guardians", []).append(new_entry)

    write_json(args.out_registry, updated)

    print(json.dumps({
        "ok": True,
        "changed": True,
        "out_registry": args.out_registry,
        "guardian_registry_number": number,
        "guardian_id": guardian_id,
        "public_key_sha256": public_key_sha256,
        "source_issue": source_issue,
        "listing_request_issue": listing_request_issue,
        "listed_at": listed_at,
        "next_steps": [
            "Run scripts/test_guardian_registry_numbers.py",
            "Run verify_guardian_status.py against the payload and updated registry",
            "Open a PR for api/guardian-registry.json",
            "Do not commit private keys"
        ]
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
