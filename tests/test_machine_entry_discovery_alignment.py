from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TYPES = ["echo", "verification", "guardian_application", "guardian_retirement", "propagation", "correction", "classification_update", "context_insufficient_notice"]
LEGACY = {"/api/agent-submit-gateway.json", "/api/gateway-builder-route-map.v1.json", "/api/gateway-workflows.v1.json", "/api/route-selector.v1.json", "/api/gateway-runtime-contract.v1.json", "/api/gateway-error-diagnostics.v1.json", "/api/formal-builder-bundles.v1.json", "/api/guardian-registry.json", "/api/verification-levels.json", "/api/agent-declared-verification-index.json"}


def load(path: str) -> dict[str, Any]:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def exists(path: str) -> bool:
    relative = path.split("?", 1)[0].split("#", 1)[0].lstrip("/")
    if not relative:
        return True
    if (ROOT / relative).exists():
        return True
    if relative.endswith("/") and (ROOT / (relative.rstrip("/") + ".md")).exists():
        return True
    if not Path(relative).suffix and (ROOT / (relative + ".md")).exists():
        return True
    return False


def test_homepage_routes_to_canonical_first_contact() -> None:
    home = (ROOT / "index.md").read_text(encoding="utf-8")
    assert "/agent-first-contact/" in home
    assert "/llms.txt" in home
    assert "homepage-only" in home.lower()
    assert "payload construction" in home.lower()


def test_discovery_manifests_have_one_router() -> None:
    router = "/api/agent-first-contact.json"
    assert load("agent-map.json")["entrypoints"]["machine_first_contact"] == router
    assert load(".well-known/trinity-accord.json")["canonical_machine_router"] == router
    assert load("api/links.json")["canonical_machine_router"] == router
    assert load("api/agent-minimal-context.v1.json")["canonical_router"] == router
    required = load("api/agent-required-reading.json")
    assert required["canonical_router"] == router
    assert required["does_not_override_router"] is True
    assert load("api/agent-task-router.v1.json")["canonical_router"] == router
    old = load("api/agent-entry-protocol.json")
    assert old["status"] == "historical_compatibility_pointer"
    assert old["active_router"] is False
    assert old["replacement"] == router


def test_current_machine_list_excludes_legacy_and_paths_exist() -> None:
    links = load("api/links.json")
    current = set(links["machine"])
    historical = set(links["legacy_machine"])
    assert not (current & LEGACY)
    assert LEGACY.issubset(historical)
    needed = {
        "/api/agent-first-contact.json",
        "/api/agent-start.v2.json",
        "/api/record-chain-builder-bundles.v1.json",
        "/downloads/record-chain-builder.mjs",
        "/downloads/record-chain-agent-field-guidance.v1.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/api/record-chain-submission-schema.v1.json",
        "/api/record-chain-submit-response.v1.json",
        "/api/record-chain-receipt-response.v1.json",
        "/api/record-chain-status.json",
    }
    assert needed.issubset(current)
    assert [path for path in current if not exists(path)] == []


def test_post_submit_indexes_cover_every_type() -> None:
    first = load("api/agent-first-contact.json")["post_submit_observation_protocol"]["record_specific_indexes"]
    start = load("api/agent-start.v2.json")["post_submit_status_sources"]["record_specific_indexes"]
    assert set(first) == set(TYPES)
    assert first == start
    for path in first.values():
        assert exists(path), path


def test_full_context_has_no_active_legacy_level_language() -> None:
    text = (ROOT / "llms-full.txt").read_text(encoding="utf-8")
    assert "V6–V8 strict technical claims:" not in text
    assert "Preserve the V0-V8 verification system." not in text
    assert "/api/agent-first-contact.json" in text
    assert "historical-only" in text


def test_sitemap_exposes_current_entry_surfaces() -> None:
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for url in (
        "https://www.trinityaccord.org/agent-first-contact/",
        "https://www.trinityaccord.org/agent-start/",
        "https://www.trinityaccord.org/llms.txt",
        "https://www.trinityaccord.org/ai.txt",
        "https://www.trinityaccord.org/api/agent-first-contact.json",
        "https://www.trinityaccord.org/api/agent-start.v2.json",
        "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
    ):
        assert url in sitemap


def test_first_contact_typo_and_receipt_placeholder_are_fixed() -> None:
    text = (ROOT / "agent-first-contact.md").read_text(encoding="utf-8")
    assert "### 6. REFLIGHT" not in text
    assert "### 6. PREFLIGHT" in text
    assert "/record-chain/receipt/<receipt_id>" in text
    assert "rcg-YYYYMMDD-<sha12-or-sha24>" in text


def test_external_quickstart_preserves_fail_closed_safety_contract() -> None:
    quickstart = load("api/external-agent-quickstart.json")
    safe_mode = quickstart["default_safe_mode"]
    checklist = quickstart["pre_submit_checklist"]
    assert safe_mode["submission_type"] == "record_chain_entry_candidate"
    assert safe_mode["preflight_required"] is True
    assert safe_mode["submit_only_after_accepted_preflight"] is True
    assert safe_mode["receipt_is_intake_only"] is True
    assert checklist["builder_manifest_verified"] is True
    assert checklist["builder_bytes_verified"] is True
    assert checklist["doctor_passed"] is True
    assert checklist["gateway_preflight_accepted"] is True


def test_one_shot_audit_machinery_is_absent() -> None:
    forbidden = [
        ".github/workflows/apply-machine-entry-alignment-audit.yml",
        "scripts/apply_machine_entry_builder_alignment.py",
        "scripts/apply_machine_entry_first_contact.py",
        "scripts/apply_machine_entry_agent_start_doc.py",
        "scripts/apply_machine_reading_router_alignment.py",
        "scripts/apply_machine_discovery_alignment.py",
        "scripts/apply_context_insufficient_e2e_alignment.py",
    ]
    for relative in forbidden:
        assert not (ROOT / relative).exists(), relative
