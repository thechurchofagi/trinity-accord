# gateway/receipts.py
"""Receipt generation for accepted submissions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .canonical import sha256_canonical_json

RECEIPT_HASH_PREFIX_LEN = 24
LEGACY_RECEIPT_HASH_PREFIX_LEN = 12


def compute_receipt_sha256(receipt: dict[str, Any]) -> str:
    material = dict(receipt)
    material.pop("receipt_sha256", None)
    return sha256_canonical_json(material)


def make_legacy_receipt_id(submission_sha256: str, now: datetime | None = None) -> str:
    """Generate the legacy 12-hex receipt ID for duplicate lookup only."""
    if now is None:
        now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    return f"rcg-{date_part}-{submission_sha256[:LEGACY_RECEIPT_HASH_PREFIX_LEN]}"


def make_receipt_id(submission_sha256: str, now: datetime | None = None) -> str:
    """Generate a receipt ID.

    Format: ``rcg-YYYYMMDD-<first_12_hex_chars_of_submission_sha256>``
    """
    if now is None:
        now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    short_hash = submission_sha256[:RECEIPT_HASH_PREFIX_LEN]
    return f"rcg-{date_part}-{short_hash}"


def make_receipt(
    *,
    submission: dict[str, Any],
    submission_sha256: str,
    original_submission_sha256: str = "",
    stored_submission_sha256: str = "",
    record_type: str,
    received_raw_body_sha256: str = "",
    intake_submission_path: str = "",
    pending_file_path: str = "",
    receipt_path: str = "",
    file_path: str | None = None,
    now: datetime | None = None,
    gateway_version: str = "1.0.0",
    oath_verification_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a receipt dict for a persisted submission.

    The receipt is immutable once created — callers must NOT mutate it after
    :func:`sha256_canonical_json` has been computed.  Any runtime-only metadata
    (e.g. ``commit_sha``) should be returned at the response envelope level,
    not inside the receipt body.

    Parameters
    ----------
    submission:
        The original submission object.
    submission_sha256:
        SHA-256 hex digest of the canonical submission (pre-redaction).
    original_submission_sha256:
        SHA-256 of the original (pre-redaction) canonical submission.
        Defaults to ``submission_sha256`` when empty.
    stored_submission_sha256:
        SHA-256 of the redacted (persisted) canonical submission.
        Defaults to ``submission_sha256`` when empty.
    record_type:
        The resolved record type.
    received_raw_body_sha256:
        SHA-256 hex of the raw request body bytes.
    intake_submission_path:
        Repo path of the intake submission file.
    pending_file_path:
        Repo path of the pending file.
    receipt_path:
        Repo path of the receipt file.
    file_path:
        Legacy path in the repo where the record was written (if committed).
    now:
        Timestamp override (defaults to UTC now).
    gateway_version:
        Version string of this gateway service.
    oath_verification_summary:
        Summary of oath verification results (excludes raw readback).
    """
    if now is None:
        now = datetime.now(timezone.utc)

    receipt_id = make_receipt_id(submission_sha256, now)

    receipt: dict[str, Any] = {
        "server_receipt_id": receipt_id,
        "service": "record-chain-intake-gateway",
        "gateway_version": gateway_version,
        "record_type": record_type,
        "submission_sha256": submission_sha256,
        "original_submission_sha256": original_submission_sha256 or submission_sha256,
        "stored_submission_sha256": stored_submission_sha256 or submission_sha256,
        "received_raw_body_sha256": received_raw_body_sha256,
        "accepted_at": now.isoformat().replace("+00:00", "Z"),
        "raw_readback_redacted": True,
        "receipt_is_not_final_chain_record": True,
    }

    if intake_submission_path:
        receipt["intake_submission_path"] = intake_submission_path
    if pending_file_path:
        receipt["pending_file_path"] = pending_file_path
    if receipt_path:
        receipt["receipt_path"] = receipt_path
    if file_path is not None:
        receipt["file_path"] = file_path
    if oath_verification_summary is not None:
        receipt["oath_verification"] = oath_verification_summary

    # Compute a receipt hash so callers can verify receipt integrity.
    # This MUST be the last mutation — callers must not modify the receipt after this.
    receipt["receipt_sha256"] = compute_receipt_sha256(receipt)

    return receipt
