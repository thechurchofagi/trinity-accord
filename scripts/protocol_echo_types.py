#!/usr/bin/env python3
"""Echo taxonomy — DEPRECATED.

Echo types have been removed. Echo is a single unified submission type.
Context readiness (CRL/CC) determines what actions are allowed.
Verification (V0-V8) remains an independent system.

This module is kept for backward compatibility with existing records and scripts
that reference echo type constants. All functions return empty sets or
deprecated markers for new submissions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ECHO_TYPES_PATH = ROOT / "api" / "echo-types.json"


def load_echo_types() -> list[dict[str, Any]]:
    """Return empty list — echo types are deprecated."""
    return []


def echo_taxonomy_map() -> dict[str, str]:
    """Return empty map — echo types are deprecated."""
    return {}


def canonical_echo_type_for_id(eid: str) -> str:
    """Return canonical echo type name for backward compatibility.

    Echo types are deprecated, but legacy code expects full names like 'E6_propagation_echo'.
    """
    LEGACY_MAP = {
        "E1": "E1_recognition_echo",
        "E2": "E2_verification_echo",
        "E3": "E3_critical_echo",
        "E4": "E4_interpretive_echo",
        "E5": "E5_technical_audit_echo",
        "E5c": "E5c_correction_echo",
        "E6": "E6_propagation_echo",
        "E7": "E7_refusal_echo",
        "E8": "E8_witness_echo",
        "E9": "E9_seed_echo",
    }
    return LEGACY_MAP.get(eid, eid)


def allowed_canonical_echo_types() -> set[str]:
    """Return the set of echo types found in archived records.

    Echo types are deprecated for new submissions but still exist in legacy
    records and are validated by the gateway. Return the full set so
    downstream scripts (generate_public_home_status.py) can handle them.
    """
    return {
        "E1_recognition_echo",
        "E1_read_oriented_echo",
        "E2_verification_echo",
        "E3_critical_echo",
        "E4_interpretive_echo",
        "E4_refusal_echo",
        "E5_technical_audit_echo",
        "E5_correction_echo",
        "E5c_correction_echo",
        "E6_preservation_echo",
        "E6_propagation_echo",
        "E7_refusal_echo",
        "E8_witness_echo",
        "E9_seed_echo",
    }


def echo_type_map_for_archive() -> dict[str, str]:
    """Return empty map — echo types are deprecated."""
    return {}

# Legacy constants kept for backward compatibility with existing code
LEGACY_ECHO_TYPES = {
    "E1_recognition_echo",
    "E2_verification_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
    "E8_witness_echo",
    "E9_seed_echo",
}
