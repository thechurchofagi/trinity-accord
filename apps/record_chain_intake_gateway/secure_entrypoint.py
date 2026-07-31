"""Production entrypoint for the protected Record-Chain Gateway.

The public repository must not make the exact reopening time computable from a
public commit SHA. This entrypoint replaces the unkeyed test/reference interval
function with HMAC-SHA256 keyed by a server-only secret before exposing the ASGI
application.

A dedicated ``TRINITY_COOLDOWN_SECRET`` is preferred. The already-required
``TRINITY_GITHUB_TOKEN`` is a fail-safe fallback so an existing production
service fails closed rather than silently losing the cooldown during rollout.
"""
from __future__ import annotations

import hashlib
import hmac
import os

from apps.record_chain_intake_gateway import protected_app as protection


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

app = protection.app
