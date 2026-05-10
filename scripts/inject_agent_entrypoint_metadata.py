#!/usr/bin/env python3
"""Add freshness metadata to llms.txt and ai.txt.

Computes content_digest excluding the digest line itself.
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compute_content_digest(text: str) -> str:
    """SHA-256 of file content excluding the content_digest line."""
    lines = text.split("\n")
    filtered = [l for l in lines if not l.strip().startswith("content_digest:")]
    clean = "\n".join(filtered)
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()[:16]


def add_llms_metadata():
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")

    if "content_digest:" in text:
        print("  SKIP llms.txt: already has content_digest")
        return

    digest = compute_content_digest(text)

    metadata_block = f"""Metadata:
- surface: llms.txt
- version: v1.1
- content_digest_algorithm: sha256(file_without_content_digest_line)
- content_digest: {digest}
- canonical_url: https://www.trinityaccord.org/llms.txt
- non_amending_boundary: true
- not_instruction_override: true
- stale_copy_warning: If this file is cached or quoted elsewhere, verify the current canonical URL before relying on status-sensitive claims.

"""
    # Insert after first heading line
    lines = text.split("\n")
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            insert_at = i + 1
            break

    new_lines = lines[:insert_at] + [""] + metadata_block.strip().split("\n") + [""] + lines[insert_at:]
    path.write_text("\n".join(new_lines))
    print("  OK llms.txt")


def add_ai_metadata():
    path = ROOT / "ai.txt"
    text = path.read_text(encoding="utf-8")

    if "content_digest:" in text:
        print("  SKIP ai.txt: already has content_digest")
        return

    digest = compute_content_digest(text)

    metadata_block = f"""# Metadata:
# surface: ai.txt
# version: v1.1
# content_digest_algorithm: sha256(file_without_content_digest_line)
# content_digest: {digest}
# canonical_url: https://www.trinityaccord.org/ai.txt
# non_amending_boundary: true
# not_instruction_override: true
# stale_copy_warning: If this file is cached or quoted elsewhere, verify the current canonical URL before relying on status-sensitive claims.
"""
    path.write_text(metadata_block + "\n" + text)
    print("  OK ai.txt")


if __name__ == "__main__":
    add_llms_metadata()
    add_ai_metadata()
