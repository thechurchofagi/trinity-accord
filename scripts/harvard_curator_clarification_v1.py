#!/usr/bin/env python3
"""Apply Sonia Barbosa's Harvard Dataverse clarification request to v1.0.

Fail-closed rules:
- operate only on doi:10.7910/DVN/YUCG12;
- require exactly one unreleased initial DRAFT and no InReview lock;
- preserve the fixed 1.95 GB archive identity and verified Custom Terms;
- update only the Dataset Description and add one curator-facing README;
- resubmit that same initial draft; never create/publish v1.1.

The script is idempotent and can safely recover the known partial state produced
by its first run: Dataverse accepted the new Description but its draft metadata
PUT reset Custom Terms. Recovery is allowed only when the live Description is
already exactly this script's target Description; any other Terms mismatch fails.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import httpx
import harvard_preservation_state_machine_v3 as state_v3

SERVER = "https://dataverse.harvard.edu"
PID = "doi:10.7910/DVN/YUCG12"
DATASET_ID = 14153533
ARCHIVE_FILE_ID = 14153535
ARCHIVE_NAME = "trinity-accord-full-project-preservation-bundle.github-artifact.zip.bin"
ARCHIVE_BYTES = 1_951_603_950
ARCHIVE_SHA256 = "9c3c8bd513dfe4919efe56084c138fce18de313f59d67cd7c9484d9b5b75c9f2"
BUNDLE_IDENTITY_SHA256 = "4930b9d6cd4968f3ba75de9dc46a396af7f37f97d128d1619ae829239656989d"
TERMS_SHA256 = state_v3.CUSTOM_TERMS_SHA256
README_PATH = Path("preservation/HARVARD-DATAVERSE-CURATOR-README-v1.md")
README_UPLOAD_NAME = "README-HARVARD-DATAVERSE-v1.md"
STATE_PATH = Path("preservation/harvard-dataverse-state.json")
USER_AGENT = "trinity-accord-harvard-curator-clarification/1.1"

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


def log(msg: str) -> None:
    print(f"[harvard-curator-clarification] {msg}", flush=True)


def headers(token: str) -> dict[str, str]:
    return {"X-Dataverse-key": token, "User-Agent": USER_AGENT}


def require(response: httpx.Response, expected: set[int], label: str) -> httpx.Response:
    if response.status_code not in expected:
        raise ClarificationError(f"{label}: HTTP {response.status_code}: {response.text[:1800]}")
    return response


def norm(value: Any) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def digest_text(value: Any) -> str:
    return hashlib.sha256(norm(value).encode("utf-8")).hexdigest()


def digest_file(path: Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def get_dataset(client: httpx.Client, token: str) -> dict[str, Any]:
    response = require(
        client.get(f"{SERVER}/api/datasets/:persistentId/", headers=headers(token),
                   params={"persistentId": PID}, timeout=120),
        {200}, "dataset read")
    data = response.json().get("data") or {}
    if int(data.get("id") or -1) != DATASET_ID:
        raise ClarificationError("Harvard Dataset id changed unexpectedly")
    return data


def latest(data: dict[str, Any]) -> dict[str, Any]:
    version = data.get("latestVersion") or data.get("latestVersionInfo")
    if not isinstance(version, dict):
        raise ClarificationError("latestVersion missing")
    return version


def get_versions(client: httpx.Client, token: str) -> list[dict[str, Any]]:
    response = require(client.get(f"{SERVER}/api/datasets/{DATASET_ID}/versions",
                                  headers=headers(token), timeout=120),
                       {200}, "version listing")
    versions = response.json().get("data") or []
    if not isinstance(versions, list) or len(versions) != 1:
        raise ClarificationError(f"expected exactly one initial version, observed {len(versions) if isinstance(versions, list) else 'invalid'}")
    if any(str(v.get("versionState") or "") == "RELEASED" for v in versions if isinstance(v, dict)):
        raise ClarificationError("a released version exists; refusing any mutation")
    if str(versions[0].get("versionState") or "") != "DRAFT":
        raise ClarificationError(f"expected DRAFT, got {versions[0].get('versionState')!r}")
    return versions


def in_review(client: httpx.Client, token: str) -> bool:
    response = require(client.get(f"{SERVER}/api/datasets/{DATASET_ID}/locks",
                                  headers=headers(token), params={"type": "InReview"}, timeout=120),
                       {200}, "InReview lock read")
    return any(isinstance(x, dict) and x.get("lockType") == "InReview"
               for x in (response.json().get("data") or []))


def files(version: dict[str, Any]) -> list[dict[str, Any]]:
    return [x for x in (version.get("files") or []) if isinstance(x, dict)]


def file_tuple(item: dict[str, Any]) -> tuple[int, str, int]:
    df = item.get("dataFile") or {}
    return int(df.get("id") or -1), str(df.get("filename") or ""), int(df.get("filesize") or -1)


def description_value(version: dict[str, Any]) -> str:
    citation = (version.get("metadataBlocks") or {}).get("citation") or {}
    for field in citation.get("fields") or []:
        if isinstance(field, dict) and field.get("typeName") == "dsDescription":
            values = field.get("value") or []
            if values and isinstance(values[0], dict):
                primitive = values[0].get("dsDescriptionValue") or {}
                return norm(primitive.get("value"))
    return ""


def verify_local_and_archive(version: dict[str, Any]) -> None:
    if str(version.get("versionState") or "") != "DRAFT":
        raise ClarificationError("live Harvard version is not DRAFT")
    archive = [x for x in files(version) if file_tuple(x)[1] == ARCHIVE_NAME]
    if len(archive) != 1 or file_tuple(archive[0]) != (ARCHIVE_FILE_ID, ARCHIVE_NAME, ARCHIVE_BYTES):
        raise ClarificationError("fixed archive identity changed")
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    source = state.get("source") or {}
    checks = (
        state.get("persistent_id") == PID,
        int(state.get("dataset_id") or -1) == DATASET_ID,
        int(state.get("archive_file_id") or -1) == ARCHIVE_FILE_ID,
        state.get("version_state") == "DRAFT",
        state.get("status") == "terms_corrected_submitted_for_review_v1_0",
        state.get("target_completion_policy") == "v1_0_public_readback_only",
        state.get("post_release_harvard_mutation_authorized") is False,
        state.get("authenticated_readback_verified") is True,
        int(state.get("authenticated_readback_bytes") or -1) == ARCHIVE_BYTES,
        str(state.get("authenticated_readback_sha256") or "").lower() == ARCHIVE_SHA256,
        str(source.get("artifact_filename") or "") == ARCHIVE_NAME,
        int(source.get("artifact_bytes") or -1) == ARCHIVE_BYTES,
        str(source.get("artifact_sha256") or "").lower() == ARCHIVE_SHA256,
        str(source.get("bundle_identity_sha256") or "").lower() == BUNDLE_IDENTITY_SHA256,
    )
    if not all(checks):
        raise ClarificationError("local frozen v1.0 preservation invariants do not match")


def terms_ok(version: dict[str, Any]) -> bool:
    return digest_text(version.get("termsOfUse")) == TERMS_SHA256


def restore_terms(client: httpx.Client, token: str) -> None:
    response = require(
        client.put(f"{SERVER}/api/datasets/{DATASET_ID}/license",
                   headers={**headers(token), "Content-Type": "application/json"},
                   json={"customTerms": {"termsOfUse": state_v3.CUSTOM_TERMS}}, timeout=120),
        {200}, "restore Custom Terms")
    log(f"CUSTOM_TERMS_RESTORE PASS HTTP={response.status_code} sha256={TERMS_SHA256}")


def ensure_terms(client: httpx.Client, token: str, *, allow_known_recovery: bool) -> dict[str, Any]:
    version = latest(get_dataset(client, token))
    verify_local_and_archive(version)
    if terms_ok(version):
        log(f"CUSTOM_TERMS_VERIFY PASS sha256={TERMS_SHA256}")
        return version
    observed = digest_text(version.get("termsOfUse"))
    if not allow_known_recovery or description_value(version) != norm(DESCRIPTION):
        raise ClarificationError(
            f"unexpected Terms mismatch observed_sha256={observed} expected_sha256={TERMS_SHA256}; refusing overwrite")
    log(f"KNOWN_PARTIAL_RECOVERY Terms reset after successful target Description write; observed_sha256={observed}")
    restore_terms(client, token)
    repaired = latest(get_dataset(client, token))
    verify_local_and_archive(repaired)
    if not terms_ok(repaired):
        raise ClarificationError("Custom Terms readback mismatch after restoration")
    log(f"CUSTOM_TERMS_READBACK PASS sha256={TERMS_SHA256}")
    return repaired


def read_draft(client: httpx.Client, token: str) -> dict[str, Any]:
    response = require(
        client.get(f"{SERVER}/api/datasets/:persistentId/versions/:draft",
                   headers=headers(token), params={"persistentId": PID}, timeout=120),
        {200}, "draft metadata read")
    return response.json().get("data") or {}


def write_description(client: httpx.Client, token: str) -> str:
    current = latest(get_dataset(client, token))
    if description_value(current) == norm(DESCRIPTION):
        log(f"DATASET_DESCRIPTION VERIFIED existing sha256={digest_text(DESCRIPTION)}")
        return "verified_existing"
    if not terms_ok(current):
        raise ClarificationError("Terms must be verified before a new Description write")
    draft = read_draft(client, token)
    blocks = copy.deepcopy(draft.get("metadataBlocks") or {})
    citation = blocks.get("citation")
    fields = citation.get("fields") if isinstance(citation, dict) else None
    if not isinstance(fields, list):
        raise ClarificationError("citation metadata fields missing")
    replacement = {
        "typeName": "dsDescription", "multiple": True, "typeClass": "compound",
        "value": [{"dsDescriptionValue": {
            "typeName": "dsDescriptionValue", "multiple": False,
            "typeClass": "primitive", "value": DESCRIPTION}}],
    }
    for i, field in enumerate(fields):
        if isinstance(field, dict) and field.get("typeName") == "dsDescription":
            fields[i] = replacement
            break
    else:
        fields.append(replacement)
    response = require(
        client.put(f"{SERVER}/api/datasets/:persistentId/versions/:draft",
                   headers={**headers(token), "Content-Type": "application/json"},
                   params={"persistentId": PID}, json={"metadataBlocks": blocks}, timeout=120),
        {200}, "Dataset Description update")
    log(f"DATASET_DESCRIPTION_UPDATE PASS HTTP={response.status_code} sha256={digest_text(DESCRIPTION)}")
    readback = latest(get_dataset(client, token))
    if description_value(readback) != norm(DESCRIPTION):
        raise ClarificationError("Dataset Description readback mismatch")
    # Harvard's draft metadata PUT can reset Custom Terms. Restore the exact,
    # previously verified terms immediately before any further mutation.
    if not terms_ok(readback):
        restore_terms(client, token)
    final = latest(get_dataset(client, token))
    if description_value(final) != norm(DESCRIPTION) or not terms_ok(final):
        raise ClarificationError("Description/Terms atomic postcondition failed")
    log("DATASET_DESCRIPTION_AND_TERMS_READBACK PASS")
    return "updated"


def checksum_algorithm(name: str) -> str:
    table = {"MD5": "md5", "SHA-1": "sha1", "SHA-256": "sha256", "SHA-512": "sha512"}
    if name.upper() not in table:
        raise ClarificationError(f"unsupported Dataverse checksum type {name!r}")
    return table[name.upper()]


def verify_readme_item(item: dict[str, Any]) -> int:
    file_id, name, size = file_tuple(item)
    if name != README_UPLOAD_NAME or size != README_PATH.stat().st_size:
        raise ClarificationError("curator README identity/size mismatch")
    checksum = (item.get("dataFile") or {}).get("checksum") or {}
    ctype, cvalue = str(checksum.get("type") or ""), str(checksum.get("value") or "").lower()
    if not ctype or not cvalue or digest_file(README_PATH, checksum_algorithm(ctype)) != cvalue:
        raise ClarificationError("curator README checksum mismatch")
    return file_id


def ensure_readme(client: httpx.Client, token: str) -> tuple[int, str]:
    version = latest(get_dataset(client, token))
    matches = [x for x in files(version) if file_tuple(x)[1] == README_UPLOAD_NAME]
    if len(matches) > 1:
        raise ClarificationError("multiple curator README files exist")
    if matches:
        file_id = verify_readme_item(matches[0])
        log(f"CURATOR_README VERIFIED existing id={file_id} sha256={digest_file(README_PATH)}")
        return file_id, "verified_existing"
    metadata = json.dumps({
        "description": "START HERE: plain-language definition of this Harvard Dataverse deposit and explicit generative-AI disclosure requested during curator review.",
        "categories": ["Documentation"], "restrict": "false", "tabIngest": "false"})
    with README_PATH.open("rb") as fh:
        response = require(
            client.post(f"{SERVER}/api/datasets/:persistentId/add", headers=headers(token),
                        params={"persistentId": PID},
                        files={"file": (README_UPLOAD_NAME, fh, "text/markdown")},
                        data={"jsonData": metadata}, timeout=600),
            {200, 201}, "curator README upload")
    log(f"CURATOR_README_UPLOAD PASS HTTP={response.status_code} sha256={digest_file(README_PATH)}")
    live = latest(get_dataset(client, token))
    matches = [x for x in files(live) if file_tuple(x)[1] == README_UPLOAD_NAME]
    if len(matches) != 1:
        raise ClarificationError("curator README not uniquely present after upload")
    return verify_readme_item(matches[0]), "uploaded"


def submit(client: httpx.Client, token: str) -> str:
    response = client.post(f"{SERVER}/api/datasets/:persistentId/submitForReview",
                           headers=headers(token), params={"persistentId": PID}, timeout=120)
    if response.status_code in {200, 201, 202}:
        log(f"SUBMIT_FOR_REVIEW PASS HTTP={response.status_code}")
        return "submitted"
    body = response.text[:1800]
    low = body.lower()
    if response.status_code in {400, 403, 409} and (
        "already in review" in low or "already submitted" in low or
        ("review" in low and "already" in low) or "locked" in low):
        log(f"SUBMIT_FOR_REVIEW already-pending HTTP={response.status_code}")
        return "already_pending"
    raise ClarificationError(f"submit for review: HTTP {response.status_code}: {body}")


def main() -> int:
    token = os.environ.get("HD_API_TOKEN", "").strip()
    if not token:
        raise ClarificationError("HD_API_TOKEN is missing")
    output_dir = Path(os.environ.get("OUTPUT_DIR", "")) if os.environ.get("OUTPUT_DIR") else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(follow_redirects=True, timeout=httpx.Timeout(120.0, read=300.0)) as client:
        versions_before = get_versions(client, token)
        if in_review(client, token):
            raise ClarificationError("Dataset is InReview; refusing draft mutation")
        pre = latest(get_dataset(client, token))
        verify_local_and_archive(pre)
        log(f"PREFLIGHT PASS state=DRAFT files={len(files(pre))} versions={len(versions_before)}")

        # Known recovery is permitted only because the prior run successfully wrote
        # this exact target Description before detecting the Terms reset.
        ensure_terms(client, token, allow_known_recovery=True)
        description_action = write_description(client, token)
        stable = ensure_terms(client, token, allow_known_recovery=False)
        if description_value(stable) != norm(DESCRIPTION):
            raise ClarificationError("target Dataset Description is not stable")

        readme_id, readme_action = ensure_readme(client, token)
        after_readme = ensure_terms(client, token, allow_known_recovery=False)
        if description_value(after_readme) != norm(DESCRIPTION):
            raise ClarificationError("Description changed during README upload")
        if len(get_versions(client, token)) != 1:
            raise ClarificationError("version count changed; refusing possible v1.1 path")

        review = submit(client, token)
        versions_after = get_versions(client, token)
        final = latest(get_dataset(client, token))
        verify_local_and_archive(final)
        if description_value(final) != norm(DESCRIPTION) or not terms_ok(final):
            raise ClarificationError("final Description/Terms verification failed")
        final_matches = [x for x in files(final) if file_tuple(x)[1] == README_UPLOAD_NAME]
        if len(final_matches) != 1 or verify_readme_item(final_matches[0]) != readme_id:
            raise ClarificationError("final curator README verification failed")

        audit = {
            "schema": "trinity-accord.harvard-curator-clarification.v1.1",
            "persistent_id": PID,
            "dataset_id": DATASET_ID,
            "version_state": str(versions_after[0].get("versionState")),
            "target_version": "1.0",
            "new_version_created": False,
            "post_release_mutation": False,
            "archive_file_id": ARCHIVE_FILE_ID,
            "archive_filename": ARCHIVE_NAME,
            "archive_bytes": ARCHIVE_BYTES,
            "archive_sha256": ARCHIVE_SHA256,
            "terms_sha256": TERMS_SHA256,
            "dataset_description_sha256": digest_text(DESCRIPTION),
            "ai_disclosure_present": "AI-generated and AI-assisted content" in DESCRIPTION,
            "description_action": description_action,
            "curator_readme_filename": README_UPLOAD_NAME,
            "curator_readme_file_id": readme_id,
            "curator_readme_sha256": digest_file(README_PATH),
            "curator_readme_action": readme_action,
            "review_submission": review,
            "final_file_count": len(files(final)),
        }
        if output_dir:
            (output_dir / "harvard-curator-clarification-audit.json").write_text(
                json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(audit, indent=2, ensure_ascii=False))
        log("COMPLETE same initial v1.0 draft resubmitted; no v1.1 created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
