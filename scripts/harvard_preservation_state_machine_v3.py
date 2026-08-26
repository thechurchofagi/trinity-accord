#!/usr/bin/env python3
"""Harvard preservation state machine v3.

Adds fail-closed repair for a curator return caused by selecting Custom Dataset
Terms without providing Terms of Use. It preserves the exact archive identity,
reuses the already-recorded authenticated full-byte readback only when every
identity field still matches, and prevents automatic resubmission loops after a
subsequent curator return. After v1.0 publication it performs one anonymous
full-byte readback and completes without modifying Harvard or creating v1.1.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import httpx

import harvard_preservation_state_machine as impl

CUSTOM_TERMS = (
    "Archival Preservation and Verification Terms. This dataset is an institutional preservation mirror "
    "of the Trinity Accord full-project preservation bundle. It may be accessed, downloaded, cited, copied "
    "for preservation, and used for integrity and provenance verification. Materials within the bundle remain "
    "subject to any component-specific copyright, license, or third-party rights notices. Except for the foregoing "
    "archival, citation, preservation, and verification uses, this Dataverse deposit grants no additional copyright "
    "or other license to materials lacking a component-specific license. This deposit is non-amending: it does not "
    "modify, supersede, interpret, govern, or confer succession, attestation, or Canon authority over the Trinity Accord. "
    "The three Bitcoin Originals remain the sole canonical and final authority. Third-party rights, if any, remain with "
    "their respective holders."
)
CUSTOM_TERMS_SHA256 = hashlib.sha256(CUSTOM_TERMS.encode("utf-8")).hexdigest()
EXPECTED_CUSTOM_TERMS_SHA256 = "81499f397fa433c9fa50ce36def425bb3ae318e28fe7eab9b0f5e02063b5b140"
if CUSTOM_TERMS_SHA256 != EXPECTED_CUSTOM_TERMS_SHA256:
    raise RuntimeError("frozen Harvard custom terms hash mismatch")


def normalize_terms(value: Any) -> str:
    text = "" if value is None else str(value)
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")).strip()


def load_previous_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise impl.StateMachineError(f"cannot parse prior Harvard state: {exc}") from exc
    if not isinstance(payload, dict):
        raise impl.StateMachineError("prior Harvard state is not an object")
    return payload


def get_in_review_lock(client: httpx.Client, token: str, dataset_id: int) -> bool:
    response = client.get(
        f"{impl.SERVER}/api/datasets/{dataset_id}/locks",
        headers=impl.hd_headers(token),
        params={"type": "InReview"},
        timeout=120,
    )
    impl.require(response, (200,), "Harvard InReview lock lookup")
    payload = response.json()
    data = payload.get("data", [])
    if not isinstance(data, list):
        raise impl.StateMachineError("Harvard InReview lock response data is not a list")
    locked = any(isinstance(item, dict) and item.get("lockType") == "InReview" for item in data)
    impl.log(f"IN_REVIEW_LOCK {'present' if locked else 'absent'}")
    return locked


def update_custom_terms(client: httpx.Client, token: str, dataset_id: int) -> None:
    body = {"customTerms": {"termsOfUse": CUSTOM_TERMS}}
    response = client.put(
        f"{impl.SERVER}/api/datasets/{dataset_id}/license",
        headers={**impl.hd_headers(token), "Content-Type": "application/json"},
        json=body,
        timeout=120,
    )
    impl.require(response, (200,), "Harvard custom terms update")
    impl.log(f"CUSTOM_TERMS_UPDATE PASS sha256={CUSTOM_TERMS_SHA256}")


def verify_custom_terms(version: dict[str, Any]) -> None:
    observed = normalize_terms(version.get("termsOfUse"))
    expected = normalize_terms(CUSTOM_TERMS)
    if observed != expected:
        observed_hash = hashlib.sha256(observed.encode("utf-8")).hexdigest()
        raise impl.StateMachineError(
            "Harvard termsOfUse mismatch after update: "
            f"observed_sha256={observed_hash} expected_sha256={CUSTOM_TERMS_SHA256}"
        )
    impl.log(f"CUSTOM_TERMS_VERIFY PASS sha256={CUSTOM_TERMS_SHA256}")


def can_reuse_authenticated_readback(
    previous: dict[str, Any] | None,
    archive_file_id: int,
) -> bool:
    if not previous:
        return False
    source = previous.get("source")
    if not isinstance(source, dict):
        return False
    return (
        previous.get("persistent_id") == impl.PID
        and int(previous.get("archive_file_id") or -1) == archive_file_id
        and previous.get("authenticated_readback_verified") is True
        and int(previous.get("authenticated_readback_bytes") or -1) == impl.EXPECTED_BYTES
        and str(previous.get("authenticated_readback_sha256") or "").lower() == impl.EXPECTED_SHA256
        and str(source.get("artifact_filename") or "") == impl.ARCHIVE_NAME
        and int(source.get("artifact_bytes") or -1) == impl.EXPECTED_BYTES
        and str(source.get("artifact_sha256") or "").lower() == impl.EXPECTED_SHA256
        and str(source.get("bundle_identity_sha256") or "").lower() == impl.BUNDLE_IDENTITY
    )


def can_short_circuit_complete(
    previous: dict[str, Any] | None,
    *,
    dataset_id: int,
    archive_file_id: int,
) -> bool:
    """Return true only for the exact already-verified released dataset.

    A completed Harvard version is immutable. Requiring the frozen local state,
    live released-version metadata, the stable archive file ID, the explicit
    v1.0-only policy, and every source identity field lets scheduled observations
    avoid re-downloading the 1.95 GB archive every hour.
    """
    if not previous:
        return False
    source = previous.get("source")
    if not isinstance(source, dict):
        return False
    return (
        previous.get("status") == "complete"
        and previous.get("persistent_id") == impl.PID
        and int(previous.get("dataset_id") or -1) == dataset_id
        and previous.get("version_state") == "RELEASED"
        and previous.get("released_version") == "1.0"
        and int(previous.get("archive_file_id") or -1) == archive_file_id
        and previous.get("public_readback_verified") is True
        and int(previous.get("public_readback_bytes") or -1) == impl.EXPECTED_BYTES
        and str(previous.get("public_readback_sha256") or "").lower() == impl.EXPECTED_SHA256
        and previous.get("completion_policy") == "v1_0_public_readback_only"
        and previous.get("harvard_dataset_mutated_after_release") is False
        and str(source.get("artifact_filename") or "") == impl.ARCHIVE_NAME
        and int(source.get("artifact_bytes") or -1) == impl.EXPECTED_BYTES
        and str(source.get("artifact_sha256") or "").lower() == impl.EXPECTED_SHA256
        and str(source.get("bundle_identity_sha256") or "").lower() == impl.BUNDLE_IDENTITY
    )


def can_continue_unversioned_v10_draft(
    previous: dict[str, Any] | None,
    *,
    dataset_id: int,
    archive_file_id: int,
) -> bool:
    """Bind Dataverse's unnumbered initial DRAFT to the frozen v1.0 review."""
    if not previous:
        return False
    source = previous.get("source")
    if not isinstance(source, dict):
        return False
    return (
        previous.get("status")
        in {"submitted_for_review_v1_0", "terms_corrected_submitted_for_review_v1_0"}
        and previous.get("persistent_id") == impl.PID
        and int(previous.get("dataset_id") or -1) == dataset_id
        and previous.get("version_state") == "DRAFT"
        and int(previous.get("archive_file_id") or -1) == archive_file_id
        and previous.get("target_completion_policy") == "v1_0_public_readback_only"
        and previous.get("post_release_harvard_mutation_authorized") is False
        and str(source.get("artifact_filename") or "") == impl.ARCHIVE_NAME
        and int(source.get("artifact_bytes") or -1) == impl.EXPECTED_BYTES
        and str(source.get("artifact_sha256") or "").lower() == impl.EXPECTED_SHA256
        and str(source.get("bundle_identity_sha256") or "").lower() == impl.BUNDLE_IDENTITY
    )


