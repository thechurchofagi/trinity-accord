#!/usr/bin/env python3
"""Generate public Guardian API mirrors from derived guardian-state.

Reads:  record-chain/indexes/guardian-state.json
Writes: api/guardian-state.json
        api/guardian-current-registry.json

Deterministic output. No wall-clock timestamps. Uses guardian-state.derived_at.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "record-chain" / "indexes" / "guardian-state.json"
API_STATE = ROOT / "api" / "guardian-state.json"
API_CURRENT = ROOT / "api" / "guardian-current-registry.json"


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False, allow_nan=False) + "\n"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def public_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "guardian_id": entry.get("guardian_id"),
        "guardian_public_key_sha256": entry.get("guardian_public_key_sha256"),
        "status": entry.get("current_derived_status"),
        "source_record_id": entry.get("source_record_id"),
        "source_record_sha256": entry.get("source_record_sha256"),
        "source_record_path": entry.get("source_record_path"),
        "verified_by_append_before_record": entry.get("verified_by_append_before_record"),
        "activation": entry.get("activation"),
        "boundary": entry.get("boundary"),
    }


def build_outputs() -> tuple[dict[str, Any], dict[str, Any]]:
    state = read_json(SOURCE)
    guardians = state.get("guardians", [])
    if not isinstance(guardians, list):
        raise SystemExit("record-chain/indexes/guardian-state.json guardians must be a list")

    api_state = {
        **state,
        "schema": "trinityaccord.api.guardian-state.v1",
        "source": "record-chain/indexes/guardian-state.json",
        "boundary": {
            **(state.get("boundary") if isinstance(state.get("boundary"), dict) else {}),
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_verification_level": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_active_guardian_status": True,
        },
    }

    active = [g for g in guardians if g.get("current_derived_status") == "active_registered_guardian"]
    pending = [
        g for g in guardians
        if g.get("current_derived_status") in {
            "application_recorded_pending_activation",
            "pending_verification",
        }
    ]
    retired = [g for g in guardians if g.get("current_derived_status") == "retired_guardian"]

    current = {
        "schema": "trinityaccord.guardian-current-registry.v1",
        "source": "record-chain/indexes/guardian-state.json",
        "derived_at": state.get("derived_at"),
        "registry_status": "record_chain_derived_non_authoritative_guardian_key_continuity_registry",
        "active_guardians": [public_entry(g) for g in active],
        "pending_guardian_applications": [public_entry(g) for g in pending],
        "retired_guardians": [public_entry(g) for g in retired],
        "counts": {
            "active_registered_guardian": len(active),
            "pending_guardian_applications": len(pending),
            "retired_guardian": len(retired),
            "total_entries": len(guardians),
        },
        "boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_verification_level": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_active_guardian_status": True,
        },
        "legacy_registry_note": (
            "/api/guardian-registry.json is a legacy/historical key-continuity listing. "
            "Current native Guardian status is derived from Record-Chain guardian-state."
        ),
    }
    return api_state, current


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    api_state, current = build_outputs()
    expected = {
        API_STATE: dump_json(api_state),
        API_CURRENT: dump_json(current),
    }

    if args.check:
        drift = []
        for path, text in expected.items():
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                drift.append(str(path.relative_to(ROOT)))
        if drift:
            print("guardian current registry drift detected. Run: python3 scripts/generate_guardian_current_registry.py")
            for item in drift:
                print(f"- {item}")
            return 1
        print("guardian current registry up to date")
        return 0

    for path, text in expected.items():
        path.write_text(text, encoding="utf-8")
        print(f"updated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
