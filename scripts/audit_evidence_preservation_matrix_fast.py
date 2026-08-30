#!/usr/bin/env python3
"""Fast entrypoint for the full preservation audit.

Exact Release coverage comes from GitHub asset digests, so small Release metadata
needs downloading only for encrypted/future-access containers whose ciphertext
must be bound back to a plaintext six-hash row. Frozen Git snapshots are hashed
with one `git cat-file --batch` process instead of thousands of `git show` calls.
"""
from collections import defaultdict
import hashlib
import subprocess

import audit_evidence_preservation_matrix as audit

_original_release_scan = audit.scan_release_text_assets


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
    return _original_release_scan(focused, known_hashes)


def _batch_git_hash_index(commit: str):
    out = defaultdict(list)
    try:
        subprocess.run(
            ["git", "fetch", "origin", commit, "--depth=1"],
            cwd=audit.ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120,
        )
        raw = subprocess.check_output(
            ["git", "ls-tree", "-r", "-z", commit],
            cwd=audit.ROOT,
            timeout=60,
        )
    except Exception:
        return out

    blob_paths = defaultdict(list)
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        try:
            meta, path_b = entry.split(b"\t", 1)
            mode, typ, blob = meta.split(b" ", 2)
            if typ != b"blob":
                continue
            path = path_b.decode("utf-8", "replace")
            if path.startswith(("node_modules/", ".git/")):
                continue
            blob_paths[blob.decode("ascii")].append(path)
        except Exception:
            continue

    if not blob_paths:
        return out

    try:
        proc = subprocess.Popen(
            ["git", "cat-file", "--batch"],
            cwd=audit.ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        assert proc.stdin is not None and proc.stdout is not None
        for blob in blob_paths:
            proc.stdin.write((blob + "\n").encode("ascii"))
        proc.stdin.close()

        for blob in blob_paths:
            header = proc.stdout.readline().decode("ascii", "replace").strip()
            parts = header.split()
            if len(parts) < 3 or parts[1] != "blob":
                continue
            size = int(parts[2])
            remaining = size
            h = hashlib.sha256()
            while remaining:
                chunk = proc.stdout.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise RuntimeError("unexpected EOF from git cat-file --batch")
                h.update(chunk)
                remaining -= len(chunk)
            proc.stdout.read(1)  # trailing newline after batch object body
            out[h.hexdigest()].extend(blob_paths[blob])
        proc.wait(timeout=60)
    except Exception:
        return defaultdict(list)
    return out


audit.scan_release_text_assets = _focused_release_metadata
audit.git_hash_index = _batch_git_hash_index
audit.main()
