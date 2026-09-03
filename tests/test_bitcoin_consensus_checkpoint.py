from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bitcoin_consensus_checkpoint.py"
WORKFLOW_PATH = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "bitcoin-consensus-checkpoint.yml"
SPEC = importlib.util.spec_from_file_location("bitcoin_consensus_checkpoint", MODULE_PATH)
assert SPEC and SPEC.loader
checkpoint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checkpoint)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def valid_manifest(sequence: int = 1) -> dict:
    previous = None
    if sequence > 1:
        previous = {
            "tag": f"bitcoin-consensus-checkpoint-{sequence - 1:06d}",
            "manifest_sha256": _sha("previous"),
        }
    return {
        "schema": checkpoint.SCHEMA,
        "profile": checkpoint.PROFILE,
        "network": "main",
        "bitcoin_core_version": "31.1",
        "bitcoin_core_archive_sha256": _sha("bitcoin-core"),
        "assumevalid": "0",
        "prune_mib": 550,
        "clean_shutdown": True,
        "initialblockdownload": True,
        "height": 500000,
        "best_block_hash": _sha("block"),
        "verification_progress": 0.75,
        "workflow": {
            "repository": "thechurchofagi/trinity-accord",
            "run_id": "123",
            "run_attempt": "1",
            "sha": "a" * 40,
        },
        "checkpoint": {
            "sequence": sequence,
            "tag": f"bitcoin-consensus-checkpoint-{sequence:06d}",
            "created_at": "2026-08-31T12:00:00Z",
        },
        "previous_checkpoint": previous,
        "assets": [
            {
                "name": "bitcoin-datadir.tar.zst.part-0000",
                "size": 10,
                "sha256": _sha("asset"),
            }
        ],
    }


def test_accepts_genesis_checkpoint_manifest():
    checkpoint.validate_manifest(valid_manifest())


def test_accepts_linked_successor_manifest():
    checkpoint.validate_manifest(valid_manifest(2))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("assumevalid", "0000000000000000000000000000000000000000000000000000000000000000"),
        ("clean_shutdown", False),
        ("network", "test"),
        ("profile", "dual_remote_esplora"),
    ],
)
def test_rejects_trust_boundary_downgrades(field, value):
    manifest = valid_manifest()
    manifest[field] = value
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.validate_manifest(manifest)


def test_rejects_broken_predecessor_chain():
    manifest = valid_manifest(3)
    manifest["previous_checkpoint"]["tag"] = "bitcoin-consensus-checkpoint-000001"
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.validate_manifest(manifest)


def test_rejects_duplicate_assets():
    manifest = valid_manifest()
    manifest["assets"].append(dict(manifest["assets"][0]))
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.validate_manifest(manifest)


def test_verify_asset_checks_size_and_sha256(tmp_path: Path):
    payload = b"checkpoint-part"
    path = tmp_path / "bitcoin-datadir.tar.zst.part-0000"
    path.write_bytes(payload)
    manifest = valid_manifest()
    manifest["assets"][0]["size"] = len(payload)
    manifest["assets"][0]["sha256"] = hashlib.sha256(payload).hexdigest()

    checkpoint.verify_asset(manifest, path.name, path)

    path.write_bytes(payload + b"corrupt")
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.verify_asset(manifest, path.name, path)


def test_canonical_manifest_serialization_is_stable(tmp_path: Path):
    manifest = valid_manifest()
    first = tmp_path / "one.json"
    second = tmp_path / "two.json"
    checkpoint.write_canonical_json(manifest, first)
    checkpoint.write_canonical_json(json.loads(first.read_text()), second)
    assert first.read_bytes() == second.read_bytes()
    assert checkpoint.sha256_file(first) == checkpoint.sha256_file(second)


