from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RETIRED_ENTRYPOINTS = (
    ROOT / ".github/workflows/external-binary-annex-publication.yml",
    ROOT / ".github/workflows/external-binary-annex-publication-v4.yml",
    ROOT / "preservation/external-binary-annex-publication-trigger.json",
    ROOT / "preservation/external-binary-annex-publication-attempt.json",
)


def final_state() -> dict[str, object]:
    return json.loads(
        (ROOT / "preservation/external-binary-annex-state.json").read_text(
            encoding="utf-8"
        )
    )


def test_one_time_annex_workflows_are_retired_after_success():
    state = final_state()
    assert state["publication_status"] == "published_and_publicly_restored"
    for path in RETIRED_ENTRYPOINTS:
        assert not path.exists(), path


def test_retirement_preserves_complete_public_recovery_state():
    state = final_state()
    assert state["release_asset_pagination_complete"] is True
    assert state["public_metadata_verification"] == "passed"
    assert state["external_binary_payload_recovery_requires_github"] is False
    assert state["annexes"]["evidence"]["public_cold_restore"] == "passed"
    assert state["annexes"]["nft"]["public_cold_restore"] == "passed"


def test_retired_writers_are_replaced_by_read_only_recovery_entrypoints():
    index = json.loads(
        (ROOT / "api/recovery-index.json").read_text(encoding="utf-8")
    )
    entrypoints = index["recovery_entrypoints"]
    assert entrypoints["external_binary_annex_state"] == (
        "preservation/external-binary-annex-state.json"
    )
    assert entrypoints["external_binary_annex_observation"] == (
        "preservation/external-binary-annex-observation.json"
    )
    assert entrypoints["external_binary_annex_restore_cli"] == (
        "scripts/restore_external_binary_annex.py"
    )
