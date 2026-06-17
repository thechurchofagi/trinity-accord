# gateway/runtime.py
"""Runtime information helper."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

# Bump on each deploy; allow env override for CI/CD
SERVICE_VERSION = os.environ.get("TRINITY_GATEWAY_RUNTIME_VERSION", "1.1.0")
SERVICE_NAME = "record-chain-intake-gateway"

# Set at module load; overwritten by healthcheck if needed
_deployed_at: str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_runtime_info() -> dict[str, Any]:
    """Return a dict of runtime metadata suitable for health / readiness responses."""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "deployed_at": _deployed_at,
        "python_version": _python_version(),
        "repo": os.environ.get("TRINITY_REPO_FULL_NAME", "(not configured)"),
        "branch": os.environ.get("TRINITY_TARGET_BRANCH", "(not configured)"),
        "write_mode": os.environ.get("TRINITY_SUBMIT_WRITE_MODE", "github_contents_pending"),
        "max_submission_bytes": int(os.environ.get("TRINITY_MAX_SUBMISSION_BYTES", "524288")),
    }


def _python_version() -> str:
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
