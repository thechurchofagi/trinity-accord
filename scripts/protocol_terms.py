#!/usr/bin/env python3
"""
Single source of truth for Trinity Accord protocol terms and enums.
Loads from api/protocol-terms.v1.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_TERMS_PATH = ROOT / "api" / "protocol-terms.v1.json"

def load_protocol_terms():
    with open(_TERMS_PATH) as f:
        return json.load(f)

_TERMS = load_protocol_terms()

PROTOCOL_LEVELS = _TERMS["protocol_levels"]
B_LEVELS = _TERMS["component_levels"]["bitcoin_originals"]
D_LEVELS = _TERMS["component_levels"]["digital_mirrors"]
T_LEVELS = _TERMS["component_levels"]["time_anchors"]
C_LEVELS = _TERMS["component_levels"]["chronicle_recovery"]
N_LEVELS = _TERMS["component_levels"]["nft_evidence"]
P_LEVELS = _TERMS["component_levels"]["physical_anchor"]

VALID_RECORD_KINDS = set(_TERMS["record_kinds"])
VALID_ARCHIVE_STATUSES = set(_TERMS["archive_statuses"])
VALID_INDEPENDENCE_CLASSES = set(_TERMS["independence_classes"])
VALID_SCOPE_LABELS = set(_TERMS["verification_scope_labels"])

# Legacy aliases
LEGACY_ALIASES = _TERMS.get("legacy_or_intake_aliases", {})

def level_index(levels, value):
    """Return the index of value in levels list, or -1 if not found."""
    try:
        return levels.index(value)
    except ValueError:
        return -1

def level_at_least(levels, value, floor):
    """Check if value is at or above floor in the levels ordering."""
    vi = level_index(levels, value)
    fi = level_index(levels, floor)
    if vi < 0 or fi < 0:
        return False
    return vi >= fi

def max_by_order(levels, a, b):
    """Return whichever of a/b has the higher index in levels."""
    ai = level_index(levels, a)
    bi = level_index(levels, b)
    if ai >= bi:
        return a
    return b

def resolve_legacy_alias(value):
    """Resolve a legacy alias to its canonical value."""
    return LEGACY_ALIASES.get(value, value)

# --- V0-V5 Agent-Declared Archive Constants ---
ARCHIVE_KIND_AGENT_DECLARED_VERIFICATION = "agent_declared_verification_archive"
CLAIM_GATE_MODE_TEMPLATE_V0_V5 = "template_for_v0_v5"
EVIDENCE_MODE_WAIVED_V0_V5 = "waived_for_v0_v5"
COUNT_BASIS_AGENT_DECLARED_TEMPLATE_PASS = "agent_declared_template_pass"

V0_V5_LEVELS = ["V0", "V1", "V2", "V3", "V4", "V5"]
