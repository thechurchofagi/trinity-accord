# gateway/runtime.py
"""Runtime information helper."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

# Bump on each deploy; allow env override for CI/CD
SERVICE_VERSION = os.environ.get("TRINITY_GATEWAY_RUNTIME_VERSION", "1.1.0")
SERVICE_NAME = "record-chain-intake-gateway"
PROTECTION_ENTRYPOINT = "apps.record_chain_intake_gateway.secure_entrypoint:app"

# This flag is intentionally process-local. Only the production secure
# entrypoint marks it true after the resource/cooldown wrapper has actually
# been imported and installed. A stale Render start command that imports the
# core app directly therefore cannot claim that the protection layer is live.
_protection_layer_active = False

# Set at module load; overwritten by healthcheck if needed
_deployed_at: str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_runtime_info() -> dict[str, Any]:
    """Return runtime metadata bound to the entrypoint actually loaded.

    The protected entrypoint attestation is code-owned rather than supplied by
    an environment variable. Operator configuration may select the Uvicorn
    start command, but it cannot forge or accidentally drift the public proof
    emitted after this module's process-local protection marker is set.
    """
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "deployed_at": _deployed_at,
        "python_version": _python_version(),
        "repo": os.environ.get("TRINITY_REPO_FULL_NAME", "(not configured)"),
        "branch": os.environ.get("TRINITY_TARGET_BRANCH", "(not configured)"),
        "write_mode": os.environ.get("TRINITY_SUBMIT_WRITE_MODE", "github_contents_pending"),
        "max_submission_bytes": int(os.environ.get("TRINITY_MAX_SUBMISSION_BYTES", "98304")),
        "record_draft_max_bytes": int(os.environ.get("TRINITY_RECORD_DRAFT_MAX_BYTES", "49152")),
        "max_text_field_chars": int(os.environ.get("TRINITY_MAX_TEXT_FIELD_CHARS", "4000")),
        "protection_layer_active": _protection_layer_active,
        "protection_entrypoint": (
            PROTECTION_ENTRYPOINT
            if _protection_layer_active
            else "core_app_without_protection_wrapper"
        ),
        "global_acceptance_cooldown_seconds": (
            {"minimum": 3600, "maximum": 7200, "secret_keyed": True}
            if _protection_layer_active
            else None
        ),
    }


def mark_protection_layer_active() -> None:
    """Attest that the secure ASGI entrypoint installed the live wrapper."""
    global _protection_layer_active
    _protection_layer_active = True


def _python_version() -> str:
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
