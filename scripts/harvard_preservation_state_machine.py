#!/usr/bin/env python3
"""Fail-closed Harvard Dataverse preservation state machine.

This script continues the already-created Harvard Dataset without creating a new
Dataset or re-uploading the large archive when the exact registered file is
already present. Harvard Dataverse uses a Submit-for-Review workflow for ordinary
depositors, so publication can require repository staff action.

State transitions:

  DRAFT archive-only
    -> authenticated full-byte readback
    -> submitForReview for v1.0

  RELEASED archive-only
    -> anonymous/public full-byte readback
    -> generate and upload public-readback receipt
    -> submitForReview for v1.1

  RELEASED archive + receipt
    -> anonymous/public full-byte readback of archive
    -> validate receipt
    -> COMPLETE

The Harvard Dataset is always a non-amending institutional preservation mirror.
The Bitcoin Originals remain the canonical authority. Zenodo concept/version/
checkpoint DOI semantics are preserved and explicitly recorded in every state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

SERVER = "https://dataverse.harvard.edu"
PID = os.environ.get("HARVARD_PID", "doi:10.7910/DVN/YUCG12").strip()
ARCHIVE_NAME = os.environ.get(
    "HARVARD_ARCHIVE_NAME",
    "trinity-accord-full-project-preservation-bundle.github-artifact.zip.bin",
).strip()
EXPECTED_BYTES = int(os.environ.get("HARVARD_ARTIFACT_BYTES", "1951603950"))
EXPECTED_SHA256 = os.environ.get(
    "HARVARD_ARTIFACT_SHA256",
    "9c3c8bd513dfe4919efe56084c138fce18de313f59d67cd7c9484d9b5b75c9f2",
).strip().lower()
BUNDLE_IDENTITY = os.environ.get(
    "HARVARD_BUNDLE_IDENTITY_SHA256",
    "4930b9d6cd4968f3ba75de9dc46a396af7f37f97d128d1619ae829239656989d",
).strip().lower()
SOURCE_RUN_ID = int(os.environ.get("HARVARD_SOURCE_RUN_ID", "32368866492"))
SOURCE_SHA = os.environ.get(
    "HARVARD_SOURCE_GIT_SHA",
    "07cd79ba7b98294a0ff9bc45d76f305609f8a0aa",
).strip()
RECEIPT_NAME = "harvard-publication-receipt.json"
USER_AGENT = "trinity-accord-harvard-preservation-state-machine/1.0"
CHUNK = 8 * 1024 * 1024

ZENODO_RELATIONSHIP = {
    "core_repository_concept_doi": "10.5281/zenodo.21739343",
    "current_verified_repository_version_doi": "10.5281/zenodo.22020122",
    "immutable_sequence_4_evidence_checkpoint_doi": "10.5281/zenodo.21859437",
    "polygon_base_sidechain_doi": "10.5281/zenodo.22012616",
    "relationship": (
        "Harvard DOI is a second-institutional non-amending preservation mirror of "
        "the full-project preservation bundle. It does not supersede the Zenodo "
        "concept DOI, any immutable Zenodo version DOI, or the Sequence-4 evidence "
        "checkpoint DOI."
    ),
}


class StateMachineError(RuntimeError):
    pass


def log(message: str) -> None:
    print(f"[harvard-state] {message}", flush=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hd_headers(token: str) -> dict[str, str]:
    return {"X-Dataverse-key": token, "User-Agent": USER_AGENT}


def require(response: httpx.Response, allowed: tuple[int, ...], label: str) -> None:
    if response.status_code not in allowed:
        body = response.text[:1500]
        raise StateMachineError(f"{label}: HTTP {response.status_code}: {body}")


def get_dataset(client: httpx.Client, token: str) -> dict[str, Any]:
    response = client.get(
        f"{SERVER}/api/datasets/:persistentId/",
        headers=hd_headers(token),
        params={"persistentId": PID},
    )
    require(response, (200,), "Harvard Dataset lookup")
    payload = response.json()
    if payload.get("status") not in (None, "OK"):
        raise StateMachineError(f"Harvard Dataset lookup returned status={payload.get('status')!r}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise StateMachineError("Harvard Dataset lookup has no data object")
    return data


def latest_version(data: dict[str, Any]) -> dict[str, Any]:
    version = data.get("latestVersion")
    if not isinstance(version, dict):
        raise StateMachineError("Harvard Dataset has no latestVersion object")
    return version


def data_files(version: dict[str, Any]) -> list[dict[str, Any]]:
    files = version.get("files", [])
    if not isinstance(files, list):
        raise StateMachineError("Harvard Dataset latestVersion.files is not a list")
    return files


def find_named_file(version: dict[str, Any], filename: str) -> dict[str, Any] | None:
    matches: list[dict[str, Any]] = []
    for item in data_files(version):
        if not isinstance(item, dict):
            continue
        df = item.get("dataFile", {})
        if isinstance(df, dict) and df.get("filename") == filename:
            matches.append(item)
    if len(matches) > 1:
        raise StateMachineError(f"Dataset contains duplicate filename {filename!r}")
    return matches[0] if matches else None


def get_file_id(item: dict[str, Any]) -> int:
    df = item.get("dataFile", {})
    value = df.get("id") if isinstance(df, dict) else None
    if value is None:
        raise StateMachineError("Dataverse file entry has no id")
    return int(value)


def normalize_checksum(df: dict[str, Any]) -> tuple[str, str]:
    checksum = df.get("checksum")
    if not isinstance(checksum, dict):
        return "", ""
    ctype = str(checksum.get("type") or checksum.get("@type") or "").upper()
    value = str(checksum.get("value") or checksum.get("@value") or "").lower()
    return ctype, value


def verify_archive_metadata(item: dict[str, Any]) -> int:
    df = item.get("dataFile", {})
    if not isinstance(df, dict):
        raise StateMachineError("archive entry has no dataFile object")
    filename = str(df.get("filename") or "")
    if filename != ARCHIVE_NAME:
        raise StateMachineError(f"archive filename mismatch: {filename!r}")
    size_value = df.get("filesize", df.get("fileSize"))
    if size_value is None:
        raise StateMachineError("archive file metadata has no size")
    if int(size_value) != EXPECTED_BYTES:
        raise StateMachineError(
            f"archive size mismatch in Dataverse metadata: {size_value} != {EXPECTED_BYTES}"
        )
    ctype, checksum = normalize_checksum(df)
    if ctype.replace("_", "-") not in ("SHA-256", "SHA256"):
        raise StateMachineError(f"archive checksum type is not SHA-256: {ctype!r}")
    if checksum != EXPECTED_SHA256:
        raise StateMachineError(
            f"archive checksum mismatch in Dataverse metadata: {checksum} != {EXPECTED_SHA256}"
        )
    file_id = get_file_id(item)
    log(
        f"archive_metadata PASS file_id={file_id} bytes={EXPECTED_BYTES} "
        f"sha256={EXPECTED_SHA256}"
    )
    return file_id


def stream_sha256(
    client: httpx.Client,
    file_id: int,
    token: str | None,
    label: str,
) -> tuple[int, str]:
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["X-Dataverse-key"] = token
    total = 0
    digest = hashlib.sha256()
    with client.stream(
        "GET",
        f"{SERVER}/api/access/datafile/{file_id}",
        headers=headers,
        follow_redirects=True,
        timeout=300,
    ) as response:
        require(response, (200,), label)
        for chunk in response.iter_bytes(CHUNK):
            if not chunk:
                continue
            digest.update(chunk)
            total += len(chunk)
            if total == EXPECTED_BYTES or total % (256 * 1024 * 1024) < CHUNK:
                log(f"{label} progress={total}/{EXPECTED_BYTES}")
    value = digest.hexdigest()
    return total, value


def verify_archive_bytes(
    client: httpx.Client,
    file_id: int,
    token: str | None,
    public: bool,
) -> tuple[int, str]:
    label = "public_readback" if public else "authenticated_readback"
    total, value = stream_sha256(client, file_id, token, label)
    if total != EXPECTED_BYTES:
        raise StateMachineError(f"{label} byte mismatch: {total} != {EXPECTED_BYTES}")
    if value != EXPECTED_SHA256:
        raise StateMachineError(f"{label} sha256 mismatch: {value} != {EXPECTED_SHA256}")
    log(f"{label.upper()} PASS bytes={total} sha256={value}")
    return total, value


def submit_for_review(client: httpx.Client, token: str, phase: str) -> str:
    response = client.post(
        f"{SERVER}/api/datasets/:persistentId/submitForReview",
        headers=hd_headers(token),
        params={"persistentId": PID},
        timeout=120,
    )
    if response.status_code in (200, 201, 202):
        log(f"SUBMIT FOR REVIEW PASS phase={phase} HTTP={response.status_code}")
        return "submitted"
    body = response.text[:1500]
    lower = body.lower()
    if response.status_code in (400, 409) and (
        "review" in lower or "already" in lower or "locked" in lower
    ):
        log(f"SUBMIT FOR REVIEW already-pending phase={phase} HTTP={response.status_code}")
        return "already_pending"
    raise StateMachineError(
        f"Harvard submitForReview phase={phase}: HTTP {response.status_code}: {body}"
    )


def upload_receipt(client: httpx.Client, token: str, path: Path) -> None:
    metadata = {
        "description": (
            "Machine-readable receipt proving exact public-byte equivalence between "
            "the released Harvard archive and the verified GitHub preservation artifact."
        ),
        "categories": ["Documentation"],
        "restrict": "false",
    }
    with path.open("rb") as fh:
        response = client.post(
            f"{SERVER}/api/datasets/:persistentId/add",
            headers=hd_headers(token),
            params={"persistentId": PID},
            files={
                "file": (RECEIPT_NAME, fh, "application/json"),
                "jsonData": (None, json.dumps(metadata, separators=(",", ":"))),
            },
            timeout=120,
        )
    require(response, (200, 201), "Harvard receipt upload")
    log("receipt_upload PASS")


def base_state(dataset_id: int | None, version: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "trinity-accord.harvard-dataverse-state.v1",
        "observed_at": now_iso(),
        "server": SERVER,
        "persistent_id": PID,
        "dataset_id": dataset_id,
        "version_state": version.get("versionState"),
        "status": "unknown",
        "source": {
            "repository": "thechurchofagi/trinity-accord",
            "workflow_run_id": SOURCE_RUN_ID,
            "git_commit_sha": SOURCE_SHA,
            "artifact_filename": ARCHIVE_NAME,
            "artifact_bytes": EXPECTED_BYTES,
            "artifact_sha256": EXPECTED_SHA256,
            "bundle_identity_sha256": BUNDLE_IDENTITY,
        },
        "doi_relationship": ZENODO_RELATIONSHIP,
        "publication_semantics": {
            "role": "second_institutional_non_amending_mirror",
            "canonical_authority": "Bitcoin Originals only",
            "canonical_authority_changed": False,
            "zenodo_superseded": False,
        },
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_receipt_file(client: httpx.Client, item: dict[str, Any]) -> dict[str, Any]:
    file_id = get_file_id(item)
    response = client.get(
        f"{SERVER}/api/access/datafile/{file_id}",
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=120,
    )
    require(response, (200,), "Harvard public receipt readback")
    try:
        payload = response.json()
    except Exception as exc:
        raise StateMachineError(f"public receipt is not JSON: {exc}") from exc
    if payload.get("artifact_sha256") != EXPECTED_SHA256:
        raise StateMachineError("public receipt artifact_sha256 mismatch")
    if payload.get("artifact_bytes") != EXPECTED_BYTES:
        raise StateMachineError("public receipt artifact_bytes mismatch")
    if payload.get("public_readback_verified") is not True:
        raise StateMachineError("public receipt does not assert public_readback_verified=true")
    if payload.get("persistent_id") != PID:
        raise StateMachineError("public receipt persistent_id mismatch")
    log(f"PUBLIC RECEIPT READBACK PASS file_id={file_id}")
    return payload


def run(output_dir: Path, state_path: Path) -> int:
    token = os.environ.get("HD_API_TOKEN", "").strip()
    if not token:
        raise StateMachineError("HD_API_TOKEN is missing")

    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = output_dir / RECEIPT_NAME

    with httpx.Client(
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
        timeout=httpx.Timeout(120.0, read=300.0),
    ) as client:
        data = get_dataset(client, token)
        dataset_id_value = data.get("id")
        dataset_id = int(dataset_id_value) if dataset_id_value is not None else None
        version = latest_version(data)
        state = str(version.get("versionState") or "")
        files = data_files(version)
        archive_item = find_named_file(version, ARCHIVE_NAME)
        receipt_item = find_named_file(version, RECEIPT_NAME)
        if archive_item is None:
            raise StateMachineError(
                f"Dataset {PID} does not contain required archive {ARCHIVE_NAME!r}"
            )
        archive_file_id = verify_archive_metadata(archive_item)
        log(
            f"dataset PASS persistent_id={PID} dataset_id={dataset_id} "
            f"version_state={state} files={len(files)}"
        )

        record = base_state(dataset_id, version)
        record["archive_file_id"] = archive_file_id

        if state == "DRAFT":
            # A draft containing the exact archive but no receipt is the initial v1.0
            # review stage. The full authenticated readback proves the registered file
            # bytes before handing control to Harvard staff.
            if receipt_item is None:
                rb_bytes, rb_sha = verify_archive_bytes(
                    client, archive_file_id, token=token, public=False
                )
                review_result = submit_for_review(client, token, "v1.0")
                record.update(
                    {
                        "status": "submitted_for_review_v1_0",
                        "authenticated_readback_verified": True,
                        "authenticated_readback_bytes": rb_bytes,
                        "authenticated_readback_sha256": rb_sha,
                        "review_submission": review_result,
                        "public_readback_verified": False,
                    }
                )
                write_json(state_path, record)
                log("STATE submitted_for_review_v1_0")
                return 0

            # A draft with the receipt is the v1.1 review stage. This can occur on a
            # retry after receipt upload but before/after submitForReview.
            review_result = submit_for_review(client, token, "v1.1")
            record.update(
                {
                    "status": "submitted_for_review_v1_1",
                    "review_submission": review_result,
                    "public_readback_verified": True,
                    "note": "Public v1.0 archive readback was completed before receipt upload.",
                }
            )
            write_json(state_path, record)
            log("STATE submitted_for_review_v1_1")
            return 0

        if state != "RELEASED":
            raise StateMachineError(f"unsupported Harvard versionState={state!r}")

        # RELEASED always requires an anonymous/public byte-for-byte readback.
        rb_bytes, rb_sha = verify_archive_bytes(
            client, archive_file_id, token=None, public=True
        )
        record.update(
            {
                "public_readback_verified": True,
                "public_readback_bytes": rb_bytes,
                "public_readback_sha256": rb_sha,
            }
        )

        if receipt_item is None:
            receipt = {
                "schema": "trinity-accord-harvard-publication-receipt-v1",
                "generated_at": now_iso(),
                "server": SERVER,
                "persistent_id": PID,
                "dataset_id": dataset_id,
                "source_repository": "thechurchofagi/trinity-accord",
                "source_workflow_run_id": SOURCE_RUN_ID,
                "source_git_commit_sha": SOURCE_SHA,
                "harvard_archive_filename": ARCHIVE_NAME,
                "artifact_bytes": EXPECTED_BYTES,
                "artifact_sha256": EXPECTED_SHA256,
                "bundle_identity_sha256": BUNDLE_IDENTITY,
                "public_readback_verified": True,
                "public_readback_bytes": rb_bytes,
                "public_readback_sha256": rb_sha,
                "doi_relationship": ZENODO_RELATIONSHIP,
                "publication_semantics": {
                    "role": "second_institutional_non_amending_mirror",
                    "canonical_authority_changed": False,
                    "bitcoin_originals_replaced": False,
                    "zenodo_superseded": False,
                },
            }
            write_json(receipt_path, receipt)
            upload_receipt(client, token, receipt_path)
            # Adding the receipt creates the v1.1 draft. Submit it for the repository's
            # required administrative review.
            review_result = submit_for_review(client, token, "v1.1")
            record.update(
                {
                    "status": "submitted_for_review_v1_1",
                    "review_submission": review_result,
                    "receipt_uploaded": True,
                }
            )
            write_json(state_path, record)
            log("STATE released_v1_0_public_readback_pass_submitted_v1_1")
            return 0

        receipt_payload = validate_receipt_file(client, receipt_item)
        record.update(
            {
                "status": "complete",
                "receipt_file_id": get_file_id(receipt_item),
                "receipt_verified": True,
                "receipt_schema": receipt_payload.get("schema"),
            }
        )
        write_json(state_path, record)
        log(
            f"HARVARD PRESERVATION COMPLETE persistent_id={PID} "
            f"bytes={rb_bytes} sha256={rb_sha}"
        )
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="harvard-state-machine-output")
    parser.add_argument(
        "--state-path",
        default="preservation/harvard-dataverse-state.json",
    )
    args = parser.parse_args()
    return run(Path(args.output_dir), Path(args.state_path))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"FAIL {type(exc).__name__}: {exc}")
        raise
