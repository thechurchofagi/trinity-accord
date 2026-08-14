from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/sync_bitcoin_address_inscriptions.py"
WORKFLOW = ROOT / ".github/workflows/sync-bitcoin-address-inscriptions.yml"

spec = importlib.util.spec_from_file_location("sync_bitcoin_address_inscriptions", SCRIPT)
assert spec and spec.loader
sync_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_mod)


def test_inscription_id_validation_is_strict():
    assert sync_mod.ID_RE.fullmatch("0" * 64 + "i0")
    assert sync_mod.ID_RE.fullmatch("a" * 64 + "i42")
    assert not sync_mod.ID_RE.fullmatch("A" * 64 + "i0")
    assert not sync_mod.ID_RE.fullmatch("0" * 63 + "i0")
    assert not sync_mod.ID_RE.fullmatch("0" * 64 + "i01")


def test_manifest_has_no_fixed_expected_count():
    ids = ["0" * 64 + "i0", "1" * 64 + "i1"]
    manifest = sync_mod.build_manifest(sync_mod.AUTHORITY_ADDRESS, ids, [])
    assert manifest["count"] == 2
    assert manifest["ids"] == ids
    assert manifest["discovery"]["fixed_count"] is False
    assert manifest["authority_boundary"]["archive_only"] is True
    assert manifest["authority_boundary"]["three_bitcoin_originals_remain_canonical"] is True
    assert "expected_count" not in manifest


def test_sync_fails_closed_when_address_set_changes(tmp_path):
    first = ["0" * 64 + "i0"]
    second = ["0" * 64 + "i0", "1" * 64 + "i0"]
    with patch.object(sync_mod, "discover_ids", side_effect=[first, second]), patch.object(
        sync_mod,
        "write_object",
        return_value={"id": first[0], "content_length": 1, "content_sha256": "a" * 64, "content_type": "text/plain"},
    ):
        try:
            sync_mod.sync("https://example.invalid", sync_mod.AUTHORITY_ADDRESS, tmp_path)
        except RuntimeError as exc:
            assert "changed during synchronization" in str(exc)
        else:
            raise AssertionError("sync must fail closed on a changing address set")


def test_dedicated_workflow_is_isolated_and_pr_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Sync Bitcoin authority-address inscriptions" in text
    assert "workflow_dispatch:" in text
    assert "schedule:" in text
    assert "scripts/sync_bitcoin_address_inscriptions.py" in text
    assert "bitcoin-inscription-mirrors/address-wide" in text
    assert "pull-requests: write" in text
    assert "automation/bitcoin-address-inscription-snapshot" in text
    assert "gh pr create" in text
    assert "git push origin HEAD:main" not in text
    assert "homepage-status-sync" not in text
    assert "update_public_generated_artifacts.py" not in text
