"""Shared deterministic security helpers for Record-Chain intake.

No network, no LLM/NLP, no external services.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any, Iterable


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("PEM_PRIVATE_KEY", re.compile(r"-----BEGIN (?:ENCRYPTED |OPENSSH |EC |RSA |DSA )?PRIVATE KEY-----")),
    ("PGP_PRIVATE_KEY", re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----")),
    ("AGE_ENCRYPTED_FILE", re.compile(r"-----BEGIN AGE ENCRYPTED FILE-----")),
    ("GITHUB_TOKEN", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("GITHUB_FINE_GRAINED_PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("OPENAI_KEY", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("ANTHROPIC_KEY", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("AWS_ACCESS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("SLACK_TOKEN", re.compile(r"\bxox(?:a|b|p|o|s|r)-[A-Za-z0-9-]{20,}\b")),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("JWT_LIKE_TOKEN", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("BEARER_LONG_TOKEN", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{40,}\b", re.IGNORECASE)),
)

PRIVATE_HUMAN_KEYS = frozenset({
    "encrypted_human_name",
    "private_identity_blob",
    "human_private_name",
    "private_human_name",
    "operator_legal_name",
    "human_legal_name",
    "legal_name",
})

PRIVATE_HUMAN_FLAG_KEYS = frozenset({
    "human_private_name_submitted",
})


def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_obj(obj: Any) -> str:
    return sha256_text(stable_json(obj))


def normalize_oath_text(text: str) -> str:
    return unicodedata.normalize(
        "NFC",
        str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip(),
    )


def iter_json_paths(value: Any, prefix: str = "$") -> Iterable[tuple[str, Any]]:
    yield prefix, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_json_paths(child, f"{prefix}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            yield from iter_json_paths(child, f"{prefix}[{idx}]")


def find_secret_hits(value: Any) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path, item in iter_json_paths(value):
        if not isinstance(item, str):
            continue
        for code, pattern in SECRET_PATTERNS:
            if pattern.search(item):
                hits.append({"code": code, "path": path})
    return hits


def find_private_human_identity_hits(value: Any) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path, item in iter_json_paths(value):
        key = path.rsplit(".", 1)[-1]
        if key in PRIVATE_HUMAN_KEYS:
            hits.append({"code": "PRIVATE_HUMAN_IDENTITY_FIELD_FORBIDDEN", "path": path})
        if key in PRIVATE_HUMAN_FLAG_KEYS and item is True:
            hits.append({"code": "HUMAN_PRIVATE_NAME_SUBMITTED_FORBIDDEN", "path": path})
    return hits
