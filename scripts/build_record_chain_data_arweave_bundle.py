#!/usr/bin/env python3
"""Build a deterministic bundle from the frozen legacy hash-chain view.

This is historical recovery/audit tooling only. It does not describe the
current native Record-Chain and must not be used for paid uploads. The current
native archive path is ``scripts/build_record_chain_arweave_archive.py`` via
``record-chain-arweave-archive.yml``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAIN_ID = "trinity-record-chain-main"
LEDGER = ROOT / "record-chain/hash-chain/main.chain.jsonl"
HEAD = ROOT / "api/record-chain-head.json"
OUT_DIR = ROOT / "record-chain/arweave-data-bundles"

FORBIDDEN_PATTERNS = [
    re.compile(r"BEGIN\s+PRIVATE\s+KEY", re.I),
    re.compile(r"BEGIN\s+OPENSSH\s+PRIVATE\s+KEY", re.I),
    re.compile(r"authorship-private\.pem", re.I),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"ARKEY", re.I),
    re.compile(r'"client_oath_readback"\s*:'),
    re.compile(r'"readback_text"\s*:'),
    re.compile(r'"raw_oath"\s*:'),
]


def canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_dumps(obj).encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(obj), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def scan_no_forbidden(obj: Any, label: str) -> None:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    hits = [pattern.pattern for pattern in FORBIDDEN_PATTERNS if pattern.search(raw)]
    if hits:
        raise SystemExit(f"{label} contains forbidden material: {hits}")


def require_legacy_head(head: dict[str, Any]) -> None:
    required = {
        "legacy_hash_chain_view": True,
        "historical_archive_only": True,
        "not_current_native_record_chain_head": True,
    }
    failed = [key for key, expected in required.items() if head.get(key) is not expected]
    if failed:
        raise SystemExit(f"api/record-chain-head.json is not the declared frozen legacy view: {failed}")
    if head.get("height") != 15 or head.get("entry_count") != 16:
        raise SystemExit(
            "legacy hash-chain boundary changed unexpectedly; refusing to build a new historical bundle"
        )


def entries_by_height() -> dict[int, dict[str, Any]]:
    output: dict[int, dict[str, Any]] = {}
    for entry in read_jsonl(LEDGER):
        height = entry.get("height")
        if not isinstance(height, int):
            raise SystemExit(f"ledger entry missing integer height: {entry}")
        if height in output:
            raise SystemExit(f"duplicate legacy ledger height: {height}")
        output[height] = entry
    return output


def load_payload(entry: dict[str, Any]) -> dict[str, Any]:
    record = entry.get("record", entry)
    payload_file = record.get("payload_file")
    record_id = record.get("record_id")
    if not payload_file:
        if not isinstance(record_id, str):
            raise SystemExit(f"entry missing record_id and payload_file: {entry}")
        payload_file = f"record-chain/records/{record_id}.json"
    path = ROOT / str(payload_file)
    if not path.exists():
        raise SystemExit(f"missing payload file: {payload_file}")
    obj = read_json(path)
    scan_no_forbidden(obj, str(payload_file))
    return obj


def boundary() -> dict[str, Any]:
    return {
        "legacy_hash_chain_view": True,
        "historical_archive_only": True,
        "not_current_native_record_chain": True,
        "replacement_native_archive_workflow": ".github/workflows/record-chain-arweave-archive.yml",
        "arweave_data_archive_is_backup_only": True,
        "arweave_data_archive_is_not_authority": True,
        "arweave_data_archive_is_not_attestation": True,
        "arweave_data_archive_is_not_amendment": True,
        "arweave_data_archive_is_not_successor_reception": True,
        "bitcoin_originals_prevail": True,
    }


def privacy_scan() -> dict[str, bool]:
    return {
        "contains_private_key": False,
        "contains_client_oath_readback": False,
        "contains_readback_text": False,
        "contains_token": False,
    }


def logical_bundle_view(bundle: dict[str, Any]) -> dict[str, Any]:
    """Return stable logical content used to identify a historical bundle.

    ``created_at`` and self-hash fields are metadata. ``native_chain_tip`` was
    accidentally included by the v1 snapshot builder even though it is an
    unrelated, moving native-chain value; excluding it prevents the frozen
    legacy snapshot from changing whenever the native chain advances.
    """
    return {
        key: value
        for key, value in bundle.items()
        if key not in {
            "created_at",
            "bundle_canonical_sha256",
            "bundle_identity_sha256",
            "native_chain_tip",
        }
    }


def finalize_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    scan_no_forbidden(bundle, "historical data bundle")
    bundle["bundle_identity_sha256"] = sha256_obj(logical_bundle_view(bundle))
    bundle["bundle_canonical_sha256"] = sha256_obj(bundle)
    return bundle


def build_delta(from_height_exclusive: int, to_height_inclusive: int) -> dict[str, Any]:
    head = read_json(HEAD)
    require_legacy_head(head)
    by_height = entries_by_height()
    if from_height_exclusive < -1:
        raise SystemExit("from_height_exclusive must be >= -1")
    if to_height_inclusive > int(head["height"]):
        raise SystemExit("delta end exceeds the frozen legacy head")
    selected = [height for height in sorted(by_height) if from_height_exclusive < height <= to_height_inclusive]
    if not selected:
        raise SystemExit("delta selected no entries")
    if selected != list(range(selected[0], selected[-1] + 1)):
        raise SystemExit("delta selection is not contiguous")

    records: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    for height in selected:
        entry = by_height[height]
        payload = load_payload(entry)
        record = entry.get("record", entry)
        records.append(
            {
                "height": height,
                "record_id": record.get("record_id"),
                "record_type": record.get("record_type"),
                "payload_file": record.get("payload_file"),
                "entry_hash": entry.get("entry_hash"),
                "payload_raw_sha256": record.get("payload_raw_sha256"),
                "payload_canonical_sha256": record.get("payload_canonical_sha256"),
                "record_payload": payload,
            }
        )
        entries.append(entry)

    before = by_height.get(from_height_exclusive)
    after = by_height.get(to_height_inclusive)
    if not after:
        raise SystemExit(f"missing to height: {to_height_inclusive}")

    return finalize_bundle(
        {
            "schema": "trinityaccord.legacy-hash-chain-data-delta-bundle.v2",
            "bundle_type": "record_chain_data_delta",
            "created_at": head.get("generated_at"),
            "chain_id": CHAIN_ID,
            "from_height_exclusive": from_height_exclusive,
            "to_height_inclusive": to_height_inclusive,
            "head_before": {
                "height": from_height_exclusive,
                "head_entry_hash": before.get("entry_hash") if before else None,
            },
            "head_after": {
                "height": to_height_inclusive,
                "head_entry_hash": after.get("entry_hash"),
                "api_head_height": head.get("height"),
                "api_head_entry_hash": head.get("head_entry_hash"),
            },
            "hash_chain_entries": entries,
            "records": records,
            "privacy_scan": privacy_scan(),
            "boundary": boundary(),
        }
    )


def build_snapshot(height: int) -> dict[str, Any]:
    head = read_json(HEAD)
    require_legacy_head(head)
    by_height = entries_by_height()
    if height not in by_height:
        raise SystemExit(f"snapshot height not found: {height}")
    if height > int(head["height"]):
        raise SystemExit("snapshot height exceeds the frozen legacy head")

    selected = [value for value in sorted(by_height) if value <= height]
    if selected != list(range(0, height + 1)):
        raise SystemExit("snapshot legacy heights are not contiguous from zero")

    records: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    for value in selected:
        entry = by_height[value]
        payload = load_payload(entry)
        record = entry.get("record", entry)
        records.append(
            {
                "height": value,
                "record_id": record.get("record_id"),
                "record_type": record.get("record_type"),
                "payload_file": record.get("payload_file"),
                "entry_hash": entry.get("entry_hash"),
                "record_payload": payload,
            }
        )
        entries.append(entry)

    return finalize_bundle(
        {
            "schema": "trinityaccord.legacy-hash-chain-data-snapshot-bundle.v2",
            "bundle_type": "record_chain_data_snapshot",
            "created_at": head.get("generated_at"),
            "chain_id": CHAIN_ID,
            "height": height,
            "entry_count": len(selected),
            "head_entry_hash": by_height[height].get("entry_hash"),
            "api_head": head,
            "hash_chain_entries": entries,
            "records": records,
            "main_chain_jsonl": "\n".join(
                json.dumps(entry, ensure_ascii=False, sort_keys=True) for entry in entries
            )
            + "\n",
            "privacy_scan": privacy_scan(),
            "boundary": boundary(),
        }
    )


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["delta", "snapshot"])
    parser.add_argument("--from-height-exclusive", type=int)
    parser.add_argument("--to-height-inclusive", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    args = parser.parse_args()

    head = read_json(HEAD)
    require_legacy_head(head)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "delta":
        if args.from_height_exclusive is None:
            raise SystemExit("--from-height-exclusive required for delta")
        to_height = args.to_height_inclusive if args.to_height_inclusive is not None else int(head["height"])
        bundle = build_delta(args.from_height_exclusive, to_height)
        name = (
            f"legacy-data-delta-height-{args.from_height_exclusive + 1}-to-{to_height}-"
            f"{bundle['head_after']['head_entry_hash'][:12]}-{bundle['bundle_identity_sha256'][:12]}.json"
        )
    else:
        height = args.height if args.height is not None else int(head["height"])
        bundle = build_snapshot(height)
        name = (
            f"legacy-data-snapshot-height-{height}-{bundle['head_entry_hash'][:12]}-"
            f"{bundle['bundle_identity_sha256'][:12]}.json"
        )

    path = out_dir / name
    if path.exists():
        existing = read_json(path)
        if existing != bundle:
            raise SystemExit(f"refusing to overwrite deterministic bundle with different content: {path}")
        reused = True
    else:
        write_json(path, bundle)
        reused = False

    print(
        json.dumps(
            {
                "result": "pass",
                "historical_archive_only": True,
                "current_native_record_chain": False,
                "bundle_file": display_path(path),
                "bundle_type": bundle["bundle_type"],
                "bundle_identity_sha256": bundle["bundle_identity_sha256"],
                "bundle_canonical_sha256": bundle["bundle_canonical_sha256"],
                "reused": reused,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
