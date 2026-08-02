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
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any

from apps.record_chain_intake_gateway import protected_app as protection
from apps.record_chain_intake_gateway.gateway import runtime


_MAX_BLOCKED_CLIENT_KEYS = 10_000
_BLOCKED_CLIENT_TARGET = 8_000
_PROTECTED_HEALTH_PATHS = frozenset({"/healthz", "/readyz"})


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


class ProtectedProductionApp:
    """ASGI wrapper exposing fail-closed production health/readiness routes."""

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
                "protection_layer_active": info["protection_layer_active"],
                "protection_entrypoint": info["protection_entrypoint"],
                "repo_configured": repo_configured,
                "branch_configured": branch_configured,
                "token_configured": token_configured,
                "cooldown_secret_configured": cooldown_secret_configured,
            },
        )

    async def __call__(self, scope, receive, send) -> None:
        if (
            scope.get("type") == "http"
            and scope.get("path") in _PROTECTED_HEALTH_PATHS
            and str(scope.get("method") or "").upper() in {"GET", "HEAD"}
        ):
            status, payload = self._readiness_payload()
            raw = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
            headers = [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(raw)).encode("ascii")),
                (b"cache-control", b"no-store"),
            ]
            await send({"type": "http.response.start", "status": status, "headers": headers})
            body = b"" if str(scope.get("method") or "").upper() == "HEAD" else raw
            await send({"type": "http.response.body", "body": body, "more_body": False})
            return
        await self.app(scope, receive, send)


app = ProtectedProductionApp(protection.app)
