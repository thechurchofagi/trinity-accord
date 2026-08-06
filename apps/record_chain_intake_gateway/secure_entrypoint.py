"""Production entrypoint for the protected Record-Chain Gateway.

This module installs the secret-keyed durable intake cooldown, preserves the
Gateway-owned authorship verification projection, and exposes hardened
read-only receipt/recovery routes. Read-only routes are rate limited, bounded,
cache-aware, and fail closed without misreporting transient repository outages
as immutable-state corruption.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import re
import time
import threading
from collections import deque
from dataclasses import dataclass
from typing import Any

from apps.record_chain_intake_gateway import app as core_gateway
from apps.record_chain_intake_gateway.gateway import runtime
from apps.record_chain_intake_gateway.gateway.canonical import (
    parse_json_strict,
    sha256_canonical_json,
)
from apps.record_chain_intake_gateway.gateway.github_adapter import get_file_text
from apps.record_chain_intake_gateway.gateway.receipts import verify_receipt_sha256


# The core Gateway verifies Ed25519 authorship before it reaches the pending
# projection call. Preserve that server-owned fact in every future pending/final
# record without changing the participant's signed payload domain.
_original_strip_unsigned_projection_fields = core_gateway.strip_unsigned_projection_fields


def _gateway_verified_pending_projection(record_draft: dict[str, Any]) -> dict[str, Any]:
    cleaned = _original_strip_unsigned_projection_fields(record_draft)
    cleaned["authorship_verification_status"] = {
        "signed_payload_scope": "pre_append_record_draft",
        "verified_by_gateway_before_pending": True,
        "verified_by_append_before_record": False,
        "final_record_contains_append_assigned_fields_not_in_signed_payload": True,
    }
    return cleaned


core_gateway.strip_unsigned_projection_fields = _gateway_verified_pending_projection

# Import protection only after the production pending-projection hook is bound.
from apps.record_chain_intake_gateway import protected_app as protection  # noqa: E402


_MAX_BLOCKED_CLIENT_KEYS = 10_000
_BLOCKED_CLIENT_TARGET = 8_000
_PROTECTED_HEALTH_PATHS = frozenset({"/healthz", "/readyz"})
_SUBMISSION_RECOVERY_RE = re.compile(
    r"^/record-chain/recovery/submission/(?P<submission_sha256>[0-9a-f]{64})$"
)
_RECEIPT_ROUTE_RE = re.compile(
    r"^/record-chain/receipt/(?P<receipt_id>"
    r"rcg-[0-9]{8}-[0-9a-f]{12}(?:[0-9a-f]{12})?)$"
)
_RECEIPT_ID_RE = re.compile(
    r"^rcg-(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})-"
    r"(?P<digest>[0-9a-f]{12}(?:[0-9a-f]{12})?)$"
)

_READ_GLOBAL_LIMIT_PER_MINUTE = max(
    1, int(os.environ.get("TRINITY_READ_ROUTE_GLOBAL_LIMIT_PER_MINUTE", "600"))
)
_READ_CLIENT_LIMIT_PER_MINUTE = max(
    1, int(os.environ.get("TRINITY_READ_ROUTE_CLIENT_LIMIT_PER_MINUTE", "120"))
)
_READ_WINDOW_SECONDS = 60.0
_READ_MAX_TRACKED_CLIENTS = max(
    100, int(os.environ.get("TRINITY_READ_ROUTE_MAX_TRACKED_CLIENTS", "20000"))
)
_RECOVERY_MAX_CONCURRENCY = max(
    1, int(os.environ.get("TRINITY_RECOVERY_MAX_CONCURRENCY", "8"))
)
_RECOVERY_CACHE_MAX_ENTRIES = max(
    16, int(os.environ.get("TRINITY_RECOVERY_CACHE_MAX_ENTRIES", "2048"))
)
_RECOVERY_POSITIVE_TTL_SECONDS = max(
    0.0, float(os.environ.get("TRINITY_RECOVERY_POSITIVE_TTL_SECONDS", "30"))
)
_RECOVERY_NEGATIVE_TTL_SECONDS = max(
    0.0, float(os.environ.get("TRINITY_RECOVERY_NEGATIVE_TTL_SECONDS", "1"))
)

_read_state_lock = threading.Lock()
_recovery_active = 0
_read_global_attempts: deque[float] = deque()
_read_attempts_by_client: dict[str, deque[float]] = {}
_recovery_cache: dict[str, tuple[float, int, dict[str, Any]]] = {}


class RecoveryBackendUnavailable(RuntimeError):
    """The durable repository could not be read reliably."""


class RecoveryStateInconsistent(RuntimeError):
    """Durable artifacts were readable but failed immutable binding checks."""


@dataclass(frozen=True)
class VerifiedIntakeArtifacts:
    index: dict[str, Any]
    receipt: dict[str, Any]
    receipt_id: str
    receipt_path: str
    intake_submission_path: str
    pending_file_path: str
    record_type: str
    stored_submission_sha256: str


def _server_cooldown_secret() -> bytes:
    secret = (
        os.environ.get("TRINITY_COOLDOWN_SECRET", "").strip()
        or os.environ.get("TRINITY_GITHUB_TOKEN", "").strip()
    )
    if not secret:
        raise RuntimeError(
            "TRINITY_COOLDOWN_SECRET or TRINITY_GITHUB_TOKEN is required for "
            "unpredictable durable intake cooldowns"
        )
    return secret.encode("utf-8")


def keyed_cooldown_seconds(commit_sha: str, *, secret: bytes | None = None) -> int:
    """Return a secret-keyed interval in the inclusive 3600..7200 range."""
    key = secret if secret is not None else _server_cooldown_secret()
    digest = hmac.new(
        key,
        commit_sha.encode("ascii", errors="ignore"),
        hashlib.sha256,
    ).digest()
    offset = int.from_bytes(digest[:4], "big") % (
        protection._COOLDOWN_SPAN_SECONDS + 1
    )
    return protection._COOLDOWN_MIN_SECONDS + offset


# Patch the module global resolved by IntakeProtectionMiddleware._cooldown_state.
protection.cooldown_seconds_for_commit = keyed_cooldown_seconds

# Reduce GitHub API pressure during blocked-request floods. The final gate still
# forces an uncached read immediately before any durable write.
protection._COOLDOWN_CACHE_SECONDS = 30.0

# Bound the process-local blocked-client guidance map.
_original_blocked_attempt_count = protection.IntakeProtectionMiddleware._blocked_attempt_count


def _bounded_blocked_attempt_count(self, client_key: str) -> int:
    count = _original_blocked_attempt_count(self, client_key)
    entries_by_client = self._blocked_attempts
    if len(entries_by_client) <= _MAX_BLOCKED_CLIENT_KEYS:
        return count

    now = time.monotonic()
    cutoff = now - protection._BLOCKED_ATTEMPT_WINDOW_SECONDS
    last_seen: list[tuple[float, str]] = []
    for key, entries in list(entries_by_client.items()):
        while entries and entries[0] < cutoff:
            entries.popleft()
        if not entries:
            entries_by_client.pop(key, None)
        else:
            last_seen.append((entries[-1], key))

    excess = len(entries_by_client) - _BLOCKED_CLIENT_TARGET
    if excess > 0:
        removed = 0
        for _, key in sorted(last_seen):
            if key == client_key:
                continue
            entries_by_client.pop(key, None)
            removed += 1
            if removed >= excess:
                break
    return count


protection.IntakeProtectionMiddleware._blocked_attempt_count = _bounded_blocked_attempt_count

# Do not interpret an empty path-filter result as a genuinely empty deployment.
_original_latest_intake_commit = protection.IntakeProtectionMiddleware._latest_intake_commit


async def _latest_intake_commit_fail_closed(self, *, force: bool):
    latest = await _original_latest_intake_commit(self, force=force)
    allow_empty = os.environ.get("TRINITY_ALLOW_EMPTY_INTAKE_HISTORY", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if latest is None and not allow_empty:
        raise RuntimeError(
            "durable intake history was not found; refusing to fail open. "
            "Set TRINITY_ALLOW_EMPTY_INTAKE_HISTORY=true only for a verified new empty deployment"
        )
    return latest


protection.IntakeProtectionMiddleware._latest_intake_commit = _latest_intake_commit_fail_closed

# This marker is process-local and is set only by this secure module.
runtime.mark_protection_layer_active(runtime.BASE_PROTECTION_ENTRYPOINT)


def _parse_object(text: str, *, label: str) -> dict[str, Any]:
    parsed = parse_json_strict(text)
    if not isinstance(parsed, dict):
        raise RecoveryStateInconsistent(f"{label} is not a JSON object")
    return parsed


async def _read_text(path: str, *, label: str) -> str | None:
    try:
        return await get_file_text(path)
    except Exception as exc:
        raise RecoveryBackendUnavailable(f"{label} could not be read") from exc


def _canonical_receipt_paths(receipt_id: str, record_type: str) -> tuple[str, str, str]:
    match = _RECEIPT_ID_RE.fullmatch(receipt_id)
    if match is None:
        raise RecoveryStateInconsistent("invalid receipt_id")
    year = match.group("year")
    month = match.group("month")
    receipt_path = (
        f"record-chain/intake/receipts/{year}/{month}/{receipt_id}.receipt.json"
    )
    submission_path = (
        f"record-chain/intake/submissions/{year}/{month}/{receipt_id}.submission.json"
    )
    pending_path = f"record-chain/pending/{receipt_id}.{record_type}.pending.json"
    return receipt_path, submission_path, pending_path


async def _verify_intake_artifacts(
    *,
    index: dict[str, Any],
    submission_sha256: str,
    expected_record_type: str | None = None,
) -> VerifiedIntakeArtifacts:
    if index.get("schema") != "trinityaccord.record-chain-intake-idempotency.v1":
        raise RecoveryStateInconsistent("unexpected idempotency schema")
    if index.get("submission_sha256") != submission_sha256:
        raise RecoveryStateInconsistent("idempotency submission hash mismatch")
    materialization_complete = (
        index.get("idempotency_written") is True
        and index.get("receipt_written") is True
        and index.get("pending_written") is True
        and index.get("transaction_state") == "pending_written"
    )
    if not materialization_complete:
        raise RecoveryStateInconsistent(
            "intake transaction is not fully materialized"
        )

    receipt_id = index.get("receipt_id")
    record_type = index.get("record_type")
    if not isinstance(receipt_id, str):
        raise RecoveryStateInconsistent("missing receipt_id")
    if not isinstance(record_type, str) or not re.fullmatch(r"[a-z_]+", record_type):
        raise RecoveryStateInconsistent("invalid record_type")
    if expected_record_type and record_type != expected_record_type:
        raise RecoveryStateInconsistent("record type does not match the submitted route")

    expected_receipt_path, expected_submission_path, expected_pending_path = (
        _canonical_receipt_paths(receipt_id, record_type)
    )
    receipt_path = index.get("receipt_path")
    intake_submission_path = index.get("intake_submission_path")
    pending_file_path = index.get("pending_file_path")
    if receipt_path != expected_receipt_path:
        raise RecoveryStateInconsistent("receipt path is not canonically bound to receipt_id")
    if intake_submission_path != expected_submission_path:
        raise RecoveryStateInconsistent("submission path is not canonically bound to receipt_id")
    if pending_file_path != expected_pending_path:
        raise RecoveryStateInconsistent(
            "pending path is not canonically bound to receipt_id and record_type"
        )

    receipt_text = await _read_text(receipt_path, label="receipt")
    if receipt_text is None:
        raise RecoveryStateInconsistent("receipt path is absent")
    receipt = _parse_object(receipt_text, label="receipt")
    receipt_ok, receipt_error = verify_receipt_sha256(receipt)
    if not receipt_ok:
        raise RecoveryStateInconsistent(receipt_error)

    expected_receipt_bindings = {
        "server_receipt_id": receipt_id,
        "receipt_path": receipt_path,
        "intake_submission_path": intake_submission_path,
        "pending_file_path": pending_file_path,
        "submission_sha256": submission_sha256,
        "record_type": record_type,
    }
    for field, expected in expected_receipt_bindings.items():
        actual = receipt.get(field)
        if actual != expected:
            raise RecoveryStateInconsistent(
                f"receipt binding mismatch for {field}: expected {expected!r}, got {actual!r}"
            )
    original_submission_sha256 = receipt.get("original_submission_sha256")
    if original_submission_sha256 not in (None, "", submission_sha256):
        raise RecoveryStateInconsistent(
            "receipt original_submission_sha256 does not bind the requested submission"
        )

    stored_submission_sha256 = index.get("stored_submission_sha256")
    if (
        not isinstance(stored_submission_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", stored_submission_sha256)
    ):
        raise RecoveryStateInconsistent("invalid stored_submission_sha256 in index")
    if receipt.get("stored_submission_sha256") != stored_submission_sha256:
        raise RecoveryStateInconsistent("stored submission hash mismatch between index and receipt")

    submission_text = await _read_text(
        intake_submission_path,
        label="stored submission",
    )
    if submission_text is None:
        raise RecoveryStateInconsistent("stored submission path is absent")
    stored_submission = _parse_object(submission_text, label="stored submission")
    actual_stored_sha256 = sha256_canonical_json(stored_submission)
    if actual_stored_sha256 != stored_submission_sha256:
        raise RecoveryStateInconsistent(
            "stored submission bytes do not match stored_submission_sha256"
        )

    return VerifiedIntakeArtifacts(
        index=index,
        receipt=receipt,
        receipt_id=receipt_id,
        receipt_path=receipt_path,
        intake_submission_path=intake_submission_path,
        pending_file_path=pending_file_path,
        record_type=record_type,
        stored_submission_sha256=stored_submission_sha256,
    )


# Harden the duplicate-submit path as well as the dedicated recovery route.
_original_submit_response_from_idempotency_index = (
    core_gateway._submit_response_from_idempotency_index
)


async def _verified_submit_response_from_idempotency_index(
    *,
    index: dict[str, Any],
    record_type: str,
    submission_sha256: str,
    received_raw_body_sha256: str,
    body: dict[str, Any],
):
    await _verify_intake_artifacts(
        index=index,
        submission_sha256=submission_sha256,
        expected_record_type=record_type,
    )
    return await _original_submit_response_from_idempotency_index(
        index=index,
        record_type=record_type,
        submission_sha256=submission_sha256,
        received_raw_body_sha256=received_raw_body_sha256,
        body=body,
    )


core_gateway._submit_response_from_idempotency_index = (
    _verified_submit_response_from_idempotency_index
)


def _boundary() -> dict[str, bool]:
    return {
        "read_only_recovery": True,
        "does_not_create_submission": True,
        "does_not_retry_submission": True,
        "does_not_bypass_cooldown": True,
    }


def _recovery_error(
    *,
    status: int,
    code: str,
    message: str,
    submission_sha256: str,
) -> tuple[int, dict[str, Any]]:
    return status, {
        "found": False,
        "recovery_verified": False,
        "receipt_hash_verified": False,
        "submission_sha256": submission_sha256,
        "diagnostic_code": code,
        "message": message,
        "boundary": _boundary(),
    }


def _receipt_error(
    *,
    status: int,
    code: str,
    message: str,
    receipt_id: str,
) -> tuple[int, dict[str, Any]]:
    diagnostic = {
        "code": code,
        "severity": "error",
        "message": message,
    }
    return status, {
        "found": False,
        "receipt_hash_verified": False,
        "receipt_id": receipt_id,
        "diagnostic_code": code,
        "message": message,
        "diagnostics": [diagnostic],
        "boundary": {
            "read_only_receipt_lookup": True,
            "does_not_create_submission": True,
            "does_not_retry_submission": True,
            "does_not_bypass_cooldown": True,
        },
    }


def _request_headers(scope: dict[str, Any]) -> dict[str, str]:
    return protection.IntakeProtectionMiddleware._headers(scope)


def _client_key(scope: dict[str, Any], headers: dict[str, str]) -> str:
    return protection.IntakeProtectionMiddleware._client_key(scope, headers)


def _prune_read_state(now: float) -> None:
    cutoff = now - _READ_WINDOW_SECONDS
    while _read_global_attempts and _read_global_attempts[0] < cutoff:
        _read_global_attempts.popleft()
    for key, attempts in list(_read_attempts_by_client.items()):
        while attempts and attempts[0] < cutoff:
            attempts.popleft()
        if not attempts:
            _read_attempts_by_client.pop(key, None)


def _allow_read_route(client_key: str) -> tuple[bool, int]:
    now = time.monotonic()
    with _read_state_lock:
        _prune_read_state(now)
        attempts = _read_attempts_by_client.get(client_key)
        if attempts is None:
            if len(_read_attempts_by_client) >= _READ_MAX_TRACKED_CLIENTS:
                oldest_key = min(
                    _read_attempts_by_client,
                    key=lambda key: (
                        _read_attempts_by_client[key][-1]
                        if _read_attempts_by_client[key]
                        else float("-inf")
                    ),
                )
                _read_attempts_by_client.pop(oldest_key, None)
            attempts = deque()
            _read_attempts_by_client[client_key] = attempts

        if len(_read_global_attempts) >= _READ_GLOBAL_LIMIT_PER_MINUTE:
            retry_after = max(
                int(_read_global_attempts[0] + _READ_WINDOW_SECONDS - now),
                1,
            )
            return False, retry_after
        if len(attempts) >= _READ_CLIENT_LIMIT_PER_MINUTE:
            retry_after = max(int(attempts[0] + _READ_WINDOW_SECONDS - now), 1)
            return False, retry_after

        _read_global_attempts.append(now)
        attempts.append(now)
        return True, 0


def _cache_get(submission_sha256: str) -> tuple[int, dict[str, Any]] | None:
    with _read_state_lock:
        item = _recovery_cache.get(submission_sha256)
        if item is None:
            return None
        expires_at, status, payload = item
        if time.monotonic() >= expires_at:
            _recovery_cache.pop(submission_sha256, None)
            return None
        return status, payload


def _cache_put(
    submission_sha256: str,
    *,
    status: int,
    payload: dict[str, Any],
) -> None:
    ttl = (
        _RECOVERY_POSITIVE_TTL_SECONDS
        if status == 200
        else _RECOVERY_NEGATIVE_TTL_SECONDS
    )
    if ttl <= 0 or status not in {200, 404}:
        return
    with _read_state_lock:
        _recovery_cache.pop(submission_sha256, None)
        _recovery_cache[submission_sha256] = (
            time.monotonic() + ttl,
            status,
            payload,
        )
        while len(_recovery_cache) > _RECOVERY_CACHE_MAX_ENTRIES:
            oldest_key = next(iter(_recovery_cache))
            _recovery_cache.pop(oldest_key, None)


def _try_acquire_recovery_slot() -> bool:
    global _recovery_active
    with _read_state_lock:
        if _recovery_active >= _RECOVERY_MAX_CONCURRENCY:
            return False
        _recovery_active += 1
        return True


def _release_recovery_slot() -> None:
    global _recovery_active
    with _read_state_lock:
        _recovery_active = max(_recovery_active - 1, 0)


class ProtectedProductionApp:
    """ASGI wrapper exposing fail-closed production and read-only routes."""

    def __init__(self, app: Any) -> None:
        self.app = app

    @staticmethod
    def _readiness_payload() -> tuple[int, dict[str, Any]]:
        info = runtime.get_runtime_info()
        repo_configured = bool(os.environ.get("TRINITY_REPO_FULL_NAME", "").strip())
        branch_configured = bool(os.environ.get("TRINITY_TARGET_BRANCH", "").strip())
        token_configured = bool(os.environ.get("TRINITY_GITHUB_TOKEN", "").strip())
        cooldown_secret_configured = bool(
            os.environ.get("TRINITY_COOLDOWN_SECRET", "").strip()
            or os.environ.get("TRINITY_GITHUB_TOKEN", "").strip()
        )
        write_requires_github = info["write_mode"] == "github_contents_pending"
        ready = bool(
            info["protection_layer_active"]
            and repo_configured
            and branch_configured
            and cooldown_secret_configured
            and (token_configured if write_requires_github else True)
        )
        return (
            200 if ready else 503,
            {
                "ok": ready,
                "service": info["service"],
                "version": info["version"],
                "write_mode": info["write_mode"],
                "protection_required": True,
                "protection_layer_active": info["protection_layer_active"],
                "protection_entrypoint": info["protection_entrypoint"],
                "repo_configured": repo_configured,
                "branch_configured": branch_configured,
                "token_configured": token_configured,
                "cooldown_secret_configured": cooldown_secret_configured,
                "read_route_limits": {
                    "global_per_minute": _READ_GLOBAL_LIMIT_PER_MINUTE,
                    "client_per_minute": _READ_CLIENT_LIMIT_PER_MINUTE,
                    "recovery_max_concurrency": _RECOVERY_MAX_CONCURRENCY,
                    "recovery_cache_max_entries": _RECOVERY_CACHE_MAX_ENTRIES,
                },
            },
        )

    @staticmethod
    async def _submission_recovery_payload(
        submission_sha256: str,
    ) -> tuple[int, dict[str, Any]]:
        cached = _cache_get(submission_sha256)
        if cached is not None:
            return cached

        index_path = (
            "record-chain/intake/by-submission-sha256/"
            f"{submission_sha256}.json"
        )
        if not _try_acquire_recovery_slot():
            return _recovery_error(
                status=503,
                code="RECOVERY_CAPACITY_EXHAUSTED",
                message=(
                    "Read-only recovery capacity is temporarily exhausted; "
                    "retry later without resubmitting."
                ),
                submission_sha256=submission_sha256,
            )
        try:
            cached = _cache_get(submission_sha256)
            if cached is not None:
                return cached
            index_text = await _read_text(index_path, label="immutable intake index")
            if index_text is None:
                result = _recovery_error(
                    status=404,
                    code="SUBMISSION_NOT_MATERIALIZED",
                    message=(
                        "No immutable intake transaction exists for this "
                        "submission SHA-256."
                    ),
                    submission_sha256=submission_sha256,
                )
                _cache_put(
                    submission_sha256,
                    status=result[0],
                    payload=result[1],
                )
                return result

            try:
                index = _parse_object(index_text, label="idempotency index")
                artifacts = await _verify_intake_artifacts(
                    index=index,
                    submission_sha256=submission_sha256,
                )
                final_status_path = (
                    f"record-chain/receipt-status/{artifacts.receipt_id}.json"
                )
                final_status_text = await _read_text(
                    final_status_path,
                    label="final receipt status",
                )
                final_status: dict[str, Any] | None = None
                if final_status_text is not None:
                    try:
                        final_status = await core_gateway._read_receipt_final_status(
                            artifacts.receipt_id
                        )
                    except RuntimeError as exc:
                        raise RecoveryStateInconsistent(
                            f"final receipt status failed verification: {exc}"
                        ) from exc
                    except Exception as exc:
                        raise RecoveryBackendUnavailable(
                            "final receipt status could not be verified"
                        ) from exc
                    if final_status is None:
                        raise RecoveryStateInconsistent(
                            "final receipt status disappeared during verification"
                        )
                    if final_status.get("pending_file_path") != artifacts.pending_file_path:
                        raise RecoveryStateInconsistent(
                            "final status pending path mismatch"
                        )

                result = (
                    200,
                    {
                        "found": True,
                        "recovery_verified": True,
                        "receipt_hash_verified": True,
                        "stored_submission_hash_verified": True,
                        "idempotency_index_binding_verified": True,
                        "submission_sha256": submission_sha256,
                        "receipt_id": artifacts.receipt_id,
                        "record_type": artifacts.record_type,
                        "receipt": artifacts.receipt,
                        "final_status": final_status,
                        "boundary": _boundary(),
                    },
                )
                _cache_put(
                    submission_sha256,
                    status=result[0],
                    payload=result[1],
                )
                return result
            except RecoveryBackendUnavailable:
                raise
            except RecoveryStateInconsistent as exc:
                return _recovery_error(
                    status=409,
                    code="RECOVERY_STATE_INCONSISTENT",
                    message=(
                        "An intake index exists, but its immutable submission, "
                        "receipt, or path bindings could not be verified: "
                        f"{exc}"
                    ),
                    submission_sha256=submission_sha256,
                )
        finally:
            _release_recovery_slot()

    @staticmethod
    async def _receipt_payload(receipt_id: str) -> tuple[int, dict[str, Any]]:
        match = _RECEIPT_ID_RE.fullmatch(receipt_id)
        if match is None:
            return _receipt_error(
                status=400,
                code="INVALID_RECEIPT_ID",
                message="Receipt ID format is invalid.",
                receipt_id=receipt_id,
            )
        receipt_path = (
            "record-chain/intake/receipts/"
            f"{match.group('year')}/{match.group('month')}/"
            f"{receipt_id}.receipt.json"
        )
        durable = False
        backend_error: RecoveryBackendUnavailable | None = None
        receipt: dict[str, Any] | None = None
        try:
            receipt_text = await _read_text(receipt_path, label="receipt")
            if receipt_text is not None:
                receipt = _parse_object(receipt_text, label="receipt")
                durable = True
        except RecoveryBackendUnavailable as exc:
            backend_error = exc

        if receipt is None:
            cached = core_gateway._receipt_store.get(receipt_id)
            if cached is None:
                if backend_error is not None:
                    return _receipt_error(
                        status=503,
                        code="RECEIPT_BACKEND_UNAVAILABLE",
                        message=str(backend_error),
                        receipt_id=receipt_id,
                    )
                return _receipt_error(
                    status=404,
                    code="RECEIPT_NOT_FOUND",
                    message="No durable or process-local receipt exists.",
                    receipt_id=receipt_id,
                )
            receipt = cached

        try:
            ok, error = verify_receipt_sha256(receipt)
            if not ok:
                raise RecoveryStateInconsistent(error)
            if receipt.get("server_receipt_id") != receipt_id:
                raise RecoveryStateInconsistent(
                    "receipt server_receipt_id does not match the requested URL"
                )
            if receipt.get("receipt_path") != receipt_path:
                raise RecoveryStateInconsistent(
                    "receipt_path does not match the canonical requested URL"
                )

            record_type = receipt.get("record_type")
            if not isinstance(record_type, str):
                raise RecoveryStateInconsistent("receipt record_type is invalid")
            expected_receipt, expected_submission, expected_pending = (
                _canonical_receipt_paths(receipt_id, record_type)
            )
            if expected_receipt != receipt_path:
                raise RecoveryStateInconsistent("receipt canonical path mismatch")
            if receipt.get("intake_submission_path") != expected_submission:
                raise RecoveryStateInconsistent(
                    "receipt intake_submission_path is not canonical"
                )
            if receipt.get("pending_file_path") != expected_pending:
                raise RecoveryStateInconsistent(
                    "receipt pending_file_path is not canonical"
                )

            stored_hash = receipt.get("stored_submission_sha256")
            if (
                not isinstance(stored_hash, str)
                or not re.fullmatch(r"[0-9a-f]{64}", stored_hash)
            ):
                raise RecoveryStateInconsistent(
                    "receipt stored_submission_sha256 is invalid"
                )

            if durable:
                stored_text = await _read_text(
                    expected_submission,
                    label="stored submission",
                )
                if stored_text is None:
                    raise RecoveryStateInconsistent(
                        "receipt-bound stored submission is absent"
                    )
                stored_submission = _parse_object(
                    stored_text,
                    label="stored submission",
                )
                if sha256_canonical_json(stored_submission) != stored_hash:
                    raise RecoveryStateInconsistent(
                        "receipt-bound stored submission hash is invalid"
                    )

            core_gateway._cache_receipt(
                receipt_id,
                receipt,
                ephemeral=(
                    not durable
                    and receipt_id in core_gateway._ephemeral_receipt_ids
                ),
            )
            envelope = await core_gateway._build_receipt_envelope(
                receipt,
                receipt_id,
                receipt_path,
                receipt_url_binding_verified=True,
                stored_submission_hash_verified=durable,
                envelope_warnings=(
                    [{
                        "code": "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE",
                        "message": (
                            "Durable receipt storage could not be read; a "
                            "hash-verified, URL-bound in-memory cache entry was returned."
                        ),
                        "receipt_path": receipt_path,
                        "retryable": True,
                    }]
                    if backend_error is not None
                    else None
                ),
            )
            return 200, envelope
        except RecoveryBackendUnavailable as exc:
            return _receipt_error(
                status=503,
                code="RECEIPT_BACKEND_UNAVAILABLE",
                message=str(exc),
                receipt_id=receipt_id,
            )
        except RecoveryStateInconsistent as exc:
            return _receipt_error(
                status=409,
                code="RECEIPT_STATE_INCONSISTENT",
                message=str(exc),
                receipt_id=receipt_id,
            )

    @staticmethod
    async def _send_json(
        send,
        *,
        status: int,
        payload: dict[str, Any],
        head: bool,
        retry_after: int | None = None,
    ) -> None:
        raw = json.dumps(
            payload,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        headers = [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(raw)).encode("ascii")),
            (b"cache-control", b"no-store"),
        ]
        if retry_after is not None:
            headers.append((b"retry-after", str(retry_after).encode("ascii")))
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": headers,
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"" if head else raw,
                "more_body": False,
            }
        )

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") == "http":
            path = str(scope.get("path") or "")
            method = str(scope.get("method") or "").upper()
            if path in _PROTECTED_HEALTH_PATHS and method in {"GET", "HEAD"}:
                status, payload = self._readiness_payload()
                await self._send_json(
                    send,
                    status=status,
                    payload=payload,
                    head=method == "HEAD",
                )
                return

            recovery_match = _SUBMISSION_RECOVERY_RE.fullmatch(path)
            receipt_match = _RECEIPT_ROUTE_RE.fullmatch(path)
            if (
                method in {"GET", "HEAD"}
                and (recovery_match is not None or receipt_match is not None)
            ):
                headers = _request_headers(scope)
                allowed, retry_after = _allow_read_route(
                    _client_key(scope, headers)
                )
                if not allowed:
                    payload = {
                        "found": False,
                        "diagnostic_code": "READ_ROUTE_RATE_LIMIT_EXCEEDED",
                        "message": (
                            "Public read verification is temporarily rate "
                            "limited to protect repository-backed availability."
                        ),
                        "retry_after_seconds": retry_after,
                        "boundary": {
                            "read_only": True,
                            "does_not_create_submission": True,
                            "does_not_bypass_cooldown": True,
                        },
                    }
                    await self._send_json(
                        send,
                        status=429,
                        payload=payload,
                        head=method == "HEAD",
                        retry_after=retry_after,
                    )
                    return

                if recovery_match is not None:
                    try:
                        status, payload = await self._submission_recovery_payload(
                            recovery_match.group("submission_sha256")
                        )
                    except RecoveryBackendUnavailable as exc:
                        status, payload = _recovery_error(
                            status=503,
                            code="RECOVERY_STATE_UNAVAILABLE",
                            message=str(exc),
                            submission_sha256=recovery_match.group(
                                "submission_sha256"
                            ),
                        )
                else:
                    status, payload = await self._receipt_payload(
                        receipt_match.group("receipt_id")
                    )
                await self._send_json(
                    send,
                    status=status,
                    payload=payload,
                    head=method == "HEAD",
                )
                return

        await self.app(scope, receive, send)


app = ProtectedProductionApp(protection.app)
