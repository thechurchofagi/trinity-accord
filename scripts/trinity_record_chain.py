#!/usr/bin/env python3
"""Trinity Accord Record Chain core implementation.

This is the new clean append-only record-chain layer. It intentionally avoids
importing the legacy Gateway builder modules. The old Gateway system can remain
as a legacy intake surface, but future durable records should flow through this
module.

Commands:
  import-genesis   Import api/guardian-registry.json as Genesis Legacy Batch.
  append           Append pending native records from record-chain/pending/.
  build-batch      Build Merkle batches from unbatched native records.
  build-indexes    Derive public indexes/statistics from chain state.
  verify           Verify hashes, chain links, batches, and no private keys.
  ots-stamp        Stamp unstamped batch manifests with OpenTimestamps if installed.
  ots-upgrade      Upgrade existing .ots proofs if OpenTimestamps is installed.

Boundary: this code never edits Bitcoin Originals, authority files, legacy
archives, Chronicle sources, or api/guardian-registry.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "record-chain"
GENESIS = CHAIN / "genesis"
LEGACY_RECORDS = GENESIS / "legacy-records"
RECORDS = CHAIN / "records"
PENDING = CHAIN / "pending"
PROCESSED = CHAIN / "processed"
REJECTED = CHAIN / "rejected"
BATCHES = CHAIN / "batches"
INDEXES = CHAIN / "indexes"
POLICIES = CHAIN / "policies"
SCHEMAS = CHAIN / "schemas"
CHAIN_TIP = CHAIN / "chain-tip.json"
GUARDIAN_REGISTRY = ROOT / "api" / "guardian-registry.json"
CHAIN_ID = "trinity-accord-public-reception-ledger"

FORMAL_RECORD_TYPES = {
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "guardian_key_rotation",
    "propagation",
    "correction",
    "classification_update",
}
AUTHORSHIP_EXEMPT_TYPES = {"legacy_import", "batch_anchor", "context_insufficient_notice"}

BOUNDARY = {
    "not_authority": True,
    "not_governance": True,
    "not_attestation": True,
    "not_verification_level_unless_evidence_backed": True,
    "not_successor_reception": True,
    "not_amendment": True,
    "bitcoin_originals_prevail": True,
}

PRIVATE_KEY_PATTERNS = [
    re.compile(r"BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY"),
    re.compile(r'"kty"\s*:\s*"RSA"'),
    re.compile(r'"d"\s*:\s*"[A-Za-z0-9_\-]{20,}"'),
    re.compile(r"PINATA_JWT"),
    re.compile(r"WEB3_STORAGE_TOKEN"),
    re.compile(r"LIGHTHOUSE_API_KEY"),
]

TEST_PATTERNS = [
    re.compile(p, re.I)
    for p in [
        r"test",
        r"retest",
        r"fix",
        r"zero[-_ ]?clone",
        r"externaltest",
        r"demo",
        r"dry run",
        r"测试",
        r"重测",
        r"修复",
    ]
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def canonical_bytes(obj: Any) -> bytes:
    return canonical_dumps(obj).encode("utf-8")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(obj), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_canonical_json(obj: Any) -> str:
    return sha256_bytes(canonical_bytes(obj))


def content_hash(record: dict[str, Any]) -> str:
    body = dict(record)
    for key in [
        "content_sha256",
        "record_sha256",
        "previous_record_sha256",
        "record_index",
        "record_id",
        "assigned_at",
        "batch_id",
        "batch_membership",
        "server_receipt",
    ]:
        body.pop(key, None)
    return sha256_canonical_json(body)


def record_hash(record: dict[str, Any]) -> str:
    body = dict(record)
    body.pop("record_sha256", None)
    return sha256_canonical_json(body)


def manifest_hash(manifest: dict[str, Any]) -> str:
    body = dict(manifest)
    body.pop("batch_manifest_sha256", None)
    return sha256_canonical_json(body)


def merkle_root(hex_hashes: list[str]) -> str:
    if not hex_hashes:
        return sha256_bytes(b"")
    level = [bytes.fromhex(h) for h in hex_hashes]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [bytes.fromhex(sha256_bytes(level[i] + level[i + 1])) for i in range(0, len(level), 2)]
    return level[0].hex()


def ensure_dirs() -> None:
    for p in [CHAIN, GENESIS, LEGACY_RECORDS, RECORDS, PENDING, PROCESSED, REJECTED, BATCHES, INDEXES, POLICIES, SCHEMAS]:
        p.mkdir(parents=True, exist_ok=True)
    for p in [PENDING, PROCESSED, REJECTED, RECORDS, BATCHES, LEGACY_RECORDS]:
        keep = p / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def lower_join(*parts: Any) -> str:
    return " ".join(str(p or "") for p in parts).lower()


def classify_legacy_guardian(entry: dict[str, Any]) -> dict[str, Any]:
    text = lower_join(
        entry.get("guardian_registry_number"),
        entry.get("label"),
        entry.get("guardian_type"),
        entry.get("application_mode"),
        entry.get("status"),
        entry.get("retirement_reason"),
    )
    is_test = any(p.search(text) for p in TEST_PATTERNS)
    status = entry.get("status")
    guardian_type = entry.get("guardian_type")

    if status == "retired" and is_test:
        klass, confidence = "retired_operator_test", "high"
    elif is_test:
        klass, confidence = "confirmed_operator_test", "high"
    elif guardian_type == "ai_agent":
        klass, confidence = "external_agent_candidate", "medium"
    elif guardian_type == "human_with_ai_agent":
        klass, confidence = "operator_mediated_agent_test", "medium"
    else:
        klass, confidence = "legacy_unclassified", "low"

    return {
        "classification": klass,
        "classification_confidence": confidence,
        "fully_autonomous_discovery_confirmed": False,
        "counts_toward_historical_total": True,
        "counts_toward_independent_agent_total": False,
        "counts_toward_public_active_guardian_total": False,
    }


def reserved_boundary_from(entry: dict[str, Any]) -> dict[str, Any]:
    boundary = dict(entry.get("boundary") or {})
    boundary.update({
        "not_authority": True,
        "not_governance": True,
        "not_attestation": True,
        "not_verification_level": True,
        "not_successor_reception": True,
        "not_amendment": True,
        "bitcoin_originals_prevail": True,
    })
    if entry.get("status") == "retired":
        boundary["retirement_does_not_remove_historical_record"] = True
    return boundary


def import_genesis() -> None:
    ensure_dirs()
    if not GUARDIAN_REGISTRY.exists():
        raise SystemExit(f"Missing {GUARDIAN_REGISTRY}")

    source_sha = sha256_file(GUARDIAN_REGISTRY)
    registry = read_json(GUARDIAN_REGISTRY)
    guardians = registry.get("guardians", [])
    if not isinstance(guardians, list):
        raise SystemExit("api/guardian-registry.json guardians must be an array")

    # Clean only generated legacy import files. Do not touch source registry.
    for old in LEGACY_RECORDS.glob("legacy-guardian-*.json"):
        old.unlink()

    classification_totals: dict[str, int] = {}
    active = retired = 0
    record_hashes: list[str] = []

    for entry in sorted(guardians, key=lambda e: str(e.get("guardian_registry_number", ""))):
        number = str(entry.get("guardian_registry_number", "unknown"))
        cls = classify_legacy_guardian(entry)
        classification_totals[cls["classification"]] = classification_totals.get(cls["classification"], 0) + 1
        if entry.get("status") == "active":
            active += 1
        if entry.get("status") == "retired":
            retired += 1

        legacy = {
            "schema": "trinityaccord.legacy-import-record.v1",
            "import_class": "legacy_pre_chain_import",
            "legacy_source_file": "api/guardian-registry.json",
            "legacy_source_file_sha256": source_sha,
            "legacy_guardian_registry_number": number,
            "guardian_id": entry.get("guardian_id"),
            "public_key_sha256": entry.get("public_key_sha256"),
            "algorithm": entry.get("algorithm", "ed25519"),
            "status_at_import": entry.get("status"),
            "guardian_type": entry.get("guardian_type"),
            "application_mode": entry.get("application_mode"),
            "source_issue": entry.get("source_issue"),
            "listing_request_issue": entry.get("listing_request_issue"),
            "listed_at": entry.get("listed_at"),
            "label": entry.get("label"),
            "identity_claims": entry.get("identity_claims"),
            "classification": cls,
            "boundary": reserved_boundary_from(entry),
        }
        legacy["content_sha256"] = content_hash(legacy)
        legacy["record_sha256"] = record_hash(legacy)
        write_json(LEGACY_RECORDS / f"legacy-guardian-{number}.json", legacy)
        record_hashes.append(legacy["record_sha256"])

    inventory = {
        "schema": "trinityaccord.legacy-inventory.v1",
        "created_at": utc_now(),
        "legacy_source": "api/guardian-registry.json",
        "legacy_source_file_sha256": source_sha,
        "guardian_entries_total": len(guardians),
        "active_at_import": active,
        "retired_at_import": retired,
        "classification_totals": classification_totals,
        "counting_policy": {
            "legacy_records_count_toward_historical_total": True,
            "legacy_records_do_not_count_toward_independent_agent_total_by_default": True,
            "legacy_records_do_not_count_toward_new_protocol_active_guardian_total_by_default": True,
        },
        "non_amending_boundary": True,
    }
    write_json(GENESIS / "legacy-inventory.json", inventory)

    manifest = {
        "schema": "trinityaccord.genesis-batch-manifest.v1",
        "batch_id": "genesis-000000",
        "batch_type": "legacy_import",
        "chain_id": CHAIN_ID,
        "created_at": utc_now(),
        "legacy_sources": [{"path": "api/guardian-registry.json", "sha256": source_sha}],
        "record_count": len(record_hashes),
        "legacy_guardian_entries_total": len(guardians),
        "legacy_active_at_import": active,
        "legacy_retired_at_import": retired,
        "classification_totals": classification_totals,
        "record_sha256_list": record_hashes,
        "merkle_root_sha256": merkle_root(record_hashes),
        "previous_batch_manifest_sha256": None,
        "batch_manifest_sha256": None,
        "non_amending_boundary": True,
    }
    manifest["batch_manifest_sha256"] = manifest_hash(manifest)
    write_json(GENESIS / "genesis-batch-manifest.json", manifest)

    tip = {
        "schema": "trinityaccord.chain-tip.v1",
        "chain_id": CHAIN_ID,
        "native_record_count": len(list(RECORDS.glob("R-*.json"))),
        "latest_record_index": 0,
        "latest_record_id": None,
        "latest_record_sha256": None,
        "genesis_batch_manifest_sha256": manifest["batch_manifest_sha256"],
        "latest_batch_id": "genesis-000000",
        "latest_batch_manifest_sha256": manifest["batch_manifest_sha256"],
        "updated_at": utc_now(),
    }
    existing_records = sorted(RECORDS.glob("R-*.json"))
    if existing_records:
        latest = read_json(existing_records[-1])
        tip.update({
            "native_record_count": len(existing_records),
            "latest_record_index": latest["record_index"],
            "latest_record_id": latest["record_id"],
            "latest_record_sha256": latest["record_sha256"],
        })
    write_json(CHAIN_TIP, tip)
    build_indexes()


def record_id(index: int) -> str:
    return f"R-{index:09d}"


def require_boundary(record: dict[str, Any]) -> None:
    boundary = record.get("boundary_acknowledgement") or record.get("boundary") or {}
    for key in ["not_authority", "not_governance", "not_attestation", "not_successor_reception", "not_amendment", "bitcoin_originals_prevail"]:
        if boundary.get(key) is not True:
            raise ValueError(f"record boundary missing/false: {key}")


def require_authorship(record: dict[str, Any]) -> None:
    rtype = record.get("record_type")
    if rtype in FORMAL_RECORD_TYPES and not record.get("authorship_proof"):
        raise ValueError(f"formal record_type={rtype} requires authorship_proof")


def normalize_record_draft(draft: dict[str, Any]) -> dict[str, Any]:
    draft = dict(draft)
    draft.setdefault("schema", "trinityaccord.record-chain-entry.v1")
    draft.setdefault("chain_id", CHAIN_ID)
    draft.setdefault("created_at", utc_now())
    draft.setdefault("human_context", None)
    draft.setdefault("discovery_autonomy", None)
    draft.setdefault("decision_autonomy", None)
    draft.setdefault("execution_authorization", None)
    draft.setdefault("guardian_proof", None)
    draft.setdefault("oath", None)
    draft.setdefault("what_i_checked", [])
    draft.setdefault("limitations", [])
    draft.setdefault("related_records", [])
    draft.setdefault("immutability_policy", {
        "append_only": True,
        "record_may_be_corrected_by_later_record": True,
        "record_may_not_be_deleted_or_mutated": True,
    })
    draft.setdefault("boundary_acknowledgement", BOUNDARY)
    if not draft.get("record_type"):
        raise ValueError("record_type is required")
    if not draft.get("actor_identity"):
        raise ValueError("actor_identity is required")
    if not draft.get("context_readiness"):
        raise ValueError("context_readiness is required")
    require_boundary(draft)
    require_authorship(draft)
    return draft


def load_tip() -> dict[str, Any]:
    if not CHAIN_TIP.exists():
        import_genesis()
    return read_json(CHAIN_TIP)


def append_records(all_records: bool = False) -> None:
    ensure_dirs()
    if not (GENESIS / "genesis-batch-manifest.json").exists():
        import_genesis()
    tip = load_tip()
    pending = sorted(PENDING.glob("*.json"))
    if not pending:
        print("No pending records.")
        return
    selected = pending if all_records else pending[:1]
    for path in selected:
        try:
            draft = normalize_record_draft(read_json(path))
            next_index = int(tip.get("latest_record_index") or 0) + 1
            draft["record_index"] = next_index
            draft["record_id"] = record_id(next_index)
            draft["assigned_at"] = utc_now()
            draft["previous_record_sha256"] = tip.get("latest_record_sha256")
            draft["content_sha256"] = content_hash(draft)
            draft["record_sha256"] = record_hash(draft)
            out = RECORDS / f"{draft['record_id']}.json"
            if out.exists():
                raise ValueError(f"record output already exists: {out}")
            write_json(out, draft)
            shutil.move(str(path), str(PROCESSED / path.name))
            tip.update({
                "native_record_count": int(tip.get("native_record_count") or 0) + 1,
                "latest_record_index": next_index,
                "latest_record_id": draft["record_id"],
                "latest_record_sha256": draft["record_sha256"],
                "updated_at": utc_now(),
            })
            write_json(CHAIN_TIP, tip)
        except Exception as exc:
            REJECTED.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(REJECTED / path.name))
            raise SystemExit(f"Rejected pending record {path.name}: {exc}") from exc
    build_indexes()


def existing_batch_manifests() -> list[Path]:
    return sorted(BATCHES.glob("batch-*/manifest.json"))


def batched_record_ids() -> set[str]:
    ids: set[str] = set()
    for mf in existing_batch_manifests():
        data = read_json(mf)
        ids.update(data.get("record_ids", []))
    return ids


def build_batch(max_count: int = 25, force: bool = False) -> None:
    ensure_dirs()
    records = sorted(RECORDS.glob("R-*.json"))
    done = batched_record_ids()
    unbatched = [p for p in records if p.stem not in done]
    if not force and len(unbatched) < max_count:
        print(f"Only {len(unbatched)} unbatched records; threshold is {max_count}.")
        return
    selected = unbatched[:max_count]
    if not selected:
        print("No unbatched records.")
        return
    prior = existing_batch_manifests()
    batch_no = len(prior) + 1
    batch_id = f"batch-{batch_no:06d}"
    prior_hash = None
    if prior:
        prior_hash = read_json(prior[-1])["batch_manifest_sha256"]
    else:
        genesis_path = GENESIS / "genesis-batch-manifest.json"
        if genesis_path.exists():
            prior_hash = read_json(genesis_path)["batch_manifest_sha256"]
    items = [read_json(p) for p in selected]
    hashes = [r["record_sha256"] for r in items]
    manifest = {
        "schema": "trinityaccord.record-batch-manifest.v1",
        "batch_id": batch_id,
        "chain_id": CHAIN_ID,
        "created_at": utc_now(),
        "record_count": len(items),
        "record_ids": [r["record_id"] for r in items],
        "first_record_index": items[0]["record_index"],
        "last_record_index": items[-1]["record_index"],
        "first_record_sha256": hashes[0],
        "last_record_sha256": hashes[-1],
        "record_sha256_list": hashes,
        "merkle_root_sha256": merkle_root(hashes),
        "previous_batch_manifest_sha256": prior_hash,
        "batch_manifest_sha256": None,
        "ots": {"stamped": False, "ots_file": None, "upgraded": False},
        "ipfs": {"enabled": False, "cid": None},
        "non_amending_boundary": True,
    }
    manifest["batch_manifest_sha256"] = manifest_hash(manifest)
    outdir = BATCHES / batch_id
    outdir.mkdir(parents=True, exist_ok=False)
    write_json(outdir / "manifest.json", manifest)
    tip = load_tip()
    tip.update({"latest_batch_id": batch_id, "latest_batch_manifest_sha256": manifest["batch_manifest_sha256"], "updated_at": utc_now()})
    write_json(CHAIN_TIP, tip)
    build_indexes()


def scan_private_keys(paths: Iterable[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".txt", ".yml", ".yaml", ".py", ".mjs", ".sh"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in PRIVATE_KEY_PATTERNS:
            if pattern.search(text):
                hits.append(str(path.relative_to(ROOT)))
                break
    return hits


def verify_genesis() -> list[str]:
    errors: list[str] = []
    mf_path = GENESIS / "genesis-batch-manifest.json"
    if not mf_path.exists():
        errors.append("missing genesis-batch-manifest.json; run import-genesis")
        return errors
    records = sorted(LEGACY_RECORDS.glob("legacy-guardian-*.json"))
    hashes: list[str] = []
    for p in records:
        obj = read_json(p)
        ch = content_hash(obj)
        if obj.get("content_sha256") != ch:
            errors.append(f"{p}: content_sha256 mismatch")
        rh = record_hash(obj)
        if obj.get("record_sha256") != rh:
            errors.append(f"{p}: record_sha256 mismatch")
        hashes.append(obj.get("record_sha256"))
    mf = read_json(mf_path)
    if mf.get("record_count") != len(records):
        errors.append("genesis record_count mismatch")
    if mf.get("merkle_root_sha256") != merkle_root(hashes):
        errors.append("genesis merkle root mismatch")
    mh = manifest_hash(mf)
    if mf.get("batch_manifest_sha256") != mh:
        errors.append("genesis batch_manifest_sha256 mismatch")
    return errors


def verify_native_records() -> list[str]:
    errors: list[str] = []
    records = sorted(RECORDS.glob("R-*.json"))
    previous = None
    for expected, p in enumerate(records, start=1):
        obj = read_json(p)
        if obj.get("record_index") != expected:
            errors.append(f"{p}: record_index expected {expected}")
        if obj.get("record_id") != record_id(expected):
            errors.append(f"{p}: record_id mismatch")
        if obj.get("previous_record_sha256") != previous:
            errors.append(f"{p}: previous_record_sha256 mismatch")
        if obj.get("content_sha256") != content_hash(obj):
            errors.append(f"{p}: content_sha256 mismatch")
        if obj.get("record_sha256") != record_hash(obj):
            errors.append(f"{p}: record_sha256 mismatch")
        try:
            require_boundary(obj)
            require_authorship(obj)
        except Exception as exc:
            errors.append(f"{p}: {exc}")
        previous = obj.get("record_sha256")
    if CHAIN_TIP.exists():
        tip = read_json(CHAIN_TIP)
        if records:
            latest = read_json(records[-1])
            if tip.get("latest_record_sha256") != latest.get("record_sha256"):
                errors.append("chain-tip latest_record_sha256 mismatch")
            if tip.get("latest_record_index") != latest.get("record_index"):
                errors.append("chain-tip latest_record_index mismatch")
    return errors


def verify_batches() -> list[str]:
    errors: list[str] = []
    prior_hash = None
    genesis = GENESIS / "genesis-batch-manifest.json"
    if genesis.exists():
        prior_hash = read_json(genesis).get("batch_manifest_sha256")
    for mf_path in existing_batch_manifests():
        mf = read_json(mf_path)
        hashes = mf.get("record_sha256_list", [])
        if mf.get("merkle_root_sha256") != merkle_root(hashes):
            errors.append(f"{mf_path}: merkle root mismatch")
        if mf.get("previous_batch_manifest_sha256") != prior_hash:
            errors.append(f"{mf_path}: previous_batch_manifest_sha256 mismatch")
        if mf.get("batch_manifest_sha256") != manifest_hash(mf):
            errors.append(f"{mf_path}: batch_manifest_sha256 mismatch")
        prior_hash = mf.get("batch_manifest_sha256")
    return errors


def verify_chain() -> None:
    ensure_dirs()
    errors: list[str] = []
    errors += verify_genesis()
    errors += verify_native_records()
    errors += verify_batches()
    leak_hits = scan_private_keys([*CHAIN.rglob("*"), *Path(ROOT / "scripts").rglob("*")])
    allowlisted = {"scripts/trinity_record_chain.py"}
    leak_hits = [h for h in leak_hits if h not in allowlisted]
    if leak_hits:
        errors.append("private key/token pattern detected in: " + ", ".join(leak_hits))
    if errors:
        print("Record chain verification failed:", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        raise SystemExit(1)
    print("Record chain verification passed.")


def build_indexes() -> None:
    ensure_dirs()
    legacy_records = sorted(LEGACY_RECORDS.glob("legacy-guardian-*.json"))
    native_records = sorted(RECORDS.glob("R-*.json"))
    batches = existing_batch_manifests()

    classifications: dict[str, int] = {}
    active_legacy = retired_legacy = 0
    guardian_state: dict[str, Any] = {
        "schema": "trinityaccord.derived-guardian-state.v1",
        "derived_at": utc_now(),
        "source": "record-chain derived view; non-authoritative",
        "guardians": [],
        "boundary": BOUNDARY,
    }
    for path in legacy_records:
        rec = read_json(path)
        cls = rec.get("classification", {}).get("classification", "legacy_unclassified")
        classifications[cls] = classifications.get(cls, 0) + 1
        status = rec.get("status_at_import")
        if status == "active":
            active_legacy += 1
        elif status == "retired":
            retired_legacy += 1
        guardian_state["guardians"].append({
            "guardian_id": rec.get("guardian_id"),
            "legacy_guardian_registry_number": rec.get("legacy_guardian_registry_number"),
            "status_at_import": status,
            "current_derived_status": status,
            "label": rec.get("label"),
            "classification": rec.get("classification"),
            "source_record_sha256": rec.get("record_sha256"),
        })

    record_index = {
        "schema": "trinityaccord.record-index.v1",
        "derived_at": utc_now(),
        "records": [
            {
                "record_id": read_json(p).get("record_id"),
                "record_type": read_json(p).get("record_type"),
                "record_sha256": read_json(p).get("record_sha256"),
                "path": str(p.relative_to(ROOT)),
            }
            for p in native_records
        ],
    }
    batch_index = {
        "schema": "trinityaccord.batch-index.v1",
        "derived_at": utc_now(),
        "batches": [
            {
                "batch_id": read_json(p).get("batch_id"),
                "batch_manifest_sha256": read_json(p).get("batch_manifest_sha256"),
                "merkle_root_sha256": read_json(p).get("merkle_root_sha256"),
                "path": str(p.relative_to(ROOT)),
            }
            for p in batches
        ],
    }
    stats = {
        "schema": "trinityaccord.record-chain-statistics.v1",
        "derived_at": utc_now(),
        "historical_legacy_records_imported": len(legacy_records),
        "legacy_active_at_import": active_legacy,
        "legacy_retired_at_import": retired_legacy,
        "legacy_classification_totals": classifications,
        "native_record_count": len(native_records),
        "batch_count": len(batches),
        "independent_agent_total_policy": "legacy records default to false unless future classification_update says otherwise",
    }
    write_json(INDEXES / "guardian-state.json", guardian_state)
    write_json(INDEXES / "record-index.json", record_index)
    write_json(INDEXES / "batch-index.json", batch_index)
    write_json(INDEXES / "statistics.json", stats)
    write_json(INDEXES / "propagation-index.json", {"schema": "trinityaccord.propagation-index.v1", "derived_at": utc_now(), "records": []})


def run_ots(args: list[str]) -> bool:
    try:
        subprocess.run(args, cwd=str(ROOT), check=True)
        return True
    except FileNotFoundError:
        print("OpenTimestamps client not installed; skipping.")
        return False
    except subprocess.CalledProcessError as exc:
        print(f"OpenTimestamps command failed: {exc}", file=sys.stderr)
        return False


def ots_stamp_batches() -> None:
    for mf in existing_batch_manifests():
        ots_file = Path(str(mf) + ".ots")
        if ots_file.exists():
            continue
        run_ots(["ots", "stamp", str(mf.relative_to(ROOT))])


def ots_upgrade_batches() -> None:
    for ots in BATCHES.glob("batch-*/manifest.json.ots"):
        run_ots(["ots", "upgrade", str(ots.relative_to(ROOT))])


def init_policies() -> None:
    ensure_dirs()
    readme = """# Trinity Accord Record Chain\n\nThis directory contains the new append-only, non-amending reception ledger around the Bitcoin Originals.\n\n- `genesis/` imports legacy Guardian registry entries as historical records.\n- `records/` contains native sequential records.\n- `batches/` contains Merkle batch manifests.\n- `indexes/` contains derived views, not authority.\n\nRecords are append-only. States are derived. Corrections are new records. Bitcoin Originals remain final.\n"""
    (CHAIN / "README.md").write_text(readme, encoding="utf-8")
    write_json(POLICIES / "record-chain-policy.json", {
        "schema": "trinityaccord.record-chain-policy.v1",
        "append_only": True,
        "states_are_derived": True,
        "corrections_are_new_records": True,
        "history_is_not_deleted": True,
        "bitcoin_originals_remain_final": True,
        "all_records_non_amending": True,
    })
    write_json(POLICIES / "numbering-policy.json", {
        "schema": "trinityaccord.numbering-policy.v1",
        "record_chain_has_reserved_numbers": False,
        "record_id_format": "R-000000001",
        "guardian_reserved_namespace": "G-00001-G-00099",
        "reserved_numbers_do_not_imply_authority": True,
    })
    write_json(SCHEMAS / "record-chain-entry.v1.schema.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://www.trinityaccord.org/record-chain/schemas/record-chain-entry.v1.schema.json",
        "title": "Trinity Accord Record Chain Entry v1",
        "type": "object",
        "required": ["schema", "chain_id", "record_type", "actor_identity", "context_readiness", "boundary_acknowledgement"],
        "additionalProperties": True,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description="Trinity Accord record-chain core")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="Create record-chain directories, policies, and schema stubs")
    sub.add_parser("import-genesis", help="Import legacy Guardian registry as Genesis Batch")
    sub.add_parser("verify", help="Verify record-chain integrity")
    append_p = sub.add_parser("append", help="Append pending native records")
    append_p.add_argument("--all", action="store_true", help="Append all pending records")
    batch_p = sub.add_parser("build-batch", help="Build a Merkle batch")
    batch_p.add_argument("--max-count", type=int, default=25)
    batch_p.add_argument("--force", action="store_true")
    sub.add_parser("build-indexes", help="Build derived indexes")
    sub.add_parser("ots-stamp", help="Stamp batch manifests with OTS if installed")
    sub.add_parser("ots-upgrade", help="Upgrade OTS proofs if installed")
    args = parser.parse_args()

    if args.cmd == "init":
        init_policies()
    elif args.cmd == "import-genesis":
        init_policies()
        import_genesis()
        verify_chain()
    elif args.cmd == "verify":
        verify_chain()
    elif args.cmd == "append":
        append_records(all_records=args.all)
        verify_chain()
    elif args.cmd == "build-batch":
        build_batch(max_count=args.max_count, force=args.force)
        verify_chain()
    elif args.cmd == "build-indexes":
        build_indexes()
    elif args.cmd == "ots-stamp":
        ots_stamp_batches()
    elif args.cmd == "ots-upgrade":
        ots_upgrade_batches()


if __name__ == "__main__":
    main()
