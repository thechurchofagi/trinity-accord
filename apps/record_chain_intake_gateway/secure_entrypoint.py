"""Production entrypoint for the protected Record-Chain Gateway.

The public repository must not make the exact reopening time computable from a
public commit SHA. This entrypoint replaces the unkeyed test/reference interval
function with HMAC-SHA256 keyed by a server-only secret before exposing the ASGI
application.

A dedicated ``TRINITY_COOLDOWN_SECRET`` is preferred. The already-required
``TRINITY_GITHUB_TOKEN`` is a fail-safe fallback so an existing production
service fails closed rather than silently losing the cooldown during rollout.

Both ``/healthz`` and ``/readyz`` are intercepted by this production wrapper and
run the same strict configuration/protection check. Render currently probes
``/healthz``; ``/readyz`` remains the explicit machine-facing protected
readiness route. The deployment helper separately reads back the secure Uvicorn
start command, so an unprotected core-app command cannot be accepted as a valid
production deployment.

The wrapper also exposes a read-only ambiguity-recovery endpoint keyed by the
canonical submission SHA-256. It verifies the immutable idempotency index and
receipt hash before returning an existing receipt. It never submits, retries,
or bypasses the durable intake cooldown.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
from typing import Any

from apps.record_chain_intake_gateway import app as core_gateway
from apps.record_chain_intake_gateway.gateway import runtime
from apps.record_chain_intake_gateway.gateway.canonical import parse_json_strict
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
_RECEIPT_ID_RE = re.compile(
    r"^rcg-(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2})-"
    r"(?P<digest>[0-9a-f]{12}(?:[0-9a-f]{12})?)$"
)


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
# The production app therefore never uses the public unkeyed reference helper.
protection.cooldown_seconds_for_commit = keyed_cooldown_seconds

# Reduce GitHub API pressure during a blocked-request flood. The final gate still
# forces an uncached read immediately before any durable write.
protection._COOLDOWN_CACHE_SECONDS = 30.0

# Bound the process-local client guidance map. The durable acceptance state is
# still the immutable intake commit; this map is only for progressively clearer
# rejection guidance and must never become an unbounded high-cardinality store.
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

# A successful GitHub API response that contains no materialization commit must
# not be interpreted as "no cooldown" in an established deployment. This closes
# the rare path-filter/history-window fail-open case. A genuinely new empty
# deployment can opt in explicitly after an operator verifies that history is
# actually empty.
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

# This marker is process-local and is set only by this module. Readiness can
# therefore distinguish a genuinely wrapped runtime from a Render service that
# merely deployed the correct source commit with a stale core-app start command.
runtime.mark_protection_layer_active()


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
        "boundary": {
            "read_only_recovery": True,
            "does_not_create_submission": True,
            "does_not_retry_submission": True,
            "does_not_bypass_cooldown": True,
        },
    }


def _parse_object(text: str, *, label: str) -> dict[str, Any]:
    parsed = parse_json_strict(text)
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} is not a JSON object")
    return parsed


class ProtectedProductionApp:
    """ASGI wrapper exposing fail-closed production and recovery routes."""

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
            },
        )

    @staticmethod
    async def _submission_recovery_payload(
        submission_sha256: str,
    ) -> tuple[int, dict[str, Any]]:
        index_path = (
            "record-chain/intake/by-submission-sha256/"
            f"{submission_sha256}.json"
        )
        try:
            index_text = await get_file_text(index_path)
        except Exception:
            return _recovery_error(
                status=503,
                code="RECOVERY_STATE_UNAVAILABLE",
                message="The immutable intake index could not be read.",
                submission_sha256=submission_sha256,
            )
        if index_text is None:
            return _recovery_error(
                status=404,
                code="SUBMISSION_NOT_MATERIALIZED",
                message="No immutable intake transaction exists for this submission SHA-256.",
                submission_sha256=submission_sha256,
            )

        try:
            index = _parse_object(index_text, label="idempotency index")
            if index.get("schema") != "trinityaccord.record-chain-intake-idempotency.v1":
                raise ValueError("unexpected idempotency schema")
            if index.get("submission_sha256") != submission_sha256:
                raise ValueError("idempotency submission hash mismatch")
            if index.get("idempotency_written") is not True:
                raise ValueError("idempotency index is not committed")
            if index.get("receipt_written") is not True:
                raise ValueError("receipt is not marked written")

            receipt_id = index.get("receipt_id")
            if not isinstance(receipt_id, str):
                raise ValueError("missing receipt_id")
            receipt_match = _RECEIPT_ID_RE.fullmatch(receipt_id)
            if receipt_match is None:
                raise ValueError("invalid receipt_id")

            expected_receipt_path = (
                "record-chain/intake/receipts/"
                f"{receipt_match.group('year')}/{receipt_match.group('month')}/"
                f"{receipt_id}.receipt.json"
            )
            receipt_path = index.get("receipt_path")
            if receipt_path != expected_receipt_path:
                raise ValueError("receipt path is not canonically bound to receipt_id")

            receipt_text = await get_file_text(receipt_path)
            if receipt_text is None:
                raise ValueError("receipt path is absent")
            receipt = _parse_object(receipt_text, label="receipt")
            receipt_ok, receipt_error = verify_receipt_sha256(receipt)
            if not receipt_ok:
                raise ValueError(receipt_error)
            if receipt.get("server_receipt_id") != receipt_id:
                raise ValueError("receipt id mismatch")
            if receipt.get("receipt_path") != receipt_path:
                raise ValueError("receipt path mismatch")
            if receipt.get("submission_sha256") != submission_sha256:
                raise ValueError("receipt submission hash mismatch")
            if receipt.get("stored_submission_sha256") != index.get("stored_submission_sha256"):
                raise ValueError("stored submission hash mismatch")
            if receipt.get("record_type") != index.get("record_type"):
                raise ValueError("record type mismatch")

            final_status_path = f"record-chain/receipt-status/{receipt_id}.json"
            final_status_text = await get_file_text(final_status_path)
            final_status: dict[str, Any] | None = None
            if final_status_text is not None:
                final_status = _parse_object(final_status_text, label="final status")
                if final_status.get("receipt_id") != receipt_id:
                    raise ValueError("final status receipt id mismatch")
                if (
                    final_status.get("pending_file_path")
                    and final_status.get("pending_file_path") != index.get("pending_file_path")
                ):
                    raise ValueError("final status pending path mismatch")

            return 200, {
                "found": True,
                "recovery_verified": True,
                "receipt_hash_verified": True,
                "submission_sha256": submission_sha256,
                "receipt_id": receipt_id,
                "record_type": receipt.get("record_type"),
                "receipt": receipt,
                "final_status": final_status,
                "boundary": {
                    "read_only_recovery": True,
                    "does_not_create_submission": True,
                    "does_not_retry_submission": True,
                    "does_not_bypass_cooldown": True,
                },
            }
        except Exception:
            return _recovery_error(
                status=409,
                code="RECOVERY_STATE_INCONSISTENT",
                message=(
                    "An intake index exists, but its immutable receipt bindings "
                    "could not be verified. Recovery failed closed."
                ),
                submission_sha256=submission_sha256,
            )

    @staticmethod
    async def _send_json(send, *, status: int, payload: dict[str, Any], head: bool) -> None:
        raw = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
        headers = [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(raw)).encode("ascii")),
            (b"cache-control", b"no-store"),
        ]
        await send({"type": "http.response.start", "status": status, "headers": headers})
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
            if recovery_match and method in {"GET", "HEAD"}:
                status, payload = await self._submission_recovery_payload(
                    recovery_match.group("submission_sha256")
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
