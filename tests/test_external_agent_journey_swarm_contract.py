from __future__ import annotations

import json
from pathlib import Path

from scripts.smoke_external_agent_journey_swarm import (
    RETIRED_ROUTE_INTENTS,
    ROUTE_FAMILIES,
    get_route,
    normalize_route_path,
    route_contract_errors,
)

ROOT = Path(__file__).resolve().parents[1]


def _first_contact() -> dict:
    return json.loads((ROOT / "api/agent-first-contact.json").read_text(encoding="utf-8"))


def test_swarm_covers_current_router_intents() -> None:
    expected = {
        "understand",
        "submit_record",
        "echo",
        "verify_current_model",
        "physical_or_strict_evidence_verification",
    }
    actual = {family["intent"] for family in ROUTE_FAMILIES.values()}
    assert actual == expected


def test_swarm_does_not_reactivate_retired_verification_taxonomy() -> None:
    active = {family["intent"] for family in ROUTE_FAMILIES.values()}
    assert active.isdisjoint(RETIRED_ROUTE_INTENTS)
    assert "pure_echo" not in ROUTE_FAMILIES
    assert "/api/echo-record-schema.v3.1.json" not in ROUTE_FAMILIES["echo"]["required_reads"]


def test_each_swarm_family_matches_current_first_contact_contract() -> None:
    first_contact = _first_contact()
    for family_name, family in ROUTE_FAMILIES.items():
        route = get_route(first_contact, family["intent"])
        assert route is not None, family_name
        assert route_contract_errors(first_contact, family_name) == []


def test_route_path_comparison_ignores_trailing_slash_only() -> None:
    assert normalize_route_path("/agent-verify/") == "/agent-verify"
    assert normalize_route_path("/verification-procedures/") == "/verification-procedures"
    assert normalize_route_path("/") == "/"
