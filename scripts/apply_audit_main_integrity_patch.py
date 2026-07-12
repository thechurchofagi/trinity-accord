#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one exact replacement, found {count}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def regex_replace_once(path: str, pattern: str, replacement: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S | re.M)
    if count != 1:
        raise SystemExit(f"{path}: expected one regex replacement, found {count}")
    target.write_text(updated, encoding="utf-8")


# 1. Keep Gateway rejection fields identical to the append signature-domain stripper.
replace_once(
    "apps/record_chain_intake_gateway/app.py",
    "from apps.record_chain_intake_gateway.gateway.authorship import (\n    strip_authorship_for_signing,\n    strip_unsigned_projection_fields,\n)",
    "from apps.record_chain_intake_gateway.gateway.authorship import (\n    UNSIGNED_PROJECTION_FIELDS,\n    strip_authorship_for_signing,\n    strip_unsigned_projection_fields,\n)",
)
replace_once(
    "apps/record_chain_intake_gateway/app.py",
    '''_UNSIGNED_CLIENT_PROJECTION_FIELDS = frozenset({
    "actor_identity",
    "boundary",
    "server_normalization",
    "server_append_metadata",
    "append_assigned_metadata",
    "authorship_verification_status",
    "record_id",
    "record_index",
    "assigned_at",
    "previous_record_sha256",
    "content_sha256",
    "record_sha256",
    "chain_id",
})''',
    '''_UNSIGNED_CLIENT_PROJECTION_FIELDS = frozenset(UNSIGNED_PROJECTION_FIELDS)''',
)

# 2. Reject malformed classification-update targets at public validation time.
replace_once(
    "apps/record_chain_intake_gateway/gateway/validation.py",
    '''            target_sha = content.get("target_record_sha256")
            if isinstance(target_sha, str) and not re.fullmatch(r"[a-f0-9]{64}", target_sha):
                missing(
                    "INVALID_CLASSIFICATION_TARGET_SHA",
                    "draft.classification_update_content.target_record_sha256",
                    "target_record_sha256 must be a 64-character lowercase hex SHA-256",
                )''',
    '''            target_id = content.get("target_record_id")
            if isinstance(target_id, str) and not re.fullmatch(r"R-[0-9]{9}", target_id):
                missing(
                    "INVALID_CLASSIFICATION_TARGET_ID",
                    "draft.classification_update_content.target_record_id",
                    "target_record_id must use canonical R-000000000 format",
                )

            target_sha = content.get("target_record_sha256")
            if isinstance(target_sha, str) and not re.fullmatch(r"[a-f0-9]{64}", target_sha):
                missing(
                    "INVALID_CLASSIFICATION_TARGET_SHA",
                    "draft.classification_update_content.target_record_sha256",
                    "target_record_sha256 must be a 64-character lowercase hex SHA-256",
                )''',
)

# 3. Fail closed for every classification-update target-binding branch in final verification.
replace_once(
    "scripts/trinity_record_chain.py",
    '''                # B.6: Classification update target binding
                if rtype == "classification_update":
                    cu_content = obj.get("classification_update_content")
                    if isinstance(cu_content, dict):
                        target_rid = cu_content.get("target_record_id")
                        target_sha = cu_content.get("target_record_sha256")
                        if isinstance(target_rid, str) and re.fullmatch(r"R-[0-9]{9}", target_rid):
                            target_path = RECORDS / f"{target_rid}.json"
                            if target_path.exists():
                                target_rec = read_json(target_path)
                                if target_rec.get("record_sha256") != target_sha:
                                    errors.append(f"{p}: classification_update target_record_sha256 mismatch for {target_rid}")''',
    '''                # B.6: Classification update target binding
                if rtype == "classification_update":
                    cu_content = obj.get("classification_update_content")
                    if not isinstance(cu_content, dict):
                        errors.append(f"{p}: classification_update requires classification_update_content")
                    else:
                        target_rid = cu_content.get("target_record_id")
                        target_sha = cu_content.get("target_record_sha256")
                        if not isinstance(target_rid, str) or not re.fullmatch(r"R-[0-9]{9}", target_rid):
                            errors.append(f"{p}: classification_update requires valid target_record_id")
                        elif not isinstance(target_sha, str) or not re.fullmatch(r"[a-f0-9]{64}", target_sha):
                            errors.append(f"{p}: classification_update requires valid target_record_sha256")
                        else:
                            target_path = RECORDS / f"{target_rid}.json"
                            if not target_path.exists():
                                errors.append(f"{p}: classification_update target record {target_rid} does not exist")
                            else:
                                target_rec = read_json(target_path)
                                if target_rec.get("record_sha256") != target_sha:
                                    errors.append(f"{p}: classification_update target_record_sha256 mismatch for {target_rid}")''',
)

