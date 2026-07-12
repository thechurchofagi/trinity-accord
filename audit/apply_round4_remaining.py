#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one replacement target, found {text.count(old)}")
    path.write_text(text.replace(old, new), encoding="utf-8")


generator = Path("scripts/generate_waiting_heartbeat_status.py")
replace_once(
    generator,
    "from typing import Any\n",
    "from typing import Any\n\nfrom waiting_heartbeat_capsule_integrity import (\n"
    "    capsule_claims_verified,\n"
    "    verified_capsule_binding_errors,\n"
    "    verified_capsule_is_bound,\n"
    ")\n",
)
replace_once(
    generator,
    '''def capsule_is_verified(c: dict[str, Any] | None) -> bool:\n    if not c:\n        return False\n    txid = c.get("txid") or c.get("tx_id") or c.get("arweave_txid") or c.get("arweave_tx_id")\n    status = c.get("result") or c.get("status")\n    return bool(txid) and c.get("hash_match") is True and status in {"uploaded", "success", "arweave_archived"}\n''',
    '''def capsule_is_verified(c: dict[str, Any] | None) -> bool:\n    if not c:\n        return False\n    heartbeat_id = c.get("heartbeat_id")\n    if not isinstance(heartbeat_id, str) or not heartbeat_id:\n        return False\n    return verified_capsule_is_bound(\n        c,\n        capsule_path=CAPSULES_DIR / f"{heartbeat_id}.capsule.json",\n        repository_root=ROOT,\n    )\n\n\ndef require_verified_capsule_bindings(capsules: list[dict[str, Any]]) -> None:\n    """Fail generation if any result claims verification without real binding."""\n    failures: list[str] = []\n    for capsule in capsules:\n        if not capsule_claims_verified(capsule):\n            continue\n        heartbeat_id = capsule.get("heartbeat_id")\n        capsule_path = CAPSULES_DIR / f"{heartbeat_id}.capsule.json"\n        for error in verified_capsule_binding_errors(\n            capsule,\n            capsule_path=capsule_path,\n            repository_root=ROOT,\n        ):\n            failures.append(f"{heartbeat_id}: {error}")\n    if failures:\n        raise SystemExit("Invalid verified Waiting Heartbeat capsule evidence:\\n- " + "\\n- ".join(failures))\n''',
)
replace_once(
    generator,
    "    capsules = load_capsules()\n    ots = read_json(OTS_LATEST, {})\n",
    "    capsules = load_capsules()\n    require_verified_capsule_bindings(capsules)\n    ots = read_json(OTS_LATEST, {})\n",
)

