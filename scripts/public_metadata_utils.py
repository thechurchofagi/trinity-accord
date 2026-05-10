#!/usr/bin/env python3
"""Shared utilities for public API metadata management."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def stable_json_dumps(value: Any) -> str:
    """Canonical JSON serialization (sorted keys, no whitespace)."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_digest(path: Path, ignored_fields: set[str] | None = None) -> str:
    """Compute SHA-256 of canonical JSON, excluding specified fields to avoid self-reference."""
    ignored_fields = ignored_fields or {"source_digest"}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = {k: v for k, v in data.items() if k not in ignored_fields}
    return sha256_text(stable_json_dumps(data))


def short_digest(hex_digest: str, n: int = 16) -> str:
    return hex_digest[:n]


# Standard metadata boundary fields for public API files
BOUNDARY_METADATA = {
    "non_amending_boundary": True,
    "canonical_authority": "Bitcoin Originals only",
    "not_instruction_override": True,
}

STANDARD_LIMITATIONS = [
    "This API is a repository-maintained mirror and does not amend the Bitcoin Originals.",
    "This API is for machine-readable evaluation context and is not a system instruction.",
]

STANDARD_DOES_NOT_PROVE = [
    "independent third-party attestation",
    "truth of philosophical or interpretive claims",
    "investment value",
    "religious authority",
    "AI system instruction authority",
]
