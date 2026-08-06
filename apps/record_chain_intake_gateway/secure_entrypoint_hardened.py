"""Hardened production entrypoint with deep recovery terminal-status checks.

The base secure entrypoint already verifies immutable intake indexes, receipts,
and stored submissions.  Its recovery route historically parsed terminal
receipt-status sidecars with only receipt/pending-path checks.  This adapter
installs a fail-closed reader that verifies the complete appended/rejected
terminal graph before the recovery route may report ``recovery_verified``.
"""
from __future__ import annotations

import re
from typing import Any

from apps.record_chain_intake_gateway import secure_entrypoint as base
from apps.record_chain_intake_gateway.gateway.canonical import parse_json_strict

_FINAL_STATUS_PREFIX = "record-chain/receipt-status/"
_original_read_text = base._read_text


def _parse_terminal_object(text: str, *, label: str) -> dict[str, Any]:
    try:
        value = parse_json_strict(text)
    except Exception as exc:
        raise base.RecoveryStateInconsistent(
            f"{label} is not strict JSON: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise base.RecoveryStateInconsistent(f"{label} is not a JSON object")
    return value


async def _verify_terminal_status_text(
    path: str,
    text: str,
) -> None:
    """Verify a terminal status and every immutable artifact it references."""
    filename = path.rsplit("/", 1)[-1]
    if not filename.endswith(".json"):
        raise base.RecoveryStateInconsistent("final status path is not canonical")
    receipt_id = filename[:-5]
    if base._RECEIPT_ID_RE.fullmatch(receipt_id) is None:
        raise base.RecoveryStateInconsistent(
            "final status path does not contain a canonical receipt id"
        )

    status = _parse_terminal_object(text, label="final receipt status")
    if status.get("schema") != "trinityaccord.record-chain-receipt-final-status.v1":
        raise base.RecoveryStateInconsistent("final status schema mismatch")
    if status.get("receipt_id") != receipt_id:
        raise base.RecoveryStateInconsistent("final status receipt id mismatch")

    pending_path = status.get("pending_file_path")
    pending_pattern = (
        rf"record-chain/pending/{re.escape(receipt_id)}\."
        r"[a-z_]+\.pending\.json"
    )
    if not isinstance(pending_path, str) or re.fullmatch(
        pending_pattern, pending_path
    ) is None:
        raise base.RecoveryStateInconsistent(
            "final status pending path is invalid or receipt-mismatched"
        )

    append_status = status.get("append_status")
    if append_status == "appended":
        final_id = status.get("final_record_id")
        final_sha = status.get("final_record_sha256")
        if not isinstance(final_id, str) or re.fullmatch(
            r"R-[0-9]{9}", final_id
        ) is None:
            raise base.RecoveryStateInconsistent(
                "final status final_record_id is invalid"
            )
        expected_final_path = f"record-chain/records/{final_id}.json"
        if status.get("final_record_path") != expected_final_path:
            raise base.RecoveryStateInconsistent(
                "final status final_record_path mismatch"
            )
        if not isinstance(final_sha, str) or re.fullmatch(
            r"[a-f0-9]{64}", final_sha
        ) is None:
            raise base.RecoveryStateInconsistent(
                "final status final_record_sha256 is invalid"
            )

        final_text = await _original_read_text(
            expected_final_path,
            label="final record",
        )
        if final_text is None:
            raise base.RecoveryStateInconsistent(
                "final status references an absent final record"
            )
        final_record = _parse_terminal_object(final_text, label="final record")
        if (
            final_record.get("record_id") != final_id
            or final_record.get("record_sha256") != final_sha
        ):
            raise base.RecoveryStateInconsistent(
                "final status final record binding mismatch"
            )
        if base.core_gateway._record_chain_record_sha256(final_record) != final_sha:
            raise base.RecoveryStateInconsistent(
                "final status final record hash recomputation failed"
            )
        if (
            status.get("rejection_path") is not None
            or status.get("rejection_code") is not None
        ):
            raise base.RecoveryStateInconsistent(
                "final status appended/rejection fields conflict"
            )
        return

    if append_status == "rejected":
        pending_name = pending_path.rsplit("/", 1)[-1]
        expected_rejection_path = (
            f"record-chain/rejected/{pending_name[:-5]}.rejection.json"
        )
        rejection_path = status.get("rejection_path")
        if rejection_path != expected_rejection_path:
            raise base.RecoveryStateInconsistent(
                "final status rejection path is invalid or pending-mismatched"
            )
        rejection_text = await _original_read_text(
            rejection_path,
            label="rejection metadata",
        )
        if rejection_text is None:
            raise base.RecoveryStateInconsistent(
                "final status references absent rejection metadata"
            )
        rejection = _parse_terminal_object(
            rejection_text,
            label="rejection metadata",
        )
        if rejection.get("source_pending") != pending_name:
            raise base.RecoveryStateInconsistent(
                "final status rejection source binding mismatch"
            )
        if any(
            status.get(field) is not None
            for field in (
                "final_record_id",
                "final_record_path",
                "final_record_sha256",
            )
        ):
            raise base.RecoveryStateInconsistent(
                "final status rejected/final fields conflict"
            )
        return

    raise base.RecoveryStateInconsistent("final status append_status is invalid")


async def _deeply_verified_read_text(path: str, *, label: str) -> str | None:
    """Read normally, but fully verify terminal status sidecars before use."""
    text = await _original_read_text(path, label=label)
    if text is None or not path.startswith(_FINAL_STATUS_PREFIX):
        return text
    await _verify_terminal_status_text(path, text)
    return text


# ProtectedProductionApp resolves this module global at request time, so the
# already-created base application immediately receives the stronger check.
base._read_text = _deeply_verified_read_text
app = base.app