# 4. Verify every chain-tip field used by downstream status/OTS/archive consumers.
replace_once(
    "scripts/trinity_record_chain.py",
    '''    if CHAIN_TIP.exists():
        tip = read_json(CHAIN_TIP)
        if records:
            latest = read_json(records[-1])
            if tip.get("latest_record_sha256") != latest.get("record_sha256"):
                errors.append("chain-tip latest_record_sha256 mismatch")
            if tip.get("latest_record_index") != latest.get("record_index"):
                errors.append("chain-tip latest_record_index mismatch")
        else:
            # No native records: tip must reflect Genesis-only state
            if tip.get("latest_record_sha256") is not None:
                errors.append("chain-tip latest_record_sha256 should be null when no native records exist")
            if tip.get("latest_record_index") != 0:
                errors.append("chain-tip latest_record_index should be 0 when no native records exist")
            genesis_path = GENESIS / "genesis-batch-manifest.json"
            if genesis_path.exists():
                genesis_hash = read_json(genesis_path).get("batch_manifest_sha256")
                if tip.get("genesis_batch_manifest_sha256") != genesis_hash:
                    errors.append("chain-tip genesis_batch_manifest_sha256 mismatch")
                if tip.get("latest_batch_manifest_sha256") != genesis_hash:
                    errors.append("chain-tip latest_batch_manifest_sha256 should equal genesis hash when no later batches exist")
    return errors''',
    '''    if CHAIN_TIP.exists():
        tip = read_json(CHAIN_TIP)
        if tip.get("chain_id") != CHAIN_ID:
            errors.append("chain-tip chain_id mismatch")
        if records:
            latest = read_json(records[-1])
            if tip.get("latest_record_id") != latest.get("record_id"):
                errors.append("chain-tip latest_record_id mismatch")
            if tip.get("latest_record_sha256") != latest.get("record_sha256"):
                errors.append("chain-tip latest_record_sha256 mismatch")
            if tip.get("latest_record_index") != latest.get("record_index"):
                errors.append("chain-tip latest_record_index mismatch")
            if tip.get("native_record_count") != len(records):
                errors.append("chain-tip native_record_count mismatch")
        else:
            # No native records: tip must reflect Genesis-only state
            if tip.get("latest_record_id") is not None:
                errors.append("chain-tip latest_record_id should be null when no native records exist")
            if tip.get("latest_record_sha256") is not None:
                errors.append("chain-tip latest_record_sha256 should be null when no native records exist")
            if tip.get("latest_record_index") != 0:
                errors.append("chain-tip latest_record_index should be 0 when no native records exist")
            if tip.get("native_record_count") != 0:
                errors.append("chain-tip native_record_count should be 0 when no native records exist")
            genesis_path = GENESIS / "genesis-batch-manifest.json"
            if genesis_path.exists():
                genesis_hash = read_json(genesis_path).get("batch_manifest_sha256")
                if tip.get("genesis_batch_manifest_sha256") != genesis_hash:
                    errors.append("chain-tip genesis_batch_manifest_sha256 mismatch")
                if tip.get("latest_batch_manifest_sha256") != genesis_hash:
                    errors.append("chain-tip latest_batch_manifest_sha256 should equal genesis hash when no later batches exist")
    return errors''',
)