def submit_for_review(client: httpx.Client, token: str, phase: str) -> str:
    response = client.post(
        f"{impl.SERVER}/api/datasets/:persistentId/submitForReview",
        headers=impl.hd_headers(token),
        params={"persistentId": impl.PID},
        timeout=120,
    )
    if response.status_code in (200, 201, 202):
        impl.log(f"SUBMIT FOR REVIEW PASS phase={phase} HTTP={response.status_code}")
        return "submitted"
    body = response.text[:1500]
    lower = body.lower()
    if response.status_code in (400, 403, 409) and (
        "already in review" in lower
        or "already submitted" in lower
        or ("review" in lower and "already" in lower)
        or "locked" in lower
    ):
        impl.log(f"SUBMIT FOR REVIEW already-pending phase={phase} HTTP={response.status_code}")
        return "already_pending"
    raise impl.StateMachineError(
        f"Harvard submitForReview phase={phase}: HTTP {response.status_code}: {body}"
    )


def write_v10_record(
    record: dict[str, Any],
    state_path: Path,
    *,
    archive_file_id: int,
    rb_bytes: int,
    rb_sha: str,
    reused: bool,
    review_result: str,
    terms_corrected: bool,
) -> None:
    record.update(
        {
            "status": "terms_corrected_submitted_for_review_v1_0",
            "archive_file_id": archive_file_id,
            "authenticated_readback_verified": True,
            "authenticated_readback_bytes": rb_bytes,
            "authenticated_readback_sha256": rb_sha,
            "authenticated_readback_reused": reused,
            "review_submission": review_result,
            "public_readback_verified": False,
            "target_completion_policy": "v1_0_public_readback_only",
            "post_release_harvard_mutation_authorized": False,
            "dataset_terms": {
                "mode": "Custom Dataset Terms",
                "terms_of_use_sha256": CUSTOM_TERMS_SHA256,
                "terms_corrected_after_curator_return": terms_corrected,
                "non_amending_authority_preserved": True,
            },
        }
    )
    impl.write_json(state_path, record)
    impl.log("STATE terms_corrected_submitted_for_review_v1_0")


