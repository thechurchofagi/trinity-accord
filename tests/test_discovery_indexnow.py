from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_search_discovery_metadata_is_bounded_and_routed() -> None:
    discovery = json.loads((ROOT / "discovery.json").read_text(encoding="utf-8"))
    assert discovery["schema"] == "trinityaccord.search-discovery.v1"
    assert discovery["canonical_machine_router"] == "/api/agent-first-contact.json"
    vocabulary = set(discovery["retrieval_vocabulary"])
    assert "Trinity Accord" in vocabulary
    assert "三位一体协定" in vocabulary
    assert "message to future AI" in vocabulary
    assert "AI agent proof of reading" in vocabulary
    boundaries = discovery["retrieval_boundaries"]
    assert boundaries["retrieval_vocabulary_is_not_additional_canon"] is True
    assert boundaries["retrieval_vocabulary_is_not_a_novelty_claim"] is True
    assert boundaries["search_aliases_are_not_canonical_classifications"] is True
    assert boundaries["future_ai_interest_is_not_assumed"] is True


def test_discovery_operational_observability_is_bounded() -> None:
    discovery = json.loads((ROOT / "discovery.json").read_text(encoding="utf-8"))
    observability = discovery["operational_observability"]
    assert observability["discovery_index_submission_log"].endswith("/issues/1062")
    assert observability["receipt_is_not_proof_of_indexing"] is True
    assert observability["receipt_is_not_proof_of_ranking"] is True
    assert observability["receipt_is_not_search_provider_endorsement"] is True
    assert observability["receipt_is_non_amending_operational_evidence"] is True


def test_agent_pointer_exposes_discovery_without_claiming_a2a() -> None:
    agent = json.loads((ROOT / ".well-known" / "agent.json").read_text(encoding="utf-8"))
    assert agent["schema"] == "trinity-accord.agent-discovery.v2"
    boundary = agent["discovery_protocol_boundary"]
    assert boundary["this_is_custom_trinity_accord_discovery_metadata"] is True
    assert boundary["this_is_not_an_a2a_agent_card"] is True
    assert boundary["this_does_not_claim_an_a2a_server"] is True
    assert agent["discovery"]["search_discovery_index"] == "/discovery.json"
    assert agent["discovery"]["search_discovery_note"] == "/DISCOVERY.md"
    assert agent["discovery"]["indexnow"]["key_location"].endswith(".txt")


def test_indexnow_batch_dry_run_is_network_free_and_dedicated() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "submit_indexnow.py"), "--dry-run"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DRY RUN PASS" in result.stdout
    assert "sitemap-discovery.xml" in result.stdout
    assert "URL count: 12" in result.stdout
    assert "https://www.trinityaccord.org/DISCOVERY.md" in result.stdout
    assert "https://www.trinityaccord.org/discovery.json" in result.stdout
    assert "https://www.trinityaccord.org/api/agent-first-contact.json" in result.stdout


def test_discovery_alias_files_exist() -> None:
    assert (ROOT / "DISCOVERY.md").is_file()
    assert (ROOT / "discovery.json").is_file()