def test_split_filter_materializes_stdin_before_hashing_and_upload():
    source = WORKFLOW_PATH.read_text()
    assert "--filter='" in source
    filter_block = source.split("--filter='", 1)[1].split("\n                '", 1)[0]

    materialize = filter_block.index('cat > "$FILE"')
    stat_file = filter_block.index('stat -c %s "$FILE"')
    hash_file = filter_block.index('sha256sum "$FILE"')
    upload = filter_block.index('gh release upload "$CHECKPOINT_TAG" "$FILE"')
    remove = filter_block.index('rm -f "$FILE"')

    assert materialize < stat_file < hash_file < upload < remove


def test_release_preflight_cleans_exact_next_draft_before_ibd():
    source = WORKFLOW_PATH.read_text()
    preflight = source.split(
        "- name: Verify checkpoint Release write permission", 1
    )[1].split("- name: Restore previous checkpoint as a verified stream", 1)[0]

    assert "next_tag=" in preflight
    assert "select(.tag_name == $tag and .draft == true)" in preflight
    assert 'gh api --method DELETE "repos/${GITHUB_REPOSITORY}/releases/${stale_id}"' in preflight
    assert "refusing to start Bitcoin IBD" in preflight


def test_restore_ignores_archived_file_ownership():
    source = WORKFLOW_PATH.read_text()
    restore = source.split(
        "- name: Restore previous checkpoint as a verified stream", 1
    )[1].split("- name: Download and verify Bitcoin Core distribution", 1)[0]

    assert '| tar --no-same-owner -xf - -C "$DATADIR"' in restore


def test_restored_pruned_chainstate_reopens_with_sealed_prune_mode():
    source = WORKFLOW_PATH.read_text()
    restore_verification = source.split(
        "- name: Verify restored chainstate matches its sealed predecessor", 1
    )[1].split("- name: Advance Bitcoin Core consensus validation", 1)[0]

    assert 'sealed_prune_mib="$(jq -r \'.prune_mib\' "$PREVIOUS_MANIFEST")"' in restore_verification
    assert (
        'bitcoind -datadir="$DATADIR" -prune="$sealed_prune_mib" '
        "-connect=0 -dnsseed=0 -listen=0 -daemonwait"
    ) in restore_verification


def test_restored_chainstate_reopen_failure_prints_debug_tail():
    source = WORKFLOW_PATH.read_text()
    restore_verification = source.split(
        "- name: Verify restored chainstate matches its sealed predecessor", 1
    )[1].split("- name: Advance Bitcoin Core consensus validation", 1)[0]

    assert 'if ! bitcoind -datadir="$DATADIR"' in restore_verification
    assert 'tail -n 100 "$DATADIR/debug.log" >&2' in restore_verification


def test_completed_ibd_draft_is_remotely_restored_before_publication():
    source = WORKFLOW_PATH.read_text()
    sealing = source.split(
        "- name: Seal immutable checkpoint into a draft Release", 1
    )[1].split("- name: Finalize live telemetry check", 1)[0]

    manifest_upload = sealing.index(
        'gh release upload "$tag" "$CHECKPOINT_MANIFEST#bitcoin-consensus-checkpoint.json"'
    )
    final_gate = sealing.index('if [[ "$final_ibd" == "false" ]]')
    remote_verify = sealing.index(
        'verify-asset "$CHECKPOINT_MANIFEST" "$name" "$final_part"'
    )
    offline_reopen = sealing.index(
        'bitcoind -datadir="$DATADIR" -prune="$PRUNE_MIB" -disablewallet=1'
    )
    publish = sealing.index('gh release edit "$tag" --draft=false')

    assert manifest_upload < final_gate < remote_verify < offline_reopen < publish
    assert 'cmp "$CHECKPOINT_MANIFEST" "$remote_manifest"' in sealing
    assert '"$DATADIR" == "$RUNNER_TEMP/bitcoin-mainnet"' in sealing
    assert 'restored_height" == "$expected_height' in sealing
    assert 'restored_hash" == "$expected_hash' in sealing
    assert 'restored_ibd" == "false' in sealing
