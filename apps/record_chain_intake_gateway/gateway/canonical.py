# gateway/canonical.py
"""Canonical JSON serialization and SHA-256 hashing utilities."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _reject_non_finite_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON number is forbidden: {value}")


def _reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key is forbidden: {key}")
        result[key] = value
    return result


def parse_json_strict(data: str | bytes | bytearray) -> Any:
    """Parse standards-compliant JSON and reject duplicate keys and NaN/Infinity."""
    return json.loads(
        data,
        parse_constant=_reject_non_finite_constant,
        object_pairs_hook=_reject_duplicate_object_pairs,
    )


def canonical_dumps(obj: Any) -> str:
    """Serialize *obj* to a canonical JSON string.

    Rules:
    - Keys are sorted recursively.
    - No extra whitespace (``separators=(',', ':')``).
    - ``ensure_ascii=False`` to preserve Unicode.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def canonical_bytes(obj: Any) -> bytes:
    """Return the UTF-8 encoding of :func:`canonical_dumps`."""
    return canonical_dumps(obj).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    """Return the hex-encoded SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_canonical_json(obj: Any) -> str:
    """SHA-256 of the canonical JSON representation of *obj*."""
    return sha256_bytes(canonical_bytes(obj))
