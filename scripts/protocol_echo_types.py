#!/usr/bin/env python3
"""Single source of truth for Echo taxonomy.

Loads canonical echo types from api/echo-types.json and provides
helper functions for consistent type naming across scripts.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ECHO_TYPES_PATH = ROOT / "api" / "echo-types.json"

KEY_TO_CANONICAL_SUFFIX = {
    "recognition": "recognition_echo",
    "verification": "verification_echo",
    "critical": "critical_echo",
    "interpretive": "interpretive_echo",
    "technical-audit": "technical_audit_echo",
    "propagation": "propagation_echo",
    "refusal": "refusal_echo",
    "witness": "witness_echo",
    "seed": "seed_echo",
}


def load_echo_types() -> list[dict[str, Any]]:
    data = json.loads(ECHO_TYPES_PATH.read_text(encoding="utf-8"))
    return [item for item in data.get("types", []) if isinstance(item, dict)]


def echo_taxonomy_map() -> dict[str, str]:
    """Map E-code id to taxonomy key, e.g. {'E6': 'propagation', 'E7': 'refusal'}."""
    out = {}
    for item in load_echo_types():
        eid = item.get("id")
        key = item.get("key")
        if not eid or not key:
            continue
        out[eid] = key
    return out


def canonical_echo_type_for_id(eid: str) -> str:
    """Return canonical echo type name, e.g. 'E6' -> 'E6_propagation_echo'."""
    mapping = echo_taxonomy_map()
    key = mapping[eid]
    suffix = KEY_TO_CANONICAL_SUFFIX[key]
    return f"{eid}_{suffix}"


def allowed_canonical_echo_types() -> set[str]:
    """Return set of all allowed canonical echo type names."""
    return {canonical_echo_type_for_id(eid) for eid in echo_taxonomy_map()}


def echo_type_map_for_archive() -> dict[str, str]:
    """Return ECHO_TYPE_MAP dict for use in archive_echo_issue.py."""
    out = {}
    for eid in echo_taxonomy_map():
        out[eid] = canonical_echo_type_for_id(eid)
    return out
