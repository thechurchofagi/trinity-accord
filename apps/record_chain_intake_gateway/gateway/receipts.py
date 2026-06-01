# gateway/receipts.py
"""Receipt generation for accepted submissions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from gateway.canonical import sha256_canonical_json


def make_receipt_id(submission_sha256: str, now: datetime | None = None) -> str:
    """Generate a receipt ID.

    Format: ``rcg-YYYYMMDD-<first_12_hex_chars_of_submission_sha256>``
    """
    if now is None:
        now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    short_hash = submission_sha256[:12]
    return f"rcg-{date_part}-{short_hash}"


def make_receipt(
    *,
    submission: dict[str, Any],
    submission_sha256: str,
    record_type: str,
    file_path: str | None = None,
    commit_sha: str | None = None,
    now: datetime | None = None,
    gateway_version: str = "1.0.0",
) -> dict[str, Any]:
    """Build a receipt dict for a persisted submission.

    Parameters
    ----------
    submission:
        The original submission object.
    submission_sha256:
        SHA-256 hex digest of the canonical submission.
    record_type:
        The resolved record type.
    file_path:
        Path in the repo where the record was written (if committed).
    commit_sha:
        Git commit SHA of the write (if committed).
    now:
        Timestamp override (defaults to UTC now).
    gateway_version:
        Version string of this gateway service.
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
        "accepted_at": now.isoformat().replace("+00:00", "Z"),
    }

    if file_path is not None:
        receipt["file_path"] = file_path
    if commit_sha is not None:
        receipt["commit_sha"] = commit_sha

    # Compute a receipt hash so callers can verify receipt integrity
    receipt["receipt_sha256"] = sha256_canonical_json(
        {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    )

    return receipt
