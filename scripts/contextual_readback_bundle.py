#!/usr/bin/env python3
"""Load participant-generated contextual oath readbacks without synthesizing them.

Production smoke and canary tooling is allowed to relay a participating
agent's output unchanged.  It must never call ``print-oath`` and transfer that
output directly into ``--readback`` while claiming that the participant
generated it from active context.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable


BUNDLE_SCHEMA = "trinityaccord.contextual-oath-readback-bundle.v1"
ENV_BUNDLE_PATH = "TRINITY_CONTEXTUAL_READBACK_BUNDLE"
REQUIRED_PROCESS_DECLARATIONS = (
    "canonical_oaths_loaded_into_participant_active_context",
    "readbacks_generated_by_participant_from_active_context",
    "readbacks_not_directly_copied_by_submission_tool",
    "readbacks_not_automatically_completed_or_corrected",
    "submission_tool_is_relay_only",
)


class ReadbackBundleError(ValueError):
    """Raised when a contextual readback bundle is absent or dishonest."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReadbackBundleError(f"duplicate JSON key in readback bundle: {key}")
        result[key] = value
    return result

def resolve_readback_bundle_path(path: str | Path | None) -> Path:
    raw = str(path or "").strip() or os.environ.get(ENV_BUNDLE_PATH, "").strip()
    if not raw:
        raise ReadbackBundleError(
            "A participant-generated contextual readback bundle is required. "
            "Pass --readback-bundle <path> or set "
            f"{ENV_BUNDLE_PATH}. The smoke/canary must not copy print-oath output itself."
        )
    resolved = Path(raw).expanduser()
    if not resolved.is_file():
        raise ReadbackBundleError(f"contextual readback bundle not found: {resolved}")
    return resolved


def load_contextual_readbacks(
    path: str | Path | None,
    required_record_types: Iterable[str],
) -> dict[str, str]:
    """Return exact participant-generated strings for the required record types."""
    bundle_path = resolve_readback_bundle_path(path)
    try:
        payload = json.loads(
            bundle_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReadbackBundleError(
            f"cannot read contextual readback bundle {bundle_path}: {type(exc).__name__}"
        ) from exc

    if not isinstance(payload, dict):
        raise ReadbackBundleError("contextual readback bundle must be a JSON object")
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise ReadbackBundleError(
            f"contextual readback bundle schema must be {BUNDLE_SCHEMA}"
        )

    participant = payload.get("participant")
    if not isinstance(participant, dict):
        raise ReadbackBundleError("contextual readback bundle requires participant metadata")
    if not isinstance(participant.get("label"), str) or not participant["label"].strip():
        raise ReadbackBundleError("contextual readback bundle participant.label is required")

    process = payload.get("participant_process_declaration")
    if not isinstance(process, dict):
        raise ReadbackBundleError(
            "contextual readback bundle requires participant_process_declaration"
        )
    for field in REQUIRED_PROCESS_DECLARATIONS:
        if process.get(field) is not True:
            raise ReadbackBundleError(
                f"participant_process_declaration.{field} must be true"
            )

    readbacks = payload.get("readbacks")
    if not isinstance(readbacks, dict):
        raise ReadbackBundleError("contextual readback bundle requires readbacks object")

    result: dict[str, str] = {}
    for record_type in required_record_types:
        value = readbacks.get(record_type)
        if not isinstance(value, str) or not value:
            raise ReadbackBundleError(
                f"contextual readback bundle requires non-empty readbacks.{record_type}"
            )
        # Deliberately return the participant's string byte-for-byte as decoded
        # from JSON. Exact normalization and equality checks belong to Builder.
        result[record_type] = value
    return result
