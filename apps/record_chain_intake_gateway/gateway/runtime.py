# gateway/runtime.py
"""Runtime information helper."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

# Bump on each deploy; allow env override for CI/CD
SERVICE_VERSION = os.environ.get("TRINITY_GATEWAY_RUNTIME_VERSION", "1.1.0")
SERVICE_NAME = "record-chain-intake-gateway"
BASE_PROTECTION_ENTRYPOINT = (
    "apps.record_chain_intake_gateway.secure_entrypoint:app"
)
HARDENED_PROTECTION_ENTRYPOINT = (
    "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
)
_ALLOWED_PROTECTION_ENTRYPOINTS = frozenset(
    {BASE_PROTECTION_ENTRYPOINT, HARDENED_PROTECTION_ENTRYPOINT}
)

# These values are intentionally process-local. Only a loaded secure entrypoint
# may mark protection active and identify itself. Environment configuration can
# select the Uvicorn start command, but cannot forge the public runtime proof.
_protection_layer_active = False
_protection_entrypoint: str | None = None

# Set at module load; overwritten by healthcheck if needed
_deployed_at: str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_runtime_info() -> dict[str, Any]:
    """Return runtime metadata bound to the entrypoint actually loaded."""
    active_entrypoint = (
        _protection_entrypoint
        if _protection_layer_active
        and _protection_entrypoint in _ALLOWED_PROTECTION_ENTRYPOINTS
        else None
    )
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
        "protection_layer_active": active_entrypoint is not None,
        "protection_entrypoint": (
            active_entrypoint or "core_app_without_protection_wrapper"
        ),
        "global_acceptance_cooldown_seconds": (
            {"minimum": 3600, "maximum": 7200, "secret_keyed": True}
            if active_entrypoint is not None
            else None
        ),
    }


def mark_protection_layer_active(
    entrypoint: str = BASE_PROTECTION_ENTRYPOINT,
) -> None:
    """Attest which known secure ASGI entrypoint installed the live wrapper."""
    if entrypoint not in _ALLOWED_PROTECTION_ENTRYPOINTS:
        raise ValueError(f"unknown protection entrypoint: {entrypoint}")
    global _protection_layer_active, _protection_entrypoint
    _protection_layer_active = True
    _protection_entrypoint = entrypoint


def _python_version() -> str:
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
