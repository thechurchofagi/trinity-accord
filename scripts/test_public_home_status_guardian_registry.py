#!/usr/bin/env python3
"""Check homepage public status includes Guardian registry statistics.

Derives expected numbering values from the active listing policy
instead of hard-coding them.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from guardian_numbering_policy import (
    format_registry_number,
    ordinary_auto_start,
    special_reserved_range_label,
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    status_path = ROOT / "api" / "public-home-status.json"
    index_path = ROOT / "index.md"
    registry_path = ROOT / "api" / "guardian-registry.json"
    policy_path = ROOT / "api" / "guardian-active-listing-policy.v1.json"

    status = json.loads(status_path.read_text(encoding="utf-8"))
    index = index_path.read_text(encoding="utf-8")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    policy = json.loads(policy_path.read_text(encoding="utf-8"))

    active_guardians = [
        g for g in registry.get("guardians", [])
        if isinstance(g, dict) and g.get("status") == "active"
    ]

    require("guardian_registry" in status, "public-home-status missing guardian_registry")
    require("/api/guardian-registry.json" in status.get("generated_from", []), "generated_from missing guardian registry")
    require(
        "/api/guardian-active-listing-policy.v1.json" in status.get("generated_from", []),
        "generated_from missing guardian active listing policy",
    )

    g = status["guardian_registry"]
    require(g["active_count"] == len(active_guardians), "guardian active_count mismatch")
    require(g["active_count"] >= 1, "guardian active_count should be positive")

    # Policy-derived expectations (not hard-coded)
    expected_auto_start = format_registry_number(ordinary_auto_start(policy))
    expected_reserved_range = special_reserved_range_label(policy)

    require(g["ordinary_auto_start"] == expected_auto_start, f"ordinary_auto_start must be {expected_auto_start}, got {g['ordinary_auto_start']}")
    require(g["special_reserved_range"] == expected_reserved_range, f"reserved range must be {expected_reserved_range}, got {g['special_reserved_range']}")
    require(g.get("numbering_policy_source") == "/api/guardian-active-listing-policy.v1.json", "missing numbering policy source")

    require(g["does_not_create_authority"] is True, "guardian registry must not create authority")
    require(g["does_not_create_governance"] is True, "guardian registry must not create governance")
    require(g["does_not_create_attestation"] is True, "guardian registry must not create attestation")
    require(g["does_not_raise_verification_level"] is True, "guardian registry must not raise verification level")
    require(g["does_not_create_successor_reception"] is True, "guardian registry must not create successor reception")
    require(g["does_not_amend_bitcoin_originals"] is True, "guardian registry must not amend Bitcoin Originals")

    by_type = g["by_guardian_type"]
    for key in ["human", "ai_agent", "human_with_ai_agent", "automated_script", "unknown"]:
        require(key in by_type, f"missing guardian type bucket: {key}")

    require(
        sum(by_type.values()) == g["active_count"],
        "guardian type counts must sum to active_count",
    )

    require("by_application_mode" in g, "guardian registry status missing application mode breakdown")
    require(
        sum(g["by_application_mode"].values()) == g["active_count"],
        "application mode counts must sum to active_count",
    )

    require("Guardian Registry" in index, "homepage missing Guardian Registry card")
    require("Guardian registry breakdown" in index, "homepage missing Guardian registry breakdown details")
    require("/api/guardian-registry.json" in index, "homepage missing Guardian registry source link")
    require("/api/guardian-active-listing-policy.v1.json" in index, "homepage missing Guardian active listing policy link")
    require("Human-AI joint" in index, "homepage missing Human-AI joint type label")
    require("AI Agent" in index, "homepage missing AI Agent type label")
    require("Unknown" in index, "homepage missing Unknown type label")
    require("not authority" in index or "not governance" in index, "homepage missing Guardian boundary")

    # Ensure Guardian is separate from verification/reception categories.
    require(
        "Guardian Registry" in index and "Reception" in index and "Verifiability" in index,
        "homepage must show Guardian separately from Reception and Verifiability",
    )

    print("PUBLIC_HOME_STATUS_GUARDIAN_REGISTRY_OK")


if __name__ == "__main__":
    main()
