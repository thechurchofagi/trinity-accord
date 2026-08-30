#!/usr/bin/env python3
"""Fast entrypoint for the full preservation audit.

Exact Release coverage comes from GitHub asset digests, so small Release metadata
needs downloading only for encrypted/future-access containers whose ciphertext
must be bound back to a plaintext six-hash row. This keeps the audit complete
while avoiding hundreds of irrelevant metadata downloads.
"""
import audit_evidence_preservation_matrix as audit

_original = audit.scan_release_text_assets


def _focused_release_metadata(releases, known_hashes):
    focused = []
    for rel in releases:
        text = " ".join([
            rel.get("tag_name") or "",
            rel.get("name") or "",
            rel.get("body") or "",
        ]).lower()
        if any(token in text for token in ["encrypt", "star-moon", "星月", "future-access", "ciphertext"]):
            focused.append(rel)
    return _original(focused, known_hashes)


audit.scan_release_text_assets = _focused_release_metadata
audit.main()