test = Path("scripts/test_waiting_heartbeat_summary_metrics.py")
replace_once(test, "import json\n", "import hashlib\nimport json\nimport tempfile\n")
replace_once(
    test,
    'CAPSULE_WORKFLOW = ROOT / ".github" / "workflows" / "waiting-heartbeat-capsule.yml"\n',
    'CAPSULE_WORKFLOW = ROOT / ".github" / "workflows" / "waiting-heartbeat-capsule.yml"\n'
    'STATUS_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "waiting-heartbeat-status-sync.yml"\n',
)
replace_once(
    test,
    '''def test_capsule_builder_recognizes_existing_result_states() -> None:\n    builder = load_capsule_builder_module()\n    require(builder.capsule_is_verified({"status": "uploaded", "arweave_txid": "txid", "hash_match": True}), "verified result should skip upload")\n    require(builder.capsule_needs_readback_repair({"status": "posted_pending_readback", "arweave_txid": "txid", "hash_match": False, "retryable": True}), "pending result should request readback repair")\n''',
    '''def test_capsule_builder_recognizes_existing_result_states() -> None:\n    builder = load_capsule_builder_module()\n    require(not builder.capsule_is_verified({"status": "uploaded", "arweave_txid": "x" * 43, "hash_match": True}), "self-declared verified result without local evidence must fail closed")\n    require(builder.capsule_needs_readback_repair({"status": "posted_pending_readback", "arweave_txid": "txid", "hash_match": False, "retryable": True}), "pending result should request readback repair")\n''',
)
insert = '''\n\ndef test_verified_capsule_binds_exact_bytes_and_final_record() -> None:\n    builder = load_capsule_builder_module()\n    with tempfile.TemporaryDirectory(prefix="heartbeat-capsule-integrity-") as tmp_value:\n        tmp = Path(tmp_value)\n        record_id = "R-000000001"\n        heartbeat_id = "hwb-20260712"\n        record_path = tmp / "record-chain" / "records" / f"{record_id}.json"\n        record_path.parent.mkdir(parents=True)\n        record = {\n            "record_id": record_id,\n            "record_index": 1,\n            "record_sha256": "a" * 64,\n            "record_type": "context_insufficient_notice",\n            "assigned_at": "2026-07-12T00:00:00Z",\n            "system_waiting_heartbeat": {"heartbeat_id": heartbeat_id},\n        }\n        record_path.write_text(json.dumps(record) + "\\n", encoding="utf-8")\n        capsule_path = tmp / "record-chain" / "heartbeat" / "capsules" / f"{heartbeat_id}.capsule.json"\n        capsule_path.parent.mkdir(parents=True)\n        capsule = {\n            "schema": "trinityaccord.waiting-heartbeat-arweave-capsule.v1",\n            "heartbeat_id": heartbeat_id,\n            "heartbeat_record": {\n                "record_id": record_id,\n                "record_index": 1,\n                "record_sha256": "a" * 64,\n                "record_type": "context_insufficient_notice",\n                "assigned_at": "2026-07-12T00:00:00Z",\n                "path": f"record-chain/records/{record_id}.json",\n            },\n        }\n        capsule_path.write_text(json.dumps(capsule) + "\\n", encoding="utf-8")\n        payload_sha = hashlib.sha256(capsule_path.read_bytes()).hexdigest()\n        result = {\n            "schema": "trinityaccord.waiting-heartbeat-arweave-upload-result.v1",\n            "heartbeat_id": heartbeat_id,\n            "status": "uploaded",\n            "arweave_txid": "x" * 43,\n            "payload_sha256": payload_sha,\n            "data_sha256": payload_sha,\n            "readback_sha256": payload_sha,\n            "hash_match": True,\n        }\n        old_root = builder.ROOT\n        try:\n            builder.ROOT = tmp\n            require(builder.capsule_is_verified(result, capsule_path=capsule_path), "fully bound verified capsule should be accepted")\n            capsule_path.write_text(json.dumps({**capsule, "created_at": "tampered"}) + "\\n", encoding="utf-8")\n            require(not builder.capsule_is_verified(result, capsule_path=capsule_path), "changed local capsule bytes must invalidate verified result")\n        finally:\n            builder.ROOT = old_root\n\n\ndef test_current_verified_capsules_all_bind_to_repository_evidence() -> None:\n    generator = load_generator_module()\n    generator.require_verified_capsule_bindings(generator.load_capsules())\n\n\ndef test_status_sync_regenerates_after_rebase() -> None:\n    text = STATUS_SYNC_WORKFLOW.read_text(encoding="utf-8")\n    rebase_pos = text.find("git rebase origin/main")\n    regenerate_pos = text.find("regenerate_waiting_status_artifacts", rebase_pos)\n    amend_pos = text.find("git commit --amend --no-edit", regenerate_pos)\n    require(rebase_pos >= 0, "status sync must rebase when main advances")\n    require(regenerate_pos > rebase_pos, "status sync must regenerate derived state after rebase")\n    require(amend_pos > regenerate_pos, "status sync must amend regenerated state before retrying push")\n'''
replace_once(
    test,
    "def test_capsule_workflow_preserves_upload_result_before_status_update() -> None:\n",
    insert + "\n\ndef test_capsule_workflow_preserves_upload_result_before_status_update() -> None:\n",
)
replace_once(
    test,
    "    test_capsule_builder_recognizes_existing_result_states()\n    test_capsule_workflow_preserves_upload_result_before_status_update()\n",
    "    test_capsule_builder_recognizes_existing_result_states()\n"
    "    test_verified_capsule_binds_exact_bytes_and_final_record()\n"
    "    test_current_verified_capsules_all_bind_to_repository_evidence()\n"
    "    test_status_sync_regenerates_after_rebase()\n"
    "    test_capsule_workflow_preserves_upload_result_before_status_update()\n",
)
print("round4 remaining source transformations applied")
