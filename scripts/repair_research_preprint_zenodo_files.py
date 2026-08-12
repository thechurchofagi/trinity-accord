#!/usr/bin/env python3
"""Correct the standalone v1.1 PDF on its existing Zenodo record.

The original GitHub archive remains immutable.  During Zenodo's bounded
post-publication correction window, this script may replace only the known
standalone PDF revision with the known corrected revision.  It does not alter
metadata, mint a DOI, create a new version, or modify the archived Canon.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from publish_preservation_capsule_to_zenodo import ZenodoClient


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_DIR = ROOT / "research" / "trinity-accord-design-and-limits"
DEFAULT_PDF = RESEARCH_DIR / "trinity-accord-design-and-limits-v1.1.pdf"
DEFAULT_API = "https://zenodo.org/api"
RECORD_ID = 21699878
DOI = "10.5281/zenodo.21699878"
VERSION = "1.1"
TITLE = (
    "Designing a Verifiable, Non-Amending Civilizational Memory Record "
    "for Future AI Agents: The Trinity Accord Case Study"
)
PDF_NAME = "trinity-accord-design-and-limits-v1.1.pdf"
PDF_SHA256 = "b391776db76f533799dc582f39af54d2e885fe2ed1982cfe3024a1400a403e9c"
PDF_MD5 = "f5d977178f40539018f92e500cc59d9e"
PDF_BYTES = 116911
PRIOR_PDF_SHA256 = "2facb19a2cfbd6d18573b7c1b18b52a7667cf0202e163c5d847ceb7a31cea4f2"
PRIOR_PDF_MD5 = "b7dbc4cf4f81dc6e3de5fa35a36987ac"
PRIOR_PDF_BYTES = 113360
ARCHIVE_NAME = "thechurchofagi/trinity-accord-ta-tr-2026-01-v1.1-zenodo.zip"
ARCHIVE_MD5 = "14b34072deba4379454687d4a6a26d00"
ARCHIVE_BYTES = 25288793
ACKNOWLEDGEMENT = "TRINITY_RESEARCH_PREPRINT_PDF_CORRECTION_V2_APPROVED"
FILE_MODIFICATION_COMMENT = (
    "Correct the v1.1 standalone PDF to formalize interpretive non-exclusivity "
    "and source-version terminology; no Canon text or empirical result changes."
)


def as_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SystemExit(f"Zenodo {label} response is not an object")
    return value


def file_name(item: dict[str, Any]) -> str:
    return str(item.get("filename") or item.get("key") or "")


def file_size(item: dict[str, Any]) -> int | None:
    value = item.get("filesize", item.get("size"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def file_md5(item: dict[str, Any]) -> str:
    return str(item.get("checksum") or "").split(":", 1)[-1].lower()


def file_download(item: dict[str, Any]) -> str:
    links = item.get("links")
    if not isinstance(links, dict):
        return ""
    direct = str(links.get("download") or links.get("content") or "")
    if direct:
        return direct
    self_link = str(links.get("self") or "")
    return self_link if self_link.endswith("/content") else ""


def files_by_name(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = record.get("files")
    if not isinstance(files, list):
        raise SystemExit("Zenodo response has no files list")
    result: dict[str, dict[str, Any]] = {}
    for item in files:
        if not isinstance(item, dict):
            continue
        name = file_name(item)
        if not name:
            continue
        if name in result:
            raise SystemExit(f"Zenodo response contains duplicate file name: {name}")
        result[name] = item
    return result


def validate_identity(record: dict[str, Any]) -> None:
    metadata = record.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    try:
        record_id = int(record.get("record_id") or record.get("recid") or record.get("id"))
    except (TypeError, ValueError) as exc:
        raise SystemExit("Zenodo record identity is missing") from exc
    if record_id != RECORD_ID:
        raise SystemExit(f"refusing unexpected Zenodo record id: {record_id}")
    observed_doi = str(record.get("doi") or metadata.get("doi") or "")
    if observed_doi != DOI:
        raise SystemExit(f"refusing unexpected Zenodo DOI: {observed_doi!r}")
    if metadata.get("title") != TITLE:
        raise SystemExit("refusing Zenodo record with an unexpected title")
    if str(metadata.get("version") or "") != VERSION:
        raise SystemExit("refusing Zenodo record with an unexpected version")


def validate_local_pdf(pdf_path: Path) -> dict[str, Any]:
    raw = pdf_path.read_bytes()
    if not raw.startswith(b"%PDF-"):
        raise SystemExit("local research preprint is not a PDF")
    identity = {
        "name": PDF_NAME,
        "bytes": len(raw),
        "md5": hashlib.md5(raw).hexdigest(),  # nosec B324 - Zenodo file identity
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    expected = {
        "name": PDF_NAME,
        "bytes": PDF_BYTES,
        "md5": PDF_MD5,
        "sha256": PDF_SHA256,
    }
    if identity != expected:
        raise SystemExit(f"local research preprint identity drifted: {identity}")
    return identity


def validate_file_entry(
    item: dict[str, Any], *, name: str, size: int, md5: str
) -> None:
    if file_name(item) != name:
        raise SystemExit(f"Zenodo file name mismatch for {name}")
    if file_size(item) != size:
        raise SystemExit(f"Zenodo file size mismatch for {name}")
    if file_md5(item) != md5:
        raise SystemExit(f"Zenodo file checksum mismatch for {name}")


def classify_pdf_entry(item: dict[str, Any]) -> str:
    """Accept only the exact prior or corrected standalone PDF identity."""
    if file_name(item) != PDF_NAME:
        raise SystemExit("Zenodo standalone PDF name mismatch")
    observed = (file_size(item), file_md5(item))
    if observed == (PDF_BYTES, PDF_MD5):
        return "corrected"
    if observed == (PRIOR_PDF_BYTES, PRIOR_PDF_MD5):
        return "prior"
    raise SystemExit(f"unexpected Zenodo standalone PDF identity: {observed}")


def validate_archive_preserved(record: dict[str, Any]) -> None:
    remote = files_by_name(record)
    archive = remote.get(ARCHIVE_NAME)
    if archive is None:
        raise SystemExit("original Zenodo GitHub archive is missing; refusing repair")
    validate_file_entry(
        archive,
        name=ARCHIVE_NAME,
        size=ARCHIVE_BYTES,
        md5=ARCHIVE_MD5,
    )


def validate_repair_window(record: dict[str, Any], now: datetime) -> None:
    created = str(record.get("created") or "")
    if not created:
        raise SystemExit("Zenodo deposition creation time is missing")
    try:
        published_at = datetime.fromisoformat(created.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SystemExit("Zenodo deposition creation time is invalid") from exc
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    if now.astimezone(timezone.utc) > published_at + timedelta(days=30):
        raise SystemExit("Zenodo 30-day minor file-correction window has elapsed")


def verify_pdf_download(
    client: ZenodoClient, item: dict[str, Any], local: dict[str, Any]
) -> None:
    validate_file_entry(
        item,
        name=PDF_NAME,
        size=int(local["bytes"]),
        md5=str(local["md5"]),
    )
    url = file_download(item)
    if not url:
        raise SystemExit("Zenodo standalone PDF has no content link")
    raw = client.request_bytes(url)
    if len(raw) != local["bytes"]:
        raise SystemExit("Zenodo standalone PDF download size mismatch")
    if hashlib.sha256(raw).hexdigest() != local["sha256"]:
        raise SystemExit("Zenodo standalone PDF download SHA-256 mismatch")


def get_deposition(client: ZenodoClient) -> dict[str, Any]:
    value = client.request("GET", f"/deposit/depositions/{RECORD_ID}")
    record = as_object(value, "deposition")
    validate_identity(record)
    return record


def get_public_record(client: ZenodoClient) -> dict[str, Any]:
    value = client.request("GET", f"/records/{RECORD_ID}")
    record = as_object(value, "public record")
    validate_identity(record)
    return record


def unlock_published_files(client: ZenodoClient) -> None:
    """Use Zenodo's published-file modification action to unlock the draft bucket."""
    public = get_public_record(client)
    links = public.get("links")
    action = links.get("file_modification") if isinstance(links, dict) else None
    expected = f"{client.api_base}/records/{RECORD_ID}/file-modification"
    if action != expected:
        raise SystemExit("Zenodo public record has an unexpected file-modification link")
    request = as_object(
        client.request(
            "POST",
            action,
            payload={
                "reason": "minor packaging correction",
                "comment": FILE_MODIFICATION_COMMENT,
            },
        ),
        "file-modification",
    )
    if str(request.get("status") or "").lower() != "accepted":
        raise SystemExit("Zenodo did not accept the published-file modification action")