def run_v3(output_dir: Path, state_path: Path) -> int:
    token = os.environ.get("HD_API_TOKEN", "").strip()
    if not token:
        raise impl.StateMachineError("HD_API_TOKEN is missing")

    previous = load_previous_state(state_path)

    with httpx.Client(
        headers={"User-Agent": impl.USER_AGENT},
        follow_redirects=True,
        timeout=httpx.Timeout(120.0, read=300.0),
    ) as client:
        data = impl.get_dataset(client, token)
        dataset_id_value = data.get("id")
        if dataset_id_value is None:
            raise impl.StateMachineError("Harvard Dataset has no numeric id")
        dataset_id = int(dataset_id_value)
        version = impl.latest_version(data)
        numbered_v10 = impl.require_v10(version, allow_unversioned_draft=True)
        state = str(version.get("versionState") or "")
        files = impl.data_files(version)
        archive_item = impl.find_named_file(version, impl.ARCHIVE_NAME)
        legacy_receipt_item = impl.find_named_file(version, impl.LEGACY_RECEIPT_NAME)
        if archive_item is None:
            raise impl.StateMachineError(
                f"Dataset {impl.PID} does not contain required archive {impl.ARCHIVE_NAME!r}"
            )
        archive_file_id = impl.verify_archive_metadata(archive_item)
        if not numbered_v10 and not can_continue_unversioned_v10_draft(
            previous,
            dataset_id=dataset_id,
            archive_file_id=archive_file_id,
        ):
            raise impl.StateMachineError(
                "unnumbered Harvard DRAFT is not bound to the frozen v1.0 review state; "
                "refusing to assume it is v1.0"
            )
        impl.log(
            f"dataset PASS persistent_id={impl.PID} dataset_id={dataset_id} "
            f"version_state={state} files={len(files)}"
        )
        if legacy_receipt_item is not None:
            raise impl.StateMachineError(
                "Harvard Dataset contains a legacy public-readback receipt; "
                "v1.0-only policy forbids creating or continuing a v1.1 mutation"
            )

        if state == "RELEASED":
            if can_short_circuit_complete(
                previous,
                dataset_id=dataset_id,
                archive_file_id=archive_file_id,
            ):
                # The released Dataset and exact archive metadata are unchanged;
                # retain the already-proven public-byte result without downloading
                # the same 1.95 GB file on every hourly observation.
                impl.log(
                    "HARVARD PRESERVATION COMPLETE V1.0 ALREADY VERIFIED "
                    f"persistent_id={impl.PID} archive_file_id={archive_file_id} "
                    "large_readback=skipped"
                )
                return 0

        if state != "DRAFT":
            # Any mismatch in the completion guard deliberately falls back to a
            # fresh full public-byte readback. The underlying implementation marks
            # the released v1.0 complete without uploading anything to Harvard.
            return ORIGINAL_RUN(output_dir, state_path)

        record = impl.base_state(dataset_id, version)
        record["archive_file_id"] = archive_file_id
        in_review = get_in_review_lock(client, token, dataset_id)

        observed_terms = normalize_terms(version.get("termsOfUse"))
        expected_terms = normalize_terms(CUSTOM_TERMS)
        terms_corrected = False

        if observed_terms != expected_terms:
            if in_review:
                raise impl.StateMachineError(
                    "Dataset is InReview but custom terms are missing/mismatched; "
                    "refusing to mutate a locked review submission"
                )
            update_custom_terms(client, token, dataset_id)
            terms_corrected = True

            # Re-read from Harvard and prove that only the expected Dataset/draft
            # still exists and the exact registered archive identity is unchanged.
            data = impl.get_dataset(client, token)
            if int(data.get("id") or -1) != dataset_id:
                raise impl.StateMachineError("Harvard dataset id changed after terms update")
            version = impl.latest_version(data)
            impl.require_v10(version, allow_unversioned_draft=True)
            if str(version.get("versionState") or "") != "DRAFT":
                raise impl.StateMachineError("Harvard versionState changed during terms repair")
            verify_custom_terms(version)
            archive_item = impl.find_named_file(version, impl.ARCHIVE_NAME)
            if archive_item is None:
                raise impl.StateMachineError("archive disappeared after terms update")
            archive_file_id_after = impl.verify_archive_metadata(archive_item)
            if archive_file_id_after != archive_file_id:
                raise impl.StateMachineError("archive file id changed after metadata-only terms update")
            if impl.find_named_file(version, impl.LEGACY_RECEIPT_NAME) is not None:
                raise impl.StateMachineError("unexpected receipt appeared during v1.0 terms repair")
            record = impl.base_state(dataset_id, version)
            record["archive_file_id"] = archive_file_id
        else:
            verify_custom_terms(version)

        # The archive itself was not changed by the license/terms edit. Reuse the
        # previous authenticated 1.95 GB readback only when all immutable identity
        # fields match; otherwise perform a new full-byte verification.
        reused = can_reuse_authenticated_readback(previous, archive_file_id)
        if reused:
            rb_bytes = impl.EXPECTED_BYTES
            rb_sha = impl.EXPECTED_SHA256
            impl.log(
                "AUTHENTICATED_READBACK REUSED "
                f"bytes={rb_bytes} sha256={rb_sha} file_id={archive_file_id}"
            )
        else:
            rb_bytes, rb_sha = impl.verify_archive_bytes(
                client, archive_file_id, token=token, public=False
            )

        # If this exact corrected submission was already sent and Harvard later
        # returned it again, do not create an automatic review loop. A new curator
        # reason must be inspected by a human/model before any further submission.
        previous_status = str((previous or {}).get("status") or "")
        if in_review:
            review_result = "already_pending_via_lock"
        else:
            if (
                observed_terms == expected_terms
                and not terms_corrected
                and previous_status == "terms_corrected_submitted_for_review_v1_0"
            ):
                # On 2026-08-26 the curator returned this same initial draft and
                # explicitly instructed: do not submit it for review; Harvard will
                # publish it after approval. Preserve the author-editable DRAFT and
                # never recreate the automatic review loop.
                impl.log(
                    "CURATOR DIRECT-PUBLICATION HANDOFF: leaving corrected v1.0 "
                    "DRAFT unsubmitted exactly as instructed"
                )
                review_result = "left_draft_for_curator_direct_publication"
            else:
                review_result = submit_for_review(client, token, "v1.0-terms-corrected")

        write_v10_record(
            record,
            state_path,
            archive_file_id=archive_file_id,
            rb_bytes=rb_bytes,
            rb_sha=rb_sha,
            reused=reused,
            review_result=review_result,
            terms_corrected=terms_corrected,
        )
        return 0


ORIGINAL_RUN = impl.run
impl.run = run_v3
impl.submit_for_review = submit_for_review

if __name__ == "__main__":
    try:
        raise SystemExit(impl.main())
    except Exception as exc:
        impl.log(f"FAIL {type(exc).__name__}: {exc}")
        raise
