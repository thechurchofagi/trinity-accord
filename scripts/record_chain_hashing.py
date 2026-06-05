#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CHAIN_ENTRY_SCHEMA = "trinity_record_chain_link.v1"
CHAIN_HEAD_SCHEMA = "trinity_record_chain_head.v1"
CHAIN_HEAD_COMMITMENT_SCHEMA = "trinity_record_chain_head_commitment.v1"
CHAIN_TYPE_INDEX_SCHEMA = "trinity_record_chain_type_index.v1"
CHAIN_ALL_INDEX_SCHEMA = "trinity_record_chain_all_index.v1"
CHAIN_INDEX_MANIFEST_SCHEMA = "trinity_record_chain_index_manifest.v1"
OTS_ANCHOR_SCHEMA = "trinity_record_chain_ots_anchor.v1"
OTS_LATEST_SCHEMA = "trinity_record_chain_ots_latest.v1"

DEFAULT_CHAIN_ID = "trinity-record-chain-main"
HASH_HEX_LEN = 64
SAFE_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


class ChainError(Exception):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_json_sha256(obj: Any) -> str:
    return sha256_bytes(canonical_json_bytes(obj))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json_atomic(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(
        obj,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"
    write_bytes_atomic(path, data.encode("utf-8"))


def write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def write_text_atomic(path: Path, text: str) -> None:
    write_bytes_atomic(path, text.encode("utf-8"))


def is_hash_hex(value: Any) -> bool:
    return isinstance(value, str) and len(value) == HASH_HEX_LEN and all(
        c in "0123456789abcdef" for c in value.lower()
    )


def record_type_slug(record_type: str) -> str:
    slug = SAFE_SLUG_RE.sub("_", record_type.strip())
    slug = slug.strip("._-")
    if not slug:
        raise ValueError(f"record_type cannot be converted to safe slug: {record_type!r}")
    return slug


def without_entry_hash(entry: dict[str, Any]) -> dict[str, Any]:
    cleaned = dict(entry)
    cleaned.pop("entry_hash", None)
    return cleaned


def compute_entry_hash(entry: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(without_entry_hash(entry)))


@dataclass(frozen=True)
class PayloadHash:
    payload_file: str
    payload_bytes: int
    payload_raw_sha256: str
    payload_canonical_sha256: str | None
    payload_canonicalization: str


def compute_payload_hash(record_file: Path) -> PayloadHash:
    raw = record_file.read_bytes()
    raw_sha = sha256_bytes(raw)

    try:
        obj = json.loads(raw.decode("utf-8"))
        canonical = canonical_json_bytes(obj)
        canonical_sha = sha256_bytes(canonical)
        canonicalization = "json.sort_keys.no_whitespace.utf8.allow_nan_false.v1"
    except Exception:
        canonical_sha = None
        canonicalization = "raw-bytes-only.non-json"

    return PayloadHash(
        payload_file=str(record_file),
        payload_bytes=len(raw),
        payload_raw_sha256=raw_sha,
        payload_canonical_sha256=canonical_sha,
        payload_canonicalization=canonicalization,
    )


def load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ChainError(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
            if not isinstance(item, dict):
                raise ChainError(f"{path}:{line_number}: entry is not an object")
            entries.append(item)
    return entries


def serialize_ledger(entries: Iterable[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(
            entry,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ) + "\n"
        for entry in entries
    )


def write_ledger_atomic(path: Path, entries: list[dict[str, Any]]) -> None:
    write_text_atomic(path, serialize_ledger(entries))


def validate_entry_shape(entry: dict[str, Any], index: int, chain_id: str) -> list[str]:
    errors: list[str] = []

    if entry.get("schema") != CHAIN_ENTRY_SCHEMA:
        errors.append(f"entry[{index}]: schema mismatch")

    if entry.get("chain_id") != chain_id:
        errors.append(f"entry[{index}]: chain_id mismatch")

    if entry.get("chain_version") != 1:
        errors.append(f"entry[{index}]: chain_version must be 1")

    if entry.get("height") != index:
        errors.append(f"entry[{index}]: height must be {index}")

    if index == 0:
        if entry.get("previous_entry_hash") is not None:
            errors.append("entry[0]: previous_entry_hash must be null")
    else:
        if not is_hash_hex(entry.get("previous_entry_hash")):
            errors.append(f"entry[{index}]: previous_entry_hash must be 64-char hex")

    if not is_hash_hex(entry.get("entry_hash")):
        errors.append(f"entry[{index}]: entry_hash must be 64-char hex")

    record = entry.get("record")
    if not isinstance(record, dict):
        errors.append(f"entry[{index}]: record must be object")
    else:
        if not record.get("record_type"):
            errors.append(f"entry[{index}]: record.record_type missing")
        if not record.get("record_id"):
            errors.append(f"entry[{index}]: record.record_id missing")
        if not record.get("payload_raw_sha256"):
            errors.append(f"entry[{index}]: record.payload_raw_sha256 missing")
        elif not is_hash_hex(record.get("payload_raw_sha256")):
            errors.append(f"entry[{index}]: record.payload_raw_sha256 invalid")

        canonical_sha = record.get("payload_canonical_sha256")
        if canonical_sha is not None and not is_hash_hex(canonical_sha):
            errors.append(f"entry[{index}]: record.payload_canonical_sha256 invalid")

    finalization = entry.get("finalization")
    if not isinstance(finalization, dict):
        errors.append(f"entry[{index}]: finalization must be object")
    else:
        if finalization.get("receipt_is_intake_only") is not True:
            errors.append(f"entry[{index}]: receipt_is_intake_only must be true")
        if finalization.get("hash_chain_inclusion_is_finalization_event") is not True:
            errors.append(
                f"entry[{index}]: hash_chain_inclusion_is_finalization_event must be true"
            )

    return errors


def verify_entries(
    entries: list[dict[str, Any]],
    *,
    chain_id: str = DEFAULT_CHAIN_ID,
    verify_payload_files: bool = False,
    base_dir: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    seen_hashes: set[str] = set()
    seen_record_ids: set[str] = set()
    previous_hash: str | None = None

    for index, entry in enumerate(entries):
        errors.extend(validate_entry_shape(entry, index, chain_id))

        expected_hash = compute_entry_hash(entry)
        actual_hash = entry.get("entry_hash")
        if actual_hash != expected_hash:
            errors.append(
                f"entry[{index}]: entry_hash mismatch: expected {expected_hash}, got {actual_hash}"
            )

        if isinstance(actual_hash, str):
            if actual_hash in seen_hashes:
                errors.append(f"entry[{index}]: duplicate entry_hash {actual_hash}")
            seen_hashes.add(actual_hash)

        if entry.get("previous_entry_hash") != previous_hash:
            errors.append(
                f"entry[{index}]: previous_entry_hash mismatch: "
                f"expected {previous_hash}, got {entry.get('previous_entry_hash')}"
            )

        record = entry.get("record") if isinstance(entry.get("record"), dict) else {}
        if isinstance(record, dict):
            record_id = record.get("record_id")
            if isinstance(record_id, str):
                if record_id in seen_record_ids:
                    errors.append(f"entry[{index}]: duplicate record_id {record_id}")
                seen_record_ids.add(record_id)

        if verify_payload_files and isinstance(record, dict):
            payload_file = record.get("payload_file")
            if payload_file:
                payload_path = Path(payload_file)
                if base_dir and not payload_path.is_absolute():
                    payload_path = base_dir / payload_path
                if not payload_path.exists():
                    errors.append(f"entry[{index}]: payload file missing: {payload_path}")
                else:
                    payload_hash = compute_payload_hash(payload_path)
                    if payload_hash.payload_raw_sha256 != record.get("payload_raw_sha256"):
                        errors.append(
                            f"entry[{index}]: payload_raw_sha256 mismatch for {payload_path}"
                        )
                    if (
                        record.get("payload_canonical_sha256") is not None
                        and payload_hash.payload_canonical_sha256
                        != record.get("payload_canonical_sha256")
                    ):
                        errors.append(
                            f"entry[{index}]: payload_canonical_sha256 mismatch for {payload_path}"
                        )

        previous_hash = actual_hash if isinstance(actual_hash, str) else None

    return errors


def build_chain_entry(
    *,
    chain_id: str,
    height: int,
    previous_entry_hash: str | None,
    record_file: Path,
    record_type: str,
    record_id: str,
    receipt_id: str | None,
    source_run_id: str | None,
    finalized_at: str,
    finalized_by: str,
    arweave_tx_id: str | None = None,
    arweave_gateway_url: str | None = None,
    arweave_payload_sha256: str | None = None,
    arweave_readback_sha256: str | None = None,
    arweave_hash_match: bool | None = None,
) -> dict[str, Any]:
    payload_hash = compute_payload_hash(record_file)

    entry: dict[str, Any] = {
        "schema": CHAIN_ENTRY_SCHEMA,
        "chain_id": chain_id,
        "chain_version": 1,
        "height": height,
        "previous_entry_hash": previous_entry_hash,
        "record": {
            "record_type": record_type,
            "record_id": record_id,
            "receipt_id": receipt_id,
            "payload_file": str(record_file),
            "payload_bytes": payload_hash.payload_bytes,
            "payload_raw_sha256": payload_hash.payload_raw_sha256,
            "payload_canonical_sha256": payload_hash.payload_canonical_sha256,
            "payload_canonicalization": payload_hash.payload_canonicalization,
        },
        "archive": {
            "arweave_tx_id": arweave_tx_id,
            "arweave_gateway_url": arweave_gateway_url,
            "arweave_payload_sha256": arweave_payload_sha256,
            "arweave_readback_sha256": arweave_readback_sha256,
            "arweave_hash_match": arweave_hash_match,
        },
        "finalization": {
            "source_run_id": source_run_id,
            "finalized_at": finalized_at,
            "finalized_by": finalized_by,
            "receipt_is_intake_only": True,
            "hash_chain_inclusion_is_finalization_event": True,
        },
    }

    entry["entry_hash"] = compute_entry_hash(entry)
    return entry


def build_chain_head(
    entries: list[dict[str, Any]],
    *,
    chain_id: str = DEFAULT_CHAIN_ID,
    generated_at: str,
) -> dict[str, Any]:
    if entries:
        last = entries[-1]
        head_hash = last.get("entry_hash")
        height = last.get("height")
    else:
        head_hash = None
        height = -1

    return {
        "schema": CHAIN_HEAD_SCHEMA,
        "chain_id": chain_id,
        "chain_version": 1,
        "height": height,
        "head_entry_hash": head_hash,
        "entry_count": len(entries),
        "generated_at": generated_at,
        "ledger_file": "record-chain/hash-chain/main.chain.jsonl",
        "canonicalization": "json.sort_keys.no_whitespace.utf8.allow_nan_false.v1",
        "receipt_semantics": "receipt is intake-only; hash-chain inclusion requires finalization",
        "ots_semantics": "OTS anchors a stable head commitment snapshot, not this volatile API file",
        "type_indexes_are_derived": True,
    }


def build_head_commitment(head: dict[str, Any]) -> dict[str, Any]:
    """
    Stable object used as the OTS input.

    Do not anchor the raw api/record-chain-head.json bytes because generated_at
    intentionally changes on rebuilds.
    """
    required = ["schema", "chain_id", "chain_version", "height", "head_entry_hash", "entry_count"]
    missing = [key for key in required if key not in head]
    if missing:
        raise ChainError(f"head missing required fields for commitment: {missing}")

    if head.get("schema") != CHAIN_HEAD_SCHEMA:
        raise ChainError(f"head schema mismatch: {head.get('schema')}")

    if head.get("height", -1) < 0 or not head.get("head_entry_hash"):
        raise ChainError("refusing to build OTS commitment for empty chain head")

    return {
        "schema": CHAIN_HEAD_COMMITMENT_SCHEMA,
        "chain_id": head["chain_id"],
        "chain_version": head["chain_version"],
        "height": head["height"],
        "head_entry_hash": head["head_entry_hash"],
        "entry_count": head["entry_count"],
        "ledger_file": head.get("ledger_file", "record-chain/hash-chain/main.chain.jsonl"),
        "canonicalization": head.get(
            "canonicalization",
            "json.sort_keys.no_whitespace.utf8.allow_nan_false.v1",
        ),
        "receipt_semantics": head.get(
            "receipt_semantics",
            "receipt is intake-only; hash-chain inclusion requires finalization",
        ),
        "type_indexes_are_derived": True,
        "ots_input_semantics": "stable commitment for OTS; excludes generated_at and other volatile fields",
    }


def build_type_index(
    entries: list[dict[str, Any]],
    *,
    chain_id: str,
    record_type: str,
    generated_at: str,
) -> dict[str, Any]:
    items = []
    for entry in entries:
        record = entry.get("record", {})
        if isinstance(record, dict) and record.get("record_type") == record_type:
            items.append(
                {
                    "global_height": entry.get("height"),
                    "entry_hash": entry.get("entry_hash"),
                    "previous_entry_hash": entry.get("previous_entry_hash"),
                    "record_id": record.get("record_id"),
                    "receipt_id": record.get("receipt_id"),
                    "payload_raw_sha256": record.get("payload_raw_sha256"),
                    "payload_canonical_sha256": record.get("payload_canonical_sha256"),
                    "arweave_tx_id": entry.get("archive", {}).get("arweave_tx_id"),
                    "finalized_at": entry.get("finalization", {}).get("finalized_at"),
                }
            )

    slug = record_type_slug(record_type)
    return {
        "schema": CHAIN_TYPE_INDEX_SCHEMA,
        "chain_id": chain_id,
        "chain_version": 1,
        "record_type": record_type,
        "record_type_slug": slug,
        "index_file": f"record-chain-index.{slug}.json",
        "entry_count": len(items),
        "entries": items,
        "generated_at": generated_at,
        "source_ledger": "record-chain/hash-chain/main.chain.jsonl",
        "authority": "derived index; main.chain.jsonl is authoritative",
    }


def build_all_index(
    entries: list[dict[str, Any]],
    *,
    chain_id: str,
    generated_at: str,
) -> dict[str, Any]:
    items = []
    for entry in entries:
        record = entry.get("record", {})
        if isinstance(record, dict):
            items.append(
                {
                    "global_height": entry.get("height"),
                    "entry_hash": entry.get("entry_hash"),
                    "record_type": record.get("record_type"),
                    "record_id": record.get("record_id"),
                    "receipt_id": record.get("receipt_id"),
                    "payload_raw_sha256": record.get("payload_raw_sha256"),
                    "finalized_at": entry.get("finalization", {}).get("finalized_at"),
                }
            )

    return {
        "schema": CHAIN_ALL_INDEX_SCHEMA,
        "chain_id": chain_id,
        "chain_version": 1,
        "entry_count": len(items),
        "entries": items,
        "generated_at": generated_at,
        "source_ledger": "record-chain/hash-chain/main.chain.jsonl",
        "authority": "derived index; main.chain.jsonl is authoritative",
    }
