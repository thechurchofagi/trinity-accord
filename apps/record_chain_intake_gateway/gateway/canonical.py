# gateway/canonical.py
"""Canonical JSON serialization and SHA-256 hashing utilities."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_dumps(obj: Any) -> str:
    """Serialize *obj* to a canonical JSON string.

    Rules:
    - Keys are sorted recursively.
    - No extra whitespace (``separators=(',', ':')``).
    - ``ensure_ascii=False`` to preserve Unicode.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_bytes(obj: Any) -> bytes:
    """Return the UTF-8 encoding of :func:`canonical_dumps`."""
    return canonical_dumps(obj).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    """Return the hex-encoded SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_canonical_json(obj: Any) -> str:
    """SHA-256 of the canonical JSON representation of *obj*."""
    return sha256_bytes(canonical_bytes(obj))
