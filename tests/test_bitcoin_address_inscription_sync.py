from __future__ import annotations

import importlib.util
import json
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


def test_manifest_has_no_fixed_expected_count_and_declares_dual_payload_archive():
    ids = ["0" * 64 + "i0", "1" * 64 + "i1"]
    manifest = sync_mod.build_manifest(sync_mod.AUTHORITY_ADDRESS, ids, [])
    assert manifest["schema"] == "trinityaccord.bitcoin-address-inscription-mirror.v2"
    assert manifest["count"] == 2
    assert manifest["ids"] == ids
    assert manifest["discovery"]["fixed_count"] is False
    assert manifest["archive"]["decoded_metadata_is_derivative"] is True
    assert "CBOR metadata" in manifest["archive"]["inscription_metadata_encoding"]
    assert manifest["authority_boundary"]["archive_only"] is True
    assert manifest["authority_boundary"]["three_bitcoin_originals_remain_canonical"] is True
    assert "expected_count" not in manifest


def test_cbor_decoder_handles_text_map():
    raw = bytes.fromhex("a1646e6f74656568656c6c6f")
    assert sync_mod.decode_cbor(raw) == {"note": "hello"}


def test_fetch_inscription_metadata_cbor_decodes_recursive_hex_string():
    inscription_id = "a" * 64 + "i0"
    raw = bytes.fromhex("a1646e6f74656568656c6c6f")
    with patch.object(
        sync_mod,
        "fetch_bytes",
        return_value=json.dumps(raw.hex()).encode("ascii"),
    ) as fetch_bytes:
        observed = sync_mod.fetch_inscription_metadata_cbor(
            "https://ordinals.example", inscription_id
        )
    assert observed == raw
    fetch_bytes.assert_called_once_with(
        f"https://ordinals.example/r/metadata/{inscription_id}",
        absent_statuses=frozenset({404}),
    )


def test_fetch_inscription_metadata_cbor_accepts_absent_metadata():
    inscription_id = "a" * 64 + "i0"
    for response in (b'""', b"null", None):
        with patch.object(sync_mod, "fetch_bytes", return_value=response):
            assert (
                sync_mod.fetch_inscription_metadata_cbor(
                    "https://ordinals.example", inscription_id
                )
                == b""
            )


def test_write_object_archives_content_and_independent_cbor_metadata(tmp_path):
    inscription_id = "a" * 64 + "i0"
    info = {
        "id": inscription_id,
        "address": sync_mod.AUTHORITY_ADDRESS,
        "content_length": 3,
        "content_type": "image/webp",
    }
    metadata_cbor = bytes.fromhex("a1646e6f74656568656c6c6f")

    def fake_fetch_bytes(url: str, **_: object) -> bytes:
        if url.endswith(f"/content/{inscription_id}"):
            return b"abc"
        if url.endswith(f"/r/metadata/{inscription_id}"):
            return json.dumps(metadata_cbor.hex()).encode("ascii")
        raise AssertionError(url)

    with patch.object(sync_mod, "fetch_json", return_value=info) as fetch_json, patch.object(
        sync_mod, "fetch_bytes", side_effect=fake_fetch_bytes
    ):
        result = sync_mod.write_object(
            "https://ordinals.example",
            sync_mod.AUTHORITY_ADDRESS,
            inscription_id,
            tmp_path,
        )

    fetch_json.assert_called_once_with(
        f"https://ordinals.example/r/inscription/{inscription_id}", negotiate=False
    )
    assert result["content_sha256"] == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    assert result["inscription_metadata_present"] is True
    assert result["inscription_metadata_length"] == len(metadata_cbor)

    obj = tmp_path / "objects" / inscription_id
    assert (obj / "inscription-metadata.cbor.hex").read_text().strip() == metadata_cbor.hex()
    decoded = json.loads((obj / "inscription-metadata.decoded.json").read_text())
    assert decoded["present"] is True
    assert decoded["derived_not_authority"] is True
    assert decoded["decoded"] == {"note": "hello"}


def test_sync_fails_closed_when_address_set_changes(tmp_path):
    first = ["0" * 64 + "i0"]
    second = ["0" * 64 + "i0", "1" * 64 + "i0"]
    with patch.object(sync_mod, "discover_ids", side_effect=[first, second]), patch.object(
        sync_mod,
        "write_object",
        return_value={
            "id": first[0],
            "content_length": 1,
            "content_sha256": "a" * 64,
            "content_type": "text/plain",
            "inscription_metadata_present": False,
            "inscription_metadata_length": 0,
            "inscription_metadata_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        },
    ):
        try:
            sync_mod.sync(
                "https://example.invalid",
                sync_mod.AUTHORITY_ADDRESS,
                tmp_path,
            )
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
