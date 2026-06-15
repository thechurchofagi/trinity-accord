#!/usr/bin/env python3
"""Contract test: guardian_key_rotation is reserved in Gateway validation."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))

from gateway.validation import (
    ALLOWED_RECORD_TYPES,
    RESERVED_RECORD_TYPES,
    detect_route,
    validate_submission,
)


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def minimal_reserved_submission():
    return {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "record_type": "guardian_key_rotation",
        "record_draft": {
            "schema": "trinityaccord.record-chain-entry-draft.v2",
            "record_type": "guardian_key_rotation",
        },
        "submission_boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True,
            "later_records_may_reclassify_or_correct_this_record": True,
        },
    }


def main():
    require(
        "guardian_key_rotation" in RESERVED_RECORD_TYPES,
        "guardian_key_rotation must be reserved",
    )
    require(
        "guardian_key_rotation" not in ALLOWED_RECORD_TYPES,
        "reserved guardian_key_rotation must not be allowed",
    )

    sub = minimal_reserved_submission()
    diagnostics = validate_submission(sub)
    codes = {d.code for d in diagnostics}

    require(
        "GUARDIAN_KEY_ROTATION_RESERVED" in codes,
        f"expected GUARDIAN_KEY_ROTATION_RESERVED, got {sorted(codes)}",
    )
    require(
        detect_route(sub) == "unknown",
        "reserved guardian_key_rotation must not route as an accepted public type",
    )

    print("PASS: guardian_key_rotation reserved-state gateway contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
