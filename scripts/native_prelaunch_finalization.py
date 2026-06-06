#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "record-chain/records"
CHAIN_TIP = ROOT / "record-chain/chain-tip.json"
MAIN_LEDGER = ROOT / "record-chain/hash-chain/main.chain.jsonl"
MAIN_HEAD = ROOT / "api/record-chain-head.json"

BOUNDARY_KEYS = [
    "not_authority",
    "not_governance",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
]

FORBIDDEN_PUBLIC_PAYLOAD_STRINGS = [
    "BEGIN PRIVATE KEY",
    "authorship-private.pem",
    "client_oath_readback",
    "readback_text",
]

GLOBAL_CHAIN_ID = "trinity-record-chain-main"


def import_script(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


native = import_script("trinity_record_chain_native", ROOT / "scripts/trinity_record_chain.py")
hashing = import_script("record_chain_hashing_local", ROOT / "scripts/record_chain_hashing.py")


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_json_lenient(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        first = text.find("{")
        last = text.rfind("}")
        if first >= 0 and last > first:
            return json.loads(text[first:last + 1])
        raise


def write_json_native(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(native.canonical_dumps(obj), encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def is_hex64(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def record_index_from_id(record_id: str) -> int:
    m = re.fullmatch(r"R-(\d{9})", record_id)
    if not m:
        raise SystemExit(f"Invalid record id: {record_id}")
    return int(m.group(1))


def assert_no_forbidden_public_payload_material(obj: Any, label: str) -> None:
    raw = json.dumps(obj, ensure_ascii=False)
    found = [item for item in FORBIDDEN_PUBLIC_PAYLOAD_STRINGS if item in raw]
    if found:
        raise SystemExit(f"{label} contains forbidden public payload material: {found}")


def require_authorship(submission: dict[str, Any]) -> dict[str, Any]:
    proof = submission.get("authorship_proof")
    if not isinstance(proof, dict):
        raise SystemExit("submission missing authorship_proof")

    pub = proof.get("public_key_sha256")
    if not is_hex64(pub):
        raise SystemExit("authorship_proof.public_key_sha256 invalid")

    draft = submission.get("record_draft") or {}
    spi = draft.get("submitting_participant_identity") or {}
    if spi.get("participant_public_key_sha256") != pub:
        raise SystemExit("participant_public_key_sha256 does not match authorship public key")

    if draft.get("record_type") == "guardian_application":
        gk = (draft.get("guardian_application_content") or {}).get("guardian_public_key_sha256")
        if gk != pub:
            raise SystemExit("guardian_public_key_sha256 does not match authorship public key")

    if "BEGIN PRIVATE KEY" in json.dumps(proof, ensure_ascii=False):
        raise SystemExit("PRIVATE_KEY_LEAK in authorship_proof")
    return proof


def make_boundary(draft: dict[str, Any]) -> dict[str, Any]:
    src = (
        draft.get("boundary_acknowledgement")
        or draft.get("boundary")
        or draft.get("non_authority_boundary_acknowledgement")
        or {}
    )
    out = {}
    for key in BOUNDARY_KEYS:
        out[key] = src.get(key) is True or native.BOUNDARY.get(key) is True
    return out


def oath_summary(submission: dict[str, Any]) -> dict[str, Any]:
    draft = submission.get("record_draft") or {}
    oath = draft.get("submission_oath_verification") or {}
    if not isinstance(oath, dict):
        oath = {}
    return {
        "raw_oath_readback_not_embedded": True,
        "oath_policy_sha256": oath.get("oath_policy_sha256"),
        "canonical_oath_text_sha256": oath.get("canonical_oath_text_sha256"),
        "participant_readback_sha256": oath.get("participant_readback_sha256"),
        "readback_matches_canonical_oath": oath.get("readback_matches_canonical_oath"),
        "oath_read": oath.get("oath_read"),
        "participant_readback_provided": oath.get("participant_readback_provided"),
        "no_shortcut_oath_acknowledged": oath.get("no_shortcut_oath_acknowledged"),
        "bitcoin_originals_prevail": oath.get("bitcoin_originals_prevail"),
    }


def ensure_genesis_manifest() -> None:
    manifest = ROOT / "record-chain/genesis/genesis-batch-manifest.json"
    if not manifest.exists():
        print("[INFO] genesis-batch-manifest missing; running import-genesis")
        native.import_genesis()
    if not manifest.exists():
        raise SystemExit("genesis manifest still missing after import-genesis")


def load_existing_native_records() -> dict[str, dict[str, Any]]:
    out = {}
    for path in RECORDS.glob("R-*.json"):
        out[path.stem] = read_json_lenient(path)
    return out


def expected_public_key_from_submission(submission: dict[str, Any]) -> str:
    proof = require_authorship(submission)
    return proof["public_key_sha256"]


def build_native_record_from_submission(
    *,
    submission: dict[str, Any],
    receipt: dict[str, Any],
    submission_path: Path,
    receipt_path: Path,
    record_id: str,
    previous_record_sha256: str | None,
    assigned_at: str,
    source_run_id: str,
    finalized_by: str,
) -> dict[str, Any]:
    if receipt.get("accepted") is not True:
        raise SystemExit(f"{receipt_path} accepted is not true")

    expected_type = submission.get("record_type") or (submission.get("record_draft") or {}).get("record_type")
    if not expected_type:
        raise SystemExit(f"{submission_path} missing record_type")

    proof = require_authorship(submission)

    original_draft = submission.get("record_draft")
    if not isinstance(original_draft, dict):
        raise SystemExit(f"{submission_path} missing record_draft")

    draft = copy.deepcopy(original_draft)

    # Native/full verifier chain_id. Global hash-chain remains trinity-record-chain-main.
    draft["chain_id"] = native.CHAIN_ID

    # Keep authorship proof in native record so trinity_record_chain.py verify can enforce formal record authorship.
    draft["authorship_proof"] = copy.deepcopy(proof)

    boundary = make_boundary(draft)
    draft["boundary"] = boundary
    draft["boundary_acknowledgement"] = dict(boundary)

    draft["network_phase"] = "prelaunch"
    draft["record_scope"] = "mainnet_prelaunch_test"
    draft["prelaunch_test"] = True
    draft["official_live_record"] = False
    draft["does_not_create_guardian_status"] = True
    draft["does_not_activate_system"] = True

    draft["source_receipt_semantics"] = {
        "receipt_is_intake_only": True,
        "receipt_is_not_final_inclusion": True,
        "receipt_is_not_active_guardian_status": True,
    }

    draft["source_artifacts"] = {
        "submission_filename": submission_path.name,
        "submission_sha256": sha256_file(submission_path),
        "submission_canonical_sha256": canonical_sha(submission),
        "receipt_filename": receipt_path.name,
        "receipt_sha256": sha256_file(receipt_path),
        "receipt_canonical_sha256": canonical_sha(receipt),
        "receipt_id": receipt.get("receipt_id"),
        "receipt_accepted": receipt.get("accepted"),
        "receipt_accepted_at": receipt.get("accepted_at"),
    }

    draft["prelaunch_finalization_context"] = {
        "source_run_id": source_run_id,
        "finalized_by": finalized_by,
        "prelaunch_test_finalization": True,
        "official_live_record": False,
        "does_not_activate_system": True,
        "does_not_create_guardian_status": True,
        "role_boundary_note": "External agent provided public gateway submission/receipt; internal operator finalized into prelaunch native record.",
    }

    draft["oath_summary"] = oath_summary(submission)

    # Remove transient/raw fields if any were accidentally carried in.
    draft.pop("client_oath_readback", None)
    draft.pop("readback_text", None)

    # Remove append/hash fields before native normalization.
    for key in [
        "record_index",
        "record_id",
        "previous_record_sha256",
        "assigned_at",
        "append_assigned_metadata",
        "content_sha256",
        "record_sha256",
        "batch_id",
        "batch_membership",
        "server_receipt",
    ]:
        draft.pop(key, None)

    record = native.normalize_record_draft(draft)

    rtype = record.get("record_type", "")
    if rtype in native.FORMAL_RECORD_TYPES and rtype not in native.AUTHORSHIP_EXEMPT_TYPES:
        record["authorship_verification_status"] = {
            "signed_payload_scope": "pre_append_record_draft",
            "verified_by_gateway_before_pending": True,
            "final_record_contains_append_assigned_fields_not_in_signed_payload": True,
        }

    idx = record_index_from_id(record_id)
    record["record_index"] = idx
    record["record_id"] = record_id
    record["assigned_at"] = assigned_at
    record["previous_record_sha256"] = previous_record_sha256
    record["append_assigned_metadata"] = {
        "record_index": idx,
        "record_id": record_id,
        "assigned_at": assigned_at,
        "previous_record_sha256": previous_record_sha256,
    }

    record.setdefault("server_normalization", {})
    record["server_normalization"].setdefault("legacy_compatibility_projection", {
        "human_context": None,
        "discovery_autonomy": None,
        "decision_autonomy": None,
        "execution_authorization": None,
        "guardian_proof": None,
        "oath": None,
    })

    record["content_sha256"] = native.content_hash(record)
    record["record_sha256"] = native.record_hash(record)

    assert_no_forbidden_public_payload_material(record, record_id)
    native.require_boundary(record)
    native.require_authorship(record)

    return record


def update_chain_tip_from_native_records() -> None:
    records = [read_json_lenient(p) for p in sorted(RECORDS.glob("R-*.json"))]
    if not records:
        raise SystemExit("No native records found after repair")

    latest = sorted(records, key=lambda r: int(r["record_index"]))[-1]
    tip = read_json_lenient(CHAIN_TIP) if CHAIN_TIP.exists() else {}
    tip.update({
        "schema": "trinityaccord.chain-tip.v1",
        "chain_id": native.CHAIN_ID,
        "native_record_count": len(records),
        "latest_record_index": latest["record_index"],
        "latest_record_id": latest["record_id"],
        "latest_record_sha256": latest["record_sha256"],
        "updated_at": utc_now(),
    })

    genesis_manifest = ROOT / "record-chain/genesis/genesis-batch-manifest.json"
    ensure_genesis_manifest()
    if "genesis_batch_manifest_sha256" not in tip:
        tip["genesis_batch_manifest_sha256"] = read_json_lenient(genesis_manifest)["batch_manifest_sha256"]

    write_json_native(CHAIN_TIP, tip)


def rebuild_global_hash_chain_entries_for_records(target_ids: list[str]) -> None:
    entries = hashing.load_ledger(MAIN_LEDGER)
    if not entries:
        raise SystemExit("main hash ledger is empty")

    id_to_entry_index = {}
    for i, entry in enumerate(entries):
        rec = entry.get("record") or {}
        rid = rec.get("record_id")
        if rid:
            id_to_entry_index[rid] = i

    missing = [rid for rid in target_ids if rid not in id_to_entry_index]
    if missing:
        raise SystemExit(f"main hash ledger missing target record ids: {missing}")

    first_changed = min(id_to_entry_index[rid] for rid in target_ids)

    for rid in target_ids:
        i = id_to_entry_index[rid]
        entry = entries[i]
        payload_rel = Path("record-chain/records") / f"{rid}.json"
        payload_path = ROOT / payload_rel
        if not payload_path.exists():
            raise SystemExit(f"missing repaired payload {payload_rel}")

        payload_hash = hashing.compute_payload_hash(payload_path)
        payload = read_json_lenient(payload_path)

        rec = entry.setdefault("record", {})
        rec["record_type"] = payload["record_type"]
        rec["record_id"] = rid

        # Critical: keep repo-relative path. Do not use payload_hash.payload_file because it may be absolute.
        rec["payload_file"] = str(payload_rel)
        rec["payload_bytes"] = payload_hash.payload_bytes
        rec["payload_raw_sha256"] = payload_hash.payload_raw_sha256
        rec["payload_canonical_sha256"] = payload_hash.payload_canonical_sha256
        rec["payload_canonicalization"] = payload_hash.payload_canonicalization

        entry.setdefault("finalization", {})
        entry["finalization"]["receipt_is_intake_only"] = True
        entry["finalization"]["hash_chain_inclusion_is_finalization_event"] = True
        entry["finalization"]["native_record_schema_compatible"] = True

    for i in range(first_changed, len(entries)):
        entries[i]["previous_entry_hash"] = None if i == 0 else entries[i - 1]["entry_hash"]
        entries[i]["entry_hash"] = hashing.compute_entry_hash(entries[i])

    errors = hashing.verify_entries(
        entries,
        chain_id=GLOBAL_CHAIN_ID,
        verify_payload_files=True,
        base_dir=ROOT,
    )
    if errors:
        print("Hash-chain repair verification failed:")
        for e in errors:
            print("-", e)
        raise SystemExit(1)

    hashing.write_ledger_atomic(MAIN_LEDGER, entries)
    head = hashing.build_chain_head(
        entries,
        chain_id=GLOBAL_CHAIN_ID,
        generated_at=utc_now(),
    )
    hashing.write_json_atomic(MAIN_HEAD, head)


def run(cmd: list[str]) -> None:
    print("[RUN]", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(cmd)}")


def rebuild_all_indexes() -> None:
    run([
        sys.executable,
        "scripts/build_record_chain_indexes.py",
        "--ledger", "record-chain/hash-chain/main.chain.jsonl",
        "--out-dir", "api",
        "--chain-id", GLOBAL_CHAIN_ID,
        "--verify-payload-files",
        "--base-dir", ".",
    ])
    native.build_indexes()


def verify_all() -> None:
    run([
        sys.executable,
        "scripts/verify_record_chain_integrity.py",
        "--ledger", "record-chain/hash-chain/main.chain.jsonl",
        "--head", "api/record-chain-head.json",
        "--chain-id", GLOBAL_CHAIN_ID,
        "--verify-payload-files",
        "--base-dir", ".",
    ])
    run([sys.executable, "scripts/trinity_record_chain.py", "verify"])