def repair(
    client: ZenodoClient,
    pdf_path: Path,
    *,
    acknowledgement: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    if acknowledgement != ACKNOWLEDGEMENT:
        raise SystemExit("exact research preprint repair acknowledgement is required")
    local = validate_local_pdf(pdf_path)
    current = get_deposition(client)
    validate_archive_preserved(current)
    current_files = files_by_name(current)

    current_pdf_state = None
    if PDF_NAME in current_files:
        current_pdf_state = classify_pdf_entry(current_files[PDF_NAME])
        if current_pdf_state == "corrected":
            verify_pdf_download(client, current_files[PDF_NAME], local)
            public = get_public_record(client)
            validate_archive_preserved(public)
            public_pdf = files_by_name(public).get(PDF_NAME)
            if public_pdf is not None:
                public_pdf_state = classify_pdf_entry(public_pdf)
                if public_pdf_state == "corrected":
                    verify_pdf_download(client, public_pdf, local)
                    return {
                        "schema": "trinityaccord.zenodo-pdf-correction-receipt.v2",
                        "status": "already_corrected_verified",
                        "mutation_performed": False,
                        "record_id": RECORD_ID,
                        "doi": DOI,
                        "record_url": f"https://zenodo.org/records/{RECORD_ID}",
                        "standalone_pdf": local,
                        "original_archive_preserved": True,
                    }

    unexpected = set(current_files) - {ARCHIVE_NAME}
    if unexpected - {PDF_NAME}:
        raise SystemExit(
            "unexpected Zenodo files require human review before correction: "
            f"{sorted(unexpected - {PDF_NAME})}"
        )
    validate_repair_window(current, now or datetime.now(timezone.utc))

    state = str(current.get("state") or "").lower()
    resuming_file_edit = state == "inprogress"
    if state == "done":
        current = as_object(
            client.request(
                "POST",
                f"/deposit/depositions/{RECORD_ID}/actions/edit",
                payload={},
            ),
            "edit-unlock",
        )
        validate_identity(current)
    elif state != "inprogress":
        raise SystemExit(f"Zenodo deposition is in an unsupported state: {state!r}")

    current = get_deposition(client)
    validate_archive_preserved(current)
    draft_files = files_by_name(current)
    if set(draft_files) - {ARCHIVE_NAME, PDF_NAME}:
        raise SystemExit("Zenodo edit draft contains unexpected files")

    # A normal edit action unlocks metadata only. Zenodo requires its
    # dedicated, policy-checked action before published files can be changed.
    # An in-progress draft is the safe retry state left after that action was
    # accepted, so do not submit a duplicate file-modification request.
    if not resuming_file_edit:
        unlock_published_files(client)
    current = get_deposition(client)
    validate_archive_preserved(current)
    links = current.get("links")
    bucket = links.get("bucket") if isinstance(links, dict) else None
    if not isinstance(bucket, str) or not bucket:
        raise SystemExit("Zenodo edit draft has no upload bucket")
    draft_files = files_by_name(current)
    remote_pdf = draft_files.get(PDF_NAME)
    if remote_pdf is not None:
        pdf_state = classify_pdf_entry(remote_pdf)
        if pdf_state == "corrected":
            verify_pdf_download(client, remote_pdf, local)
    if remote_pdf is None or pdf_state == "prior":
        # Zenodo's bucket is an object store: PUT to the existing key advances
        # that file's head version. This avoids relying on the representation-
        # specific `links.self` URL returned for a published file.
        client.request(
            "PUT",
            bucket.rstrip("/") + "/" + urllib.parse.quote(PDF_NAME),
            data=pdf_path.read_bytes(),
            # Zenodo's bucket endpoint accepts file bytes only as an opaque
            # octet stream, regardless of the uploaded file's media type.
            content_type="application/octet-stream",
        )

    current = get_deposition(client)
    validate_archive_preserved(current)
    draft_files = files_by_name(current)
    if PDF_NAME not in draft_files:
        raise SystemExit("Zenodo standalone PDF did not appear after upload")
    verify_pdf_download(client, draft_files[PDF_NAME], local)

    published = as_object(
        client.request(
            "POST",
            f"/deposit/depositions/{RECORD_ID}/actions/publish",
            payload={},
        ),
        "republish",
    )
    validate_identity(published)

    public = get_public_record(client)
    validate_archive_preserved(public)
    public_files = files_by_name(public)
    if set(public_files) != {ARCHIVE_NAME, PDF_NAME}:
        raise SystemExit("Zenodo public file set does not match the bounded correction")
    if classify_pdf_entry(public_files[PDF_NAME]) != "corrected":
        raise SystemExit("Zenodo public PDF is not the corrected revision")
    verify_pdf_download(client, public_files[PDF_NAME], local)
    return {
        "schema": "trinityaccord.zenodo-pdf-correction-receipt.v2",
        "status": "corrected_published_verified",
        "mutation_performed": True,
        "record_id": RECORD_ID,
        "doi": DOI,
        "record_url": f"https://zenodo.org/records/{RECORD_ID}",
        "standalone_pdf": local,
        "original_archive_preserved": True,
        "prior_standalone_pdf_sha256": PRIOR_PDF_SHA256,
        "scope": (
            "replace only the known standalone PDF correction; preserve the original "
            "archive, metadata, record, version, DOI, and Canon"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument(
        "--api-base",
        default=os.environ.get("ZENODO_API_BASE", DEFAULT_API),
    )
    parser.add_argument(
        "--acknowledgement",
        default=os.environ.get("ZENODO_RESEARCH_FILE_REPAIR_ACK", ""),
    )
    args = parser.parse_args()
    client = ZenodoClient(
        os.environ.get("ZENODO_ACCESS_TOKEN", "").strip(),
        args.api_base,
    )
    receipt = repair(
        client,
        args.pdf.resolve(),
        acknowledgement=args.acknowledgement,
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
