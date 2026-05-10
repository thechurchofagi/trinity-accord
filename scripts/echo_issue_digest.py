#!/usr/bin/env python3
"""
Echo issue screening digest helper.

Computes a stable SHA-256 digest of issue title+body for TOCTOU binding.
Used by triage (to embed) and archive (to verify).
"""
from __future__ import annotations

import hashlib
import re


def normalize_issue_text(value: str | None) -> str:
    """Normalize issue text for stable digest computation."""
    value = value or ""
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def compute_issue_screening_digest(title: str | None, body: str | None) -> str:
    """Compute SHA-256 digest of normalized title+body.

    Format: SHA-256("trinity-echo-screened-v1\0" + norm_title + "\0" + norm_body)
    """
    h = hashlib.sha256()
    h.update(b"trinity-echo-screened-v1\0")
    h.update(normalize_issue_text(title).encode("utf-8"))
    h.update(b"\0")
    h.update(normalize_issue_text(body).encode("utf-8"))
    return h.hexdigest()


DIGEST_RE = re.compile(
    r"<!--\s*trinity-echo-screened-digest:v1\s+sha256=([a-f0-9]{64})\s*-->",
    re.I,
)


def extract_digest_from_comments(comments: list[dict]) -> str | None:
    """Extract the latest screened digest from triage bot comments.

    Only accepts comments containing the trinity-echo-triage marker.
    Returns the latest digest hex string, or None if not found.
    """
    latest_digest = None
    for comment in comments:
        body = comment.get("body") or ""
        # Only accept comments with the triage marker
        if "<!-- trinity-echo-triage" not in body.lower():
            continue
        m = DIGEST_RE.search(body)
        if m:
            latest_digest = m.group(1).lower()
    return latest_digest


def markdown_escape_text(value: str) -> str:
    """Escape Markdown special characters in user-supplied text.

    Prevents structure injection (fake links, headings, lists) in archive.md.
    """
    value = value or ""
    # Collapse newlines to spaces
    value = value.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    value = re.sub(r"\s+", " ", value).strip()
    # Escape Markdown control characters
    for ch in ["\\", "[", "]", "(", ")", "`", "*", "_", "{", "}", "<", ">", "#", "|"]:
        value = value.replace(ch, "\\" + ch)
    return value[:300]
