from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import public_machine_deployment_contract as contract  # noqa: E402
import smoke_live_discovery_contract_v2 as smoke  # noqa: E402


def load(path: str) -> dict:
    value = json.loads((ROOT / path.lstrip("/")).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_current_links_and_well_known_pass_shared_semantics() -> None:
    errors: list[str] = []
    contract.validate_links_semantics("repo", load("/api/links.json"), errors)
    contract.validate_well_known_semantics(
        "repo", load("/.well-known/trinity-accord.json"), errors
    )
    assert errors == []


def test_live_entrypoint_semantics_pass_on_repository_sources() -> None:
    objects = {path: load(path) for path in contract.SMOKE_JSON_SURFACES}
    texts = {
        path: (ROOT / path.lstrip("/")).read_text(encoding="utf-8")
        for path in contract.SMOKE_TEXT_SURFACES
    }
    errors: list[str] = []
    smoke.validate_entrypoints(objects, texts, errors)
    assert errors == []


def test_retired_routes_cannot_reenter_active_machine_contract() -> None:
    links = load("/api/links.json")
    machine = set(links["machine"])
    legacy = set(links["legacy_machine"])
    assert machine.isdisjoint(contract.RETIRED_ACTIVE_PATHS)
    assert contract.RETIRED_ACTIVE_PATHS.issubset(legacy)

    first = load("/api/agent-first-contact.json")
    intents = {
        item["intent"]
        for item in first["choose_one"]
        if isinstance(item, dict) and "intent" in item
    }
    assert intents.isdisjoint(contract.RETIRED_ROUTE_INTENTS)
    assert smoke.CURRENT_INTENTS.issubset(intents)


def test_every_deployment_surface_exists_and_is_unique() -> None:
    assert len(contract.DEPLOYMENT_BYTE_SURFACES) == len(
        set(contract.DEPLOYMENT_BYTE_SURFACES)
    )
    missing = [
        path
        for path in contract.DEPLOYMENT_BYTE_SURFACES
        if not (ROOT / path.lstrip("/")).is_file()
    ]
    assert missing == []


def test_json_root_must_be_an_object() -> None:
    with pytest.raises(ValueError, match="JSON root must be an object"):
        contract.json_object_from_bytes(b"[]", "test surface")


def test_source_digest_is_bound_to_content() -> None:
    links = load("/api/links.json")
    errors: list[str] = []
    contract.validate_embedded_source_digest("links", links, errors)
    assert errors == []

    links["version"] = "tampered"
    errors.clear()
    contract.validate_embedded_source_digest("links", links, errors)
    assert errors and "not bound" in errors[0]


def test_smoke_uses_unique_nonce_source() -> None:
    source = (SCRIPTS / "smoke_live_discovery_contract_v2.py").read_text(
        encoding="utf-8"
    )
    assert "time.time_ns()" in source
    assert 'query.append(("cb", token))' in source
    assert "/api/echo-index.json" not in source
    assert '"verify_v0_v5_agent_declared"' not in source


def test_deploy_workflow_uses_current_v2_checks() -> None:
    workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text(
        encoding="utf-8"
    )
    assert "scripts/smoke_live_discovery_contract_v2.py" in workflow
    assert "scripts/check_deployment_freshness_v2.py" in workflow
    assert '"scripts/**"' in workflow
    assert "scripts/public_machine_deployment_contract.py" in workflow