# 5. Bind Genesis and every later batch manifest to the actual immutable records.
replace_once(
    "scripts/trinity_record_chain.py",
    '''    if mf.get("record_count") != len(records):
        errors.append("genesis record_count mismatch")
    if mf.get("merkle_root_sha256") != merkle_root(hashes):''',
    '''    if mf.get("record_count") != len(records):
        errors.append("genesis record_count mismatch")
    if mf.get("record_sha256_list") != hashes:
        errors.append("genesis record_sha256_list mismatch")
    if mf.get("merkle_root_sha256") != merkle_root(hashes):''',
)
regex_replace_once(
    "scripts/trinity_record_chain.py",
    r'''def verify_batches\(\) -> list\[str\]:\n.*?\n    return errors\n\n\n''',
    '''def verify_batches() -> list[str]:
    errors: list[str] = []
    prior_hash = None
    genesis = GENESIS / "genesis-batch-manifest.json"
    if genesis.exists():
        prior_hash = read_json(genesis).get("batch_manifest_sha256")

    manifests = existing_batch_manifests()
    covered_record_ids: set[str] = set()
    for mf_path in manifests:
        mf = read_json(mf_path)
        record_ids = mf.get("record_ids")
        hashes = mf.get("record_sha256_list")

        if mf.get("schema") != "trinityaccord.record-batch-manifest.v1":
            errors.append(f"{mf_path}: schema mismatch")
        if mf.get("chain_id") != CHAIN_ID:
            errors.append(f"{mf_path}: chain_id mismatch")
        if mf.get("batch_id") != mf_path.parent.name:
            errors.append(f"{mf_path}: batch_id/path mismatch")
        if not isinstance(record_ids, list) or not all(isinstance(rid, str) for rid in record_ids):
            errors.append(f"{mf_path}: record_ids must be a string array")
            record_ids = []
        if not isinstance(hashes, list) or not all(isinstance(value, str) for value in hashes):
            errors.append(f"{mf_path}: record_sha256_list must be a string array")
            hashes = []
        if mf.get("record_count") != len(record_ids) or len(record_ids) != len(hashes):
            errors.append(f"{mf_path}: record_count/list length mismatch")

        first_index = mf.get("first_record_index")
        last_index = mf.get("last_record_index")
        if not isinstance(first_index, int) or not isinstance(last_index, int) or first_index < 1 or last_index < first_index:
            errors.append(f"{mf_path}: invalid first/last record index")
            expected_ids: list[str] = []
        else:
            expected_ids = [record_id(index) for index in range(first_index, last_index + 1)]
            if record_ids != expected_ids:
                errors.append(f"{mf_path}: record_ids do not match first/last record index range")

        actual_hashes: list[str] = []
        for rid in record_ids:
            if rid in covered_record_ids:
                errors.append(f"{mf_path}: duplicate record id across batches: {rid}")
            covered_record_ids.add(rid)
            record_path = RECORDS / f"{rid}.json"
            if not record_path.exists():
                errors.append(f"{mf_path}: referenced record does not exist: {rid}")
                continue
            actual = read_json(record_path)
            if actual.get("record_id") != rid:
                errors.append(f"{mf_path}: referenced record_id mismatch: {rid}")
            actual_hashes.append(actual.get("record_sha256"))

        if len(actual_hashes) == len(hashes) and actual_hashes != hashes:
            errors.append(f"{mf_path}: record_sha256_list does not match referenced records")
        if hashes:
            if mf.get("first_record_sha256") != hashes[0]:
                errors.append(f"{mf_path}: first_record_sha256 mismatch")
            if mf.get("last_record_sha256") != hashes[-1]:
                errors.append(f"{mf_path}: last_record_sha256 mismatch")
        if mf.get("merkle_root_sha256") != merkle_root(hashes):
            errors.append(f"{mf_path}: merkle root mismatch")
        if mf.get("previous_batch_manifest_sha256") != prior_hash:
            errors.append(f"{mf_path}: previous_batch_manifest_sha256 mismatch")
        if mf.get("batch_manifest_sha256") != manifest_hash(mf):
            errors.append(f"{mf_path}: batch_manifest_sha256 mismatch")
        prior_hash = mf.get("batch_manifest_sha256")

    if CHAIN_TIP.exists():
        tip = read_json(CHAIN_TIP)
        if manifests:
            latest_manifest = read_json(manifests[-1])
            if tip.get("latest_batch_id") != latest_manifest.get("batch_id"):
                errors.append("chain-tip latest_batch_id mismatch")
            if tip.get("latest_batch_manifest_sha256") != latest_manifest.get("batch_manifest_sha256"):
                errors.append("chain-tip latest_batch_manifest_sha256 mismatch")
        elif genesis.exists():
            genesis_hash = read_json(genesis).get("batch_manifest_sha256")
            if tip.get("latest_batch_manifest_sha256") != genesis_hash:
                errors.append("chain-tip latest_batch_manifest_sha256 should equal genesis hash when no native batches exist")
    return errors


''',
)

