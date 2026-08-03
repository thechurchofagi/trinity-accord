# gateway/receipts.py
"""Receipt generation for accepted submissions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .canonical import sha256_canonical_json
from .runtime import get_runtime_info

RECEIPT_HASH_PREFIX_LEN = 24
LEGACY_RECEIPT_HASH_PREFIX_LEN = 12


def compute_receipt_sha256(receipt: dict[str, Any]) -> str:
    material = dict(receipt)
    material.pop("receipt_sha256", None)
    return sha256_canonical_json(material)


def verify_receipt_sha256(receipt: dict[str, Any]) -> tuple[bool, str]:
    """Verify that the receipt's receipt_sha256 matches the computed hash.

    Returns (True, "") on success, (False, error_message) on failure.
    """
    expected = receipt.get("receipt_sha256")
    if not isinstance(expected, str) or not expected:
        return False, "receipt missing receipt_sha256"
    actual = compute_receipt_sha256(receipt)
    if expected != actual:
        return False, f"receipt_sha256 mismatch: expected {expected}, got {actual}"
    return True, ""


def make_legacy_receipt_id(submission_sha256: str, now: datetime | None = None) -> str:
    """Generate the legacy 12-hex receipt ID for duplicate lookup only."""
    if now is None:
        now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    return f"rcg-{date_part}-{submission_sha256[:LEGACY_RECEIPT_HASH_PREFIX_LEN]}"


def make_receipt_id(submission_sha256: str, now: datetime | None = None) -> str:
    """Generate the current receipt ID.

    Format: ``rcg-YYYYMMDD-<first_24_hex_chars_of_submission_sha256>``.

    Legacy duplicate lookup may also recognize the older 12-hex receipt ID
    produced by :func:`make_legacy_receipt_id`, but new receipts use 24 hex.
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
    gateway_version: str | None = None,
    oath_verification_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a receipt dict for a persisted submission.

    The receipt is immutable once created — callers must NOT mutate it after
    :func:`sha256_canonical_json` has been computed. Any runtime-only metadata
    (e.g. ``commit_sha``) should be returned at the response envelope level,
    not inside the receipt body.

    ``gateway_version`` defaults to the deployed runtime version. Callers may
    still supply an explicit value for deterministic fixtures and migrations.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    if gateway_version is None:
        gateway_version = str(get_runtime_info()["version"])

    receipt: dict[str, Any] = {
        "server_receipt_id": make_receipt_id(submission_sha256, now),
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
