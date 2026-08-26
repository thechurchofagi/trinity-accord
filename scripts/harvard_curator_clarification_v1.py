#!/usr/bin/env python3
"""Apply Harvard Dataverse curator clarification to the existing v1.0 draft.

This program is deliberately narrow and fail-closed. It may only:
- update the draft Dataset Description with a plain-language project definition
  and explicit generative-AI disclosure;
- add one curator-facing README without changing the preserved source archive;
- resubmit the same initial draft for curator review.

It never publishes the Dataset, creates a new Dataset, replaces the preserved
archive, or authorizes a post-publication v1.1 mutation.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import httpx

SERVER = "https://dataverse.harvard.edu"
PID = "doi:10.7910/DVN/YUCG12"
DATASET_ID = 14153533
ARCHIVE_FILE_ID = 14153535
ARCHIVE_NAME = "trinity-accord-full-project-preservation-bundle.github-artifact.zip.bin"
ARCHIVE_BYTES = 1_951_603_950
ARCHIVE_SHA256 = "9c3c8bd513dfe4919efe56084c138fce18de313f59d67cd7c9484d9b5b75c9f2"
BUNDLE_IDENTITY_SHA256 = "4930b9d6cd4968f3ba75de9dc46a396af7f37f97d128d1619ae829239656989d"
TERMS_SHA256 = "81499f397fa433c9fa50ce36def425bb3ae318e28fe7eab9b0f5e02063b5b140"
README_PATH = Path("preservation/HARVARD-DATAVERSE-CURATOR-README-v1.md")
README_UPLOAD_NAME = "README-HARVARD-DATAVERSE-v1.md"
USER_AGENT = "trinity-accord-harvard-curator-clarification/1.0"

DESCRIPTION = (
    "Trinity Accord is a human-led, generative-AI-assisted archival research and software project. "
    "It preserves a dated record of human–AI collaboration together with the technical provenance "
    "needed to inspect, reconstruct, and audit that record over time. The project includes public "
    "texts and records addressed to possible future AI systems, source code and machine-readable "
    "manifests, provenance and timestamp evidence, cryptographic checksums, recovery materials, "
    "historical context, and verification tools. Within the project's own architecture, its fixed "
    "canonical core consists of three Bitcoin-inscribed records; the broader repository and this "
    "Dataverse deposit preserve the surrounding research/software object and its provenance.\n\n"
    "This deposit contains AI-generated and AI-assisted content. Generative AI contributed "
    "substantively during development, including drafting, analysis, coding, editing, and iterative "
    "content generation. The human creator initiated and directed the project, selected and curated "
    "the retained materials, made the project-level publication and preservation decisions, and "
    "assumes responsibility for the final deposited record. The archive intentionally preserves the "
    "resulting human–AI collaborative record with its provenance visible rather than presenting all "
    "deposited language or code as exclusively human-authored.\n\n"
    "This Harvard Dataverse v1.0 deposit is a frozen preservation snapshot of the project record and "
    "includes the exact full-project preservation archive plus review-oriented companion files. The "
    "project's specialized phrase 'completed pre-ASI human–superintelligence relation record' is a "
    "description used within the project; it is not a claim that AGI or superintelligence existed "
    "during the formation period, nor a claim of scientific proof or institutional endorsement."
)


class ClarificationError(RuntimeError):
    pass


def log(message: str) -> None:
    print(f"[harvard-curator-clarification] {message}", flush=True)


def headers(token: str) -> dict[str, str]:
    return {"X-Dataverse-key": token, "User-Agent": USER_AGENT}


def require(response: httpx.Response, expected: set[int], label: str) -> httpx.Response:
    if response.status_code not in expected:
        raise ClarificationError(
            f"{label}: HTTP {response.status_code}: {response.text[:1800]}"
        )
    return response


def normalize_text(value: Any) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def latest_version(dataset: dict[str, Any]) -> dict[str, Any]:
    version = dataset.get("latestVersion") or dataset.get("latestVersionInfo")
    if not isinstance(version, dict):
        raise ClarificationError("Harvard latestVersion is missing")
    return version


def data_files(version: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in (version.get("files") or []) if isinstance(item, dict)]


def file_meta(item: dict[str, Any]) -> tuple[int, str, int]:
    data_file = item.get("dataFile") or {}
    return (
        int(data_file.get("id") or -1),
        str(data_file.get("filename") or ""),
        int(data_file.get("filesize") or -1),
    )


def get_dataset(client: httpx.Client, token: str) -> dict[str, Any]:
    response = require(
        client.get(
            f"{SERVER}/api/datasets/:persistentId/",
            headers=headers(token),
            params={"persistentId": PID},
            timeout=120,
        ),
        {200},
        "dataset read",
    )
    payload = response.json()
    data = payload.get("data") or {}
    if int(data.get("id") or -1) != DATASET_ID:
        raise ClarificationError("Harvard Dataset id changed unexpectedly")
    return data


def get_versions(client: httpx.Client, token: str) -> list[dict[str, Any]]:
    response = require(
        client.get(
            f"{SERVER}/api/datasets/{DATASET_ID}/versions",
            headers=headers(token),
            timeout=120,
        ),
        {200},
        "version listing",
    )
    versions = response.json().get("data") or []
    if not isinstance(versions, list) or not versions:
        raise ClarificationError("Harvard version listing is empty or invalid")
    if any(str(v.get("versionState") or "") == "RELEASED" for v in versions if isinstance(v, dict)):
        raise ClarificationError("Dataset already has a released version; refusing any mutation")
    if len(versions) != 1:
        raise ClarificationError(
            f"expected exactly one initial draft version, observed {len(versions)}; refusing possible v1.1 path"
        )
    only = versions[0]
    if str(only.get("versionState") or "") != "DRAFT":
        raise ClarificationError(f"expected DRAFT version, got {only.get('versionState')!r}")
    return versions


def get_in_review_lock(client: httpx.Client, token: str) -> bool:
    response = require(
        client.get(
            f"{SERVER}/api/datasets/{DATASET_ID}/locks",
            headers=headers(token),
            params={"type": "InReview"},
            timeout=120,
        ),
        {200},
        "InReview lock read",
    )
    locks = response.json().get("data") or []
    return any(isinstance(item, dict) and item.get("lockType") == "InReview" for item in locks)


def verify_invariants(version: dict[str, Any]) -> None:
    if str(version.get("versionState") or "") != "DRAFT":
        raise ClarificationError("live Harvard version is not DRAFT")
    terms = normalize_text(version.get("termsOfUse"))
    if sha256_text(terms) != TERMS_SHA256:
        raise ClarificationError("Harvard Terms of Use hash changed unexpectedly")

    archive = [item for item in data_files(version) if file_meta(item)[1] == ARCHIVE_NAME]
    if len(archive) != 1:
        raise ClarificationError("preserved archive is not uniquely present")
    observed = file_meta(archive[0])
    expected = (ARCHIVE_FILE_ID, ARCHIVE_NAME, ARCHIVE_BYTES)
    if observed != expected:
        raise ClarificationError(
            f"preserved archive identity mismatch observed={observed!r} expected={expected!r}"
        )

    state_path = Path("preservation/harvard-dataverse-state.json")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    source = state.get("source") or {}
    if not (
        state.get("persistent_id") == PID
        and int(state.get("dataset_id") or -1) == DATASET_ID
        and int(state.get("archive_file_id") or -1) == ARCHIVE_FILE_ID
        and state.get("version_state") == "DRAFT"
        and state.get("status") == "terms_corrected_submitted_for_review_v1_0"
        and state.get("target_completion_policy") == "v1_0_public_readback_only"
        and state.get("post_release_harvard_mutation_authorized") is False
        and state.get("authenticated_readback_verified") is True
        and int(state.get("authenticated_readback_bytes") or -1) == ARCHIVE_BYTES
        and str(state.get("authenticated_readback_sha256") or "").lower() == ARCHIVE_SHA256
        and str(source.get("artifact_filename") or "") == ARCHIVE_NAME
        and int(source.get("artifact_bytes") or -1) == ARCHIVE_BYTES
        and str(source.get("artifact_sha256") or "").lower() == ARCHIVE_SHA256
        and str(source.get("bundle_identity_sha256") or "").lower() == BUNDLE_IDENTITY_SHA256
    ):
        raise ClarificationError("local Harvard v1.0 preservation invariants do not match")


def description_value(version: dict[str, Any]) -> str:
    citation = (version.get("metadataBlocks") or {}).get("citation") or {}
    for field in citation.get("fields") or []:
        if isinstance(field, dict) and field.get("typeName") == "dsDescription":
            values = field.get("value") or []
            if values and isinstance(values[0], dict):
                primitive = values[0].get("dsDescriptionValue") or {}
                return normalize_text(primitive.get("value"))
    return ""


def update_description(client: httpx.Client, token: str) -> None:
    response = require(
        client.get(
            f"{SERVER}/api/datasets/:persistentId/versions/:draft",
            headers=headers(token),
            params={"persistentId": PID},
            timeout=120,
        ),
        {200},
        "draft metadata read",
    )
    draft = response.json().get("data") or {}
    blocks = copy.deepcopy(draft.get("metadataBlocks") or {})
    citation = blocks.get("citation")
    if not isinstance(citation, dict):
        raise ClarificationError("citation metadata block missing")
    fields = citation.get("fields")
    if not isinstance(fields, list):
        raise ClarificationError("citation fields missing")

    replacement = {
        "typeName": "dsDescription",
        "multiple": True,
        "typeClass": "compound",
        "value": [
            {
                "dsDescriptionValue": {
                    "typeName": "dsDescriptionValue",
                    "multiple": False,
                    "typeClass": "primitive",
                    "value": DESCRIPTION,
                }
            }
        ],
    }
    found = False
    for index, field in enumerate(fields):
        if isinstance(field, dict) and field.get("typeName") == "dsDescription":
            fields[index] = replacement
            found = True
            break
    if not found:
        fields.append(replacement)

    payload = {"metadataBlocks": blocks}
    updated = require(
        client.put(
            f"{SERVER}/api/datasets/:persistentId/versions/:draft",
            headers={**headers(token), "Content-Type": "application/json"},
            params={"persistentId": PID},
            json=payload,
            timeout=120,
        ),
        {200},
        "dataset description update",
    )
    log(f"DATASET_DESCRIPTION_UPDATE PASS HTTP={updated.status_code} sha256={sha256_text(DESCRIPTION)}")


def supported_digest(path: Path, checksum_type: str) -> str:
    algorithms = {"MD5": "md5", "SHA-1": "sha1", "SHA-256": "sha256", "SHA-512": "sha512"}
    algorithm = algorithms.get(checksum_type.upper())
    if algorithm is None:
        raise ClarificationError(f"unsupported Dataverse checksum type {checksum_type!r}")
    h = hashlib.new(algorithm)
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def verify_existing_readme(item: dict[str, Any]) -> int:
    file_id, name, size = file_meta(item)
    if name != README_UPLOAD_NAME or size != README_PATH.stat().st_size:
        raise ClarificationError("existing curator README identity/size mismatch")
    checksum = (item.get("dataFile") or {}).get("checksum") or {}
    checksum_type = str(checksum.get("type") or "")
    checksum_value = str(checksum.get("value") or "").lower()
    if not checksum_type or not checksum_value:
        raise ClarificationError("existing curator README has no checksum")
    if supported_digest(README_PATH, checksum_type) != checksum_value:
        raise ClarificationError("existing curator README checksum mismatch")
    return file_id


def ensure_readme(client: httpx.Client, token: str, version: dict[str, Any]) -> tuple[int, str]:
    if not README_PATH.is_file():
        raise ClarificationError(f"missing local curator README: {README_PATH}")
    matches = [item for item in data_files(version) if file_meta(item)[1] == README_UPLOAD_NAME]
    if len(matches) > 1:
        raise ClarificationError("multiple curator README files already exist")
    if matches:
        file_id = verify_existing_readme(matches[0])
        log(f"CURATOR_README VERIFIED existing id={file_id} sha256={sha256_file(README_PATH)}")
        return file_id, "verified_existing"

    metadata = json.dumps(
        {
            "description": "START HERE: plain-language definition of this Harvard Dataverse deposit and explicit generative-AI disclosure requested during curator review.",
            "categories": ["Documentation"],
            "restrict": "false",
            "tabIngest": "false",
        }
    )
    with README_PATH.open("rb") as fh:
        response = require(
            client.post(
                f"{SERVER}/api/datasets/:persistentId/add",
                headers=headers(token),
                params={"persistentId": PID},
                files={"file": (README_UPLOAD_NAME, fh, "text/markdown")},
                data={"jsonData": metadata},
                timeout=600,
            ),
            {200, 201},
            "curator README upload",
        )
    log(f"CURATOR_README_UPLOAD PASS HTTP={response.status_code} sha256={sha256_file(README_PATH)}")

    live = latest_version(get_dataset(client, token))
    matches = [item for item in data_files(live) if file_meta(item)[1] == README_UPLOAD_NAME]
    if len(matches) != 1:
        raise ClarificationError("curator README not uniquely present after upload")
    file_id = verify_existing_readme(matches[0])
    return file_id, "uploaded"


def submit_for_review(client: httpx.Client, token: str) -> str:
    response = client.post(
        f"{SERVER}/api/datasets/:persistentId/submitForReview",
        headers=headers(token),
        params={"persistentId": PID},
        timeout=120,
    )
    if response.status_code in {200, 201, 202}:
        log(f"SUBMIT_FOR_REVIEW PASS HTTP={response.status_code}")
        return "submitted"
    body = response.text[:1800]
    lower = body.lower()
    if response.status_code in {400, 403, 409} and (
        "already in review" in lower
        or "already submitted" in lower
        or ("review" in lower and "already" in lower)
        or "locked" in lower
    ):
        log(f"SUBMIT_FOR_REVIEW already-pending HTTP={response.status_code}")
        return "already_pending"
    raise ClarificationError(f"submit for review: HTTP {response.status_code}: {body}")


def main() -> int:
    token = os.environ.get("HD_API_TOKEN", "").strip()
    if not token:
        raise ClarificationError("HD_API_TOKEN is missing")
    output_dir = Path(os.environ.get("OUTPUT_DIR", "")).expanduser() if os.environ.get("OUTPUT_DIR") else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(follow_redirects=True, timeout=httpx.Timeout(120.0, read=300.0)) as client:
        versions_before = get_versions(client, token)
        dataset = get_dataset(client, token)
        version = latest_version(dataset)
        verify_invariants(version)
        if get_in_review_lock(client, token):
            raise ClarificationError("Dataset is currently InReview; refusing curator-requested draft mutation")
        log(f"PREFLIGHT PASS state=DRAFT files={len(data_files(version))} versions={len(versions_before)}")

        update_description(client, token)
        after_description = latest_version(get_dataset(client, token))
        verify_invariants(after_description)
        if description_value(after_description) != normalize_text(DESCRIPTION):
            raise ClarificationError("Dataset Description readback does not match requested clarification")
        log("DATASET_DESCRIPTION_READBACK PASS")

        readme_id, readme_action = ensure_readme(client, token, after_description)
        after_readme = latest_version(get_dataset(client, token))
        verify_invariants(after_readme)
        if description_value(after_readme) != normalize_text(DESCRIPTION):
            raise ClarificationError("Dataset Description changed during README upload")
        matches = [item for item in data_files(after_readme) if file_meta(item)[1] == README_UPLOAD_NAME]
        if len(matches) != 1 or verify_existing_readme(matches[0]) != readme_id:
            raise ClarificationError("curator README final verification failed")

        versions_after_mutation = get_versions(client, token)
        if len(versions_after_mutation) != len(versions_before):
            raise ClarificationError("version count changed during clarification; refusing possible v1.1 path")

        review_result = submit_for_review(client, token)
        versions_after_submit = get_versions(client, token)
        if len(versions_after_submit) != 1 or str(versions_after_submit[0].get("versionState") or "") != "DRAFT":
            raise ClarificationError("review submission unexpectedly changed version topology")

        final_dataset = get_dataset(client, token)
        final_version = latest_version(final_dataset)
        verify_invariants(final_version)
        if description_value(final_version) != normalize_text(DESCRIPTION):
            raise ClarificationError("final Dataset Description readback mismatch")
        final_readme = [item for item in data_files(final_version) if file_meta(item)[1] == README_UPLOAD_NAME]
        if len(final_readme) != 1:
            raise ClarificationError("final curator README missing")
        final_readme_id = verify_existing_readme(final_readme[0])

        audit = {
            "schema": "trinity-accord.harvard-curator-clarification.v1",
            "persistent_id": PID,
            "dataset_id": DATASET_ID,
            "version_state": "DRAFT",
            "target_version": "1.0",
            "new_version_created": False,
            "post_release_mutation": False,
            "archive_file_id": ARCHIVE_FILE_ID,
            "archive_filename": ARCHIVE_NAME,
            "archive_bytes": ARCHIVE_BYTES,
            "archive_sha256": ARCHIVE_SHA256,
            "dataset_description_sha256": sha256_text(DESCRIPTION),
            "ai_disclosure_present": "AI-generated and AI-assisted content" in DESCRIPTION,
            "curator_readme_filename": README_UPLOAD_NAME,
            "curator_readme_file_id": final_readme_id,
            "curator_readme_sha256": sha256_file(README_PATH),
            "curator_readme_action": readme_action,
            "review_submission": review_result,
            "final_file_count": len(data_files(final_version)),
        }
        if output_dir:
            (output_dir / "harvard-curator-clarification-audit.json").write_text(
                json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
        print(json.dumps(audit, indent=2, ensure_ascii=False))
        log("HARVARD CURATOR CLARIFICATION COMPLETE v1.0 draft resubmitted; no v1.1 created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