# 6. Replace the fake-green empty deep-integrity group and move static supply-chain gates into PR CI.
replace_once(
    "scripts/run_ci_group.py",
    '''        ["python3", "scripts/test_record_chain_write_path_guard_contract.py"],
        ["python3", "scripts/test_readback_hash_parity.py"],''',
    '''        ["python3", "scripts/test_record_chain_write_path_guard_contract.py"],
        ["python3", "scripts/test_record_chain_verifier_invariants.py"],
        ["python3", "scripts/test_deep_integrity_group_nonempty.py"],
        ["python3", "scripts/test_action_pinning.py"],
        ["python3", "scripts/test_runner_image_pinning.py"],
        ["python3", "scripts/test_python_dependency_pinning.py"],
        ["python3", "scripts/test_node_dependency_pinning.py"],
        ["python3", "scripts/test_toolchain_provenance.py"],
        ["python3", "scripts/test_write_workflow_toolchain_provenance.py"],
        ["python3", "scripts/test_no_remote_script_execution.py"],
        ["python3", "scripts/test_system_tool_version_recording.py"],
        ["python3", "scripts/test_readback_hash_parity.py"],''',
)
replace_once(
    "scripts/run_ci_group.py",
    '    "readback-integrity": [],',
    '''    "readback-integrity": [
        ["python3", "scripts/test_readback_hash_parity.py"],
        ["python3", "scripts/test_readback_hash_policy.py"],
        ["python3", "scripts/test_builder_oath_readback_canonical_output.py"],
    ],''',
)

# 7. Add behavioral regressions.
(ROOT / "apps/record_chain_intake_gateway/tests/test_classification_update_target_binding.py").write_text('''from apps.record_chain_intake_gateway.gateway.validation import validate_record_type_specific_content


def _draft(target_id: str) -> dict:
    return {
        "authorization_context": {"authorization_scope": "create_classification_update_record"},
        "classification_update_content": {
            "target_record_id": target_id,
            "target_record_sha256": "a" * 64,
            "previous_classification": "old",
            "new_classification": "new",
            "classification_reason": "review",
            "evidence_or_review_basis": "record review",
        },
    }


def test_classification_update_rejects_noncanonical_target_id() -> None:
    diagnostics = validate_record_type_specific_content("classification_update", _draft("not-a-record"))
    assert "INVALID_CLASSIFICATION_TARGET_ID" in {diag.code for diag in diagnostics}


def test_classification_update_accepts_canonical_target_id_shape() -> None:
    diagnostics = validate_record_type_specific_content("classification_update", _draft("R-000000001"))
    assert "INVALID_CLASSIFICATION_TARGET_ID" not in {diag.code for diag in diagnostics}
''', encoding="utf-8")

(ROOT / "apps/record_chain_intake_gateway/tests/test_client_projection_field_alignment.py").write_text('''from apps.record_chain_intake_gateway.app import _UNSIGNED_CLIENT_PROJECTION_FIELDS
from apps.record_chain_intake_gateway.gateway.authorship import UNSIGNED_PROJECTION_FIELDS


def test_gateway_rejects_every_field_removed_from_signed_pending_domain() -> None:
    assert _UNSIGNED_CLIENT_PROJECTION_FIELDS == UNSIGNED_PROJECTION_FIELDS
''', encoding="utf-8")

