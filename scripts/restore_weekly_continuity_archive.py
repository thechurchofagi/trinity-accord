#!/usr/bin/env python3
"""Cold-start restore for Weekly Continuity Zenodo or Arweave archives.

The command never writes into the repository.  It requires a new/empty output
directory, verifies every package and embedded record, reconstructs the native
Record-Chain in order, and emits a recovery report.  A valid series must begin
with the first weekly ``full_snapshot`` and may then contain ordered deltas.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

import trinity_record_chain as chain
from weekly_continuity_package import PUBLISHED_FILE_NAMES, verify_local_package


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARWEAVE_GATEWAY = "https://arweave.net"
DEFAULT_ZENODO_API = "https://zenodo.org/api"
TXID_RE = re.compile(r"^[A-Za-z0-9_-]{43}$")
RECORD_ID_RE = re.compile(r"^R-([0-9]{9})$")


def strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid strict JSON in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object in {label}")
    return value


def fetch_bytes(url: str, label: str, attempts: int = 3) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json,application/octet-stream,*/*",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "User-Agent": "trinity-weekly-continuity-recovery/1.0",
        },
    )
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except (urllib.error.URLError, OSError) as exc:
            last_error = str(exc)
            if attempt < attempts:
                time.sleep(float(attempt))
    raise SystemExit(f"failed to download {label}: {last_error}")


def archive_txid(manifest: dict[str, Any]) -> str | None:
    arweave = manifest.get("arweave")
    if not isinstance(arweave, dict):
        return None
    value = arweave.get("txid") or arweave.get("tx_id")
    return str(value) if isinstance(value, str) and TXID_RE.fullmatch(value) else None


def source_from_deposit(deposit_dir: Path) -> dict[str, Any]:
    verified = verify_local_package(deposit_dir)
    raw = (deposit_dir / "weekly-continuity-bundle.json").read_bytes()
    manifest = strict_json_bytes(
        (deposit_dir / "archive-manifest.json").read_bytes(),
        str(deposit_dir / "archive-manifest.json"),
    )
    return {
        "label": str(deposit_dir),
        "payload": strict_json_bytes(raw, str(deposit_dir)),
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "package_identity_sha256": verified["package_identity_sha256"],
        "txid": archive_txid(manifest),
        "source_type": "verified_weekly_package",
    }


def source_from_arweave(txid: str, gateway: str) -> dict[str, Any]:
    if TXID_RE.fullmatch(txid) is None:
        raise SystemExit(f"invalid Arweave transaction id: {txid}")
    raw = fetch_bytes(f"{gateway.rstrip('/')}/{txid}", f"Arweave {txid}")
    return {
        "label": f"arweave:{txid}",
        "payload": strict_json_bytes(raw, f"Arweave {txid}"),
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "package_identity_sha256": None,
        "txid": txid,
        "source_type": "arweave_readback",
    }


def source_from_payload(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "label": str(path),
        "payload": strict_json_bytes(raw, str(path)),
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "package_identity_sha256": None,
        "txid": None,
        "source_type": "local_payload_without_transport_identity",
    }


def zenodo_file_download_url(item: dict[str, Any]) -> str:
    links = item.get("links")
    if not isinstance(links, dict):
        return ""
    # Public record APIs expose ``content``/``download`` as the byte endpoint.
    # Legacy bucket-file objects use ``self`` as the byte endpoint, so retain it
    # only as a compatibility fallback.
    return str(links.get("content") or links.get("download") or links.get("self") or "")


def source_from_zenodo_record(record_id: str, api_base: str) -> dict[str, Any]:
    if not record_id.isdigit():
        raise SystemExit(f"Zenodo record id must be numeric: {record_id}")
    record_raw = fetch_bytes(
        f"{api_base.rstrip('/')}/records/{record_id}",
        f"Zenodo record {record_id}",
    )
    record = strict_json_bytes(record_raw, f"Zenodo record {record_id}")
    files = record.get("files")
    if not isinstance(files, list):
        raise SystemExit(f"Zenodo record {record_id} has no files list")
    by_name = {
        str(item.get("key") or item.get("filename") or ""): item
        for item in files
        if isinstance(item, dict)
    }
    if set(by_name) != set(PUBLISHED_FILE_NAMES):
        raise SystemExit(f"Zenodo record {record_id} does not contain the exact six-file package")
    with tempfile.TemporaryDirectory(prefix="trinity-zenodo-recovery-") as temp:
        directory = Path(temp)
        for name in PUBLISHED_FILE_NAMES:
            item = by_name[name]
            download = zenodo_file_download_url(item)
            if not download:
                raise SystemExit(f"Zenodo record {record_id} lacks download link for {name}")
            (directory / name).write_bytes(fetch_bytes(download, f"Zenodo {record_id}/{name}"))
        source = source_from_deposit(directory)
    source["label"] = f"zenodo:{record_id}"
    source["source_type"] = "zenodo_public_readback"
    source["zenodo_record_id"] = int(record_id)
    return source


def record_ordinal(value: Any) -> int:
    if not isinstance(value, str):
        raise SystemExit(f"invalid Record-Chain record id: {value!r}")
    match = RECORD_ID_RE.fullmatch(value)
    if match is None:
        raise SystemExit(f"invalid Record-Chain record id: {value}")
    return int(match.group(1))


def safe_relative_path(value: Any, *, expected: str | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise SystemExit("embedded artifact path is missing")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise SystemExit(f"unsafe embedded artifact path: {value}")
    normalized = str(path)
    if expected is not None and normalized != expected:
        raise SystemExit(f"embedded record path mismatch: expected {expected}, got {normalized}")
    return normalized


def decode_embedded(item: dict[str, Any], label: str) -> bytes:
    encoded = item.get("content_base64")
    if not isinstance(encoded, str):
        raise SystemExit(f"missing content_base64 for {label}")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise SystemExit(f"invalid Base64 for {label}") from exc
    if item.get("bytes") != len(raw):
        raise SystemExit(f"embedded byte length mismatch for {label}")
    if item.get("sha256") and item.get("sha256") != hashlib.sha256(raw).hexdigest():
        raise SystemExit(f"embedded SHA-256 mismatch for {label}")
    return raw


def validate_payload(source: dict[str, Any]) -> dict[str, Any]:
    payload = source["payload"]
    if payload.get("schema") != "trinityaccord.record-chain-arweave-delta.v1":
        raise SystemExit(f"{source['label']}: unsupported weekly payload schema")
    if payload.get("chain_id") != chain.CHAIN_ID:
        raise SystemExit(f"{source['label']}: native chain_id mismatch")
    if payload.get("archive_cadence") != "weekly":
        raise SystemExit(f"{source['label']}: payload is not a weekly archive")
    if payload.get("archive_mode") not in {"full_snapshot", "incremental_delta"}:
        raise SystemExit(f"{source['label']}: invalid archive_mode")
    if not isinstance(payload.get("archive_id"), str) or not payload["archive_id"]:
        raise SystemExit(f"{source['label']}: archive_id is missing")
    continuity = payload.get("continuity_bundle")
    if (
        not isinstance(continuity, dict)
        or continuity.get("schema") != "trinityaccord.weekly-continuity-bundle.v1"
    ):
        raise SystemExit(f"{source['label']}: weekly continuity bundle is missing")
    coverage = payload.get("coverage")
    if not isinstance(coverage, dict):
        raise SystemExit(f"{source['label']}: coverage is missing")
    for key in (
        "previous_native_record_count",
        "delta_record_count",
        "current_native_record_count",
    ):
        if not isinstance(coverage.get(key), int) or coverage[key] < 0:
            raise SystemExit(f"{source['label']}: invalid coverage.{key}")
    records = payload.get("included_records")
    if not isinstance(records, list) or len(records) != coverage["delta_record_count"]:
        raise SystemExit(f"{source['label']}: included record count mismatch")
    return coverage


def prepare_output(output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"output directory must be new or empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)


def recover(sources: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    if not sources:
        raise SystemExit("at least one weekly continuity source is required")
    prepared = [(validate_payload(source), source) for source in sources]
    prepared.sort(key=lambda item: item[0]["current_native_record_count"])
    current_count = 0
    previous_sha: str | None = None
    previous_id: str | None = None
    previous_txid: str | None = None
    previous_archive_id: str | None = None
    tx_links_checked = 0
    restored_sources: list[dict[str, Any]] = []
    prepare_output(output_dir)
    records_dir = output_dir / "record-chain" / "records"
    records_dir.mkdir(parents=True)

    for position, (coverage, source) in enumerate(prepared):
        payload = source["payload"]
        mode = payload["archive_mode"]
        if position == 0 and (mode != "full_snapshot" or coverage["previous_native_record_count"] != 0):
            raise SystemExit("weekly recovery series must begin with the full_snapshot baseline")
        if position > 0 and mode != "incremental_delta":
            raise SystemExit("only the first weekly archive may be a full_snapshot")
        if coverage["previous_native_record_count"] != current_count:
            raise SystemExit(
                f"weekly recovery gap: expected previous count {current_count}, "
                f"got {coverage['previous_native_record_count']}"
            )

        previous = payload.get("previous_archive")
        if position > 0:
            if not isinstance(previous, dict):
                raise SystemExit("incremental weekly archive is missing previous_archive")
            if (
                previous.get("archive_id") != previous_archive_id
                or previous.get("native_record_count") != current_count
                or previous.get("latest_record_id") != previous_id
                or previous.get("latest_record_sha256") != previous_sha
            ):
                raise SystemExit("incremental weekly archive previous-archive identity mismatch")
            expected_txid = previous.get("arweave_txid")
            if previous_txid is not None:
                if expected_txid != previous_txid:
                    raise SystemExit("incremental weekly archive Arweave transaction link mismatch")
                tx_links_checked += 1

        for item in payload["included_records"]:
            if not isinstance(item, dict):
                raise SystemExit("embedded record reference is not an object")
            expected_index = current_count + 1
            record_id = str(item.get("record_id") or "")
            if record_ordinal(record_id) != expected_index:
                raise SystemExit(
                    f"weekly recovery record sequence gap: expected R-{expected_index:09d}, got {record_id}"
                )
            safe_relative_path(
                item.get("path"), expected=f"record-chain/records/{record_id}.json"
            )
            encoded = dict(item)
            encoded["sha256"] = item.get("raw_file_sha256")
            raw = decode_embedded(encoded, record_id)
            record = strict_json_bytes(raw, record_id)
            if record.get("record_id") != record_id or record.get("record_index") != expected_index:
                raise SystemExit(f"embedded record identity mismatch: {record_id}")
            if record.get("previous_record_sha256") != previous_sha:
                raise SystemExit(f"embedded native chain link mismatch: {record_id}")
            if item.get("record_sha256") != record.get("record_sha256"):
                raise SystemExit(f"embedded record reference hash mismatch: {record_id}")
            if record.get("content_sha256") != chain.content_hash(record):
                raise SystemExit(f"embedded content_sha256 mismatch: {record_id}")
            if record.get("record_sha256") != chain.record_hash(record):
                raise SystemExit(f"embedded record_sha256 mismatch: {record_id}")
            target = records_dir / f"{record_id}.json"
            target.write_bytes(raw)
            previous_id = record_id
            previous_sha = str(record["record_sha256"])
            current_count = expected_index

        if current_count != coverage["current_native_record_count"]:
            raise SystemExit(f"{source['label']}: current native record count mismatch")
        if (
            coverage.get("current_latest_record_id") != previous_id
            or coverage.get("current_latest_record_sha256") != previous_sha
        ):
            raise SystemExit(f"{source['label']}: current chain-tip identity mismatch")

        continuity = payload["continuity_bundle"]
        ots = continuity.get("latest_native_ots")
        if not isinstance(ots, dict) or ots.get("covers_current_chain_head") is not True:
            raise SystemExit(f"{source['label']}: mature Native OTS coverage is missing")
        ots_metadata = ots.get("metadata")
        if (
            not isinstance(ots_metadata, dict)
            or ots_metadata.get("native_record_count") != current_count
            or ots_metadata.get("latest_record_id") != previous_id
            or ots_metadata.get("latest_record_sha256") != previous_sha
        ):
            raise SystemExit(f"{source['label']}: Native OTS chain-tip identity mismatch")
        artifacts = ots.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) != 3:
            raise SystemExit(f"{source['label']}: Native OTS artifact set is incomplete")
        evidence_dir = output_dir / "continuity-evidence" / str(payload.get("archive_id"))
        evidence_dir.mkdir(parents=True, exist_ok=True)
        artifact_names: set[str] = set()
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                raise SystemExit("Native OTS artifact reference is invalid")
            source_path = safe_relative_path(artifact.get("path"))
            artifact_name = PurePosixPath(source_path).name
            if artifact_name in artifact_names:
                raise SystemExit(f"duplicate Native OTS artifact filename: {artifact_name}")
            artifact_names.add(artifact_name)
            (evidence_dir / artifact_name).write_bytes(
                decode_embedded(artifact, source_path)
            )

        previous_txid = source.get("txid")
        previous_archive_id = str(payload.get("archive_id") or "")
        restored_sources.append(
            {
                "label": source["label"],
                "source_type": source["source_type"],
                "archive_id": payload.get("archive_id"),
                "archive_mode": mode,
                "payload_sha256": source["payload_sha256"],
                "package_identity_sha256": source.get("package_identity_sha256"),
                "arweave_txid": source.get("txid"),
                "current_native_record_count": current_count,
            }
        )

    report = {
        "schema": "trinityaccord.weekly-continuity-recovery-report.v1",
        "result": "pass",
        "recovery_status": "full_recovery",
        "native_record_count": current_count,
        "latest_record_id": previous_id,
        "latest_record_sha256": previous_sha,
        "archive_count": len(restored_sources),
        "arweave_transaction_links_verified": tx_links_checked,
        "sources": restored_sources,
        "boundary": {
            "recovery_does_not_create_authority": True,
            "recovery_does_not_amend_bitcoin_originals": True,
            "bitcoin_originals_prevail": True,
        },
    }
    (output_dir / "recovery-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "record-chain" / "restored-chain-tip.json").write_text(
        json.dumps(
            {
                "schema": "trinityaccord.restored-native-chain-tip.v1",
                "chain_id": chain.CHAIN_ID,
                "native_record_count": current_count,
                "latest_record_id": previous_id,
                "latest_record_sha256": previous_sha,
                "derived_from_verified_weekly_continuity_archives": True,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deposit-dir", action="append", default=[])
    parser.add_argument("--payload-file", action="append", default=[])
    parser.add_argument("--arweave-txid", action="append", default=[])
    parser.add_argument("--zenodo-record-id", action="append", default=[])
    parser.add_argument("--arweave-gateway", default=DEFAULT_ARWEAVE_GATEWAY)
    parser.add_argument("--zenodo-api", default=DEFAULT_ZENODO_API)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-latest-record-id", default="")
    args = parser.parse_args()

    sources: list[dict[str, Any]] = []
    sources.extend(source_from_deposit(Path(value).resolve()) for value in args.deposit_dir)
    sources.extend(source_from_payload(Path(value).resolve()) for value in args.payload_file)
    sources.extend(
        source_from_arweave(txid, args.arweave_gateway) for txid in args.arweave_txid
    )
    sources.extend(
        source_from_zenodo_record(record_id, args.zenodo_api)
        for record_id in args.zenodo_record_id
    )
    report = recover(sources, Path(args.output_dir).resolve())
    if (
        args.expected_latest_record_id
        and report["latest_record_id"] != args.expected_latest_record_id
    ):
        raise SystemExit(
            "restored chain tip mismatch: "
            f"expected {args.expected_latest_record_id}, got {report['latest_record_id']}"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