(ROOT / "scripts/test_record_chain_verifier_invariants.py").write_text('''#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "trinity_record_chain.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load_module():
    spec = importlib.util.spec_from_file_location("trinity_record_chain_invariant_test", MODULE_PATH)
    require(spec is not None and spec.loader is not None, "could not load trinity_record_chain")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_record(module, index: int) -> dict:
    record = {
        "schema": "trinityaccord.record-chain-entry.v1",
        "chain_id": module.CHAIN_ID,
        "record_type": "context_insufficient_notice",
        "record_index": index,
        "record_id": module.record_id(index),
        "assigned_at": "2026-07-12T00:00:00Z",
        "previous_record_sha256": None,
        "reason": "invariant test",
        "boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }
    record["content_sha256"] = module.content_hash(record)
    record["record_sha256"] = module.record_hash(record)
    return record


def test_chain_tip_fields(module, root: Path) -> None:
    records = root / "records"
    records.mkdir(parents=True)
    tip_path = root / "chain-tip.json"
    record = make_record(module, 1)
    module.write_json(records / "R-000000001.json", record)
    module.write_json(tip_path, {
        "chain_id": module.CHAIN_ID,
        "latest_record_id": "R-999999999",
        "latest_record_sha256": record["record_sha256"],
        "latest_record_index": 1,
        "native_record_count": 999,
    })
    module.RECORDS = records
    module.CHAIN_TIP = tip_path
    errors = module.verify_native_records()
    require("chain-tip latest_record_id mismatch" in errors, "verify must reject wrong chain-tip latest_record_id")
    require("chain-tip native_record_count mismatch" in errors, "verify must reject wrong chain-tip native_record_count")


def test_batch_binding(module, root: Path) -> None:
    records = root / "batch-records"
    batches = root / "batches"
    genesis = root / "genesis"
    records.mkdir(parents=True)
    (batches / "batch-000001").mkdir(parents=True)
    genesis.mkdir(parents=True)
    record = make_record(module, 1)
    module.write_json(records / "R-000000001.json", record)
    genesis_hash = "b" * 64
    module.write_json(genesis / "genesis-batch-manifest.json", {"batch_manifest_sha256": genesis_hash})
    manifest = {
        "schema": "trinityaccord.record-batch-manifest.v1",
        "batch_id": "batch-000001",
        "chain_id": module.CHAIN_ID,
        "created_at": "2026-07-12T00:00:00Z",
        "record_count": 1,
        "record_ids": ["R-999999999"],
        "first_record_index": 1,
        "last_record_index": 1,
        "first_record_sha256": record["record_sha256"],
        "last_record_sha256": record["record_sha256"],
        "record_sha256_list": [record["record_sha256"]],
        "merkle_root_sha256": module.merkle_root([record["record_sha256"]]),
        "previous_batch_manifest_sha256": genesis_hash,
        "batch_manifest_sha256": None,
        "ots": {"stamped": False, "ots_file": None, "upgraded": False},
        "arweave_archive": {"enabled": False},
        "non_amending_boundary": True,
    }
    manifest["batch_manifest_sha256"] = module.manifest_hash(manifest)
    module.write_json(batches / "batch-000001" / "manifest.json", manifest)
    module.RECORDS = records
    module.BATCHES = batches
    module.GENESIS = genesis
    module.CHAIN_TIP = root / "missing-tip.json"
    errors = module.verify_batches()
    require(any("record_ids do not match" in error for error in errors), "verify must bind batch record_ids to index range")
    require(any("referenced record does not exist" in error for error in errors), "verify must bind batch entries to real records")


def main() -> int:
    module = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        test_chain_tip_fields(module, root / "tip")
        test_batch_binding(module, root / "batch")
    print("PASS: record-chain verifier invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")

(ROOT / "scripts/test_deep_integrity_group_nonempty.py").write_text('''#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_ci_group.py"
DEEP_GROUPS = {
    "claim-gate",
    "echo-archive",
    "supply-chain",
    "trust-root",
    "chronicle",
    "readback-integrity",
    "agent-start-docs",
    "verification-index",
    "pages-build",
}

spec = importlib.util.spec_from_file_location("run_ci_group_contract", RUNNER)
if spec is None or spec.loader is None:
    raise SystemExit("could not load run_ci_group")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
missing = sorted(DEEP_GROUPS - set(module.GROUPS))
empty = sorted(name for name in DEEP_GROUPS if name in module.GROUPS and not module.GROUPS[name])
if missing or empty:
    raise SystemExit(f"Deep Integrity has missing/empty groups: missing={missing}, empty={empty}")
print("PASS: every Deep Integrity matrix group executes at least one test")
''', encoding="utf-8")

print("Audit integrity patch applied.")
