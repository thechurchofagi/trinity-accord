#!/usr/bin/env python3
"""Fast entrypoint for the full preservation audit.

The audit uses exact Release digests, focused encrypted-archive metadata, streaming
Git blob hashing, and checked-in Arweave provenance. It never exposes a currently
redacted wallet address in generated output.
"""
from collections import defaultdict
import datetime as dt
import hashlib
import json
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
            cwd=audit.ROOT, check=False,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120,
        )
        raw = subprocess.check_output(
            ["git", "ls-tree", "-r", "-z", commit], cwd=audit.ROOT, timeout=60
        )
    except Exception:
        return out

    blob_paths = defaultdict(list)
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        try:
            meta, path_b = entry.split(b"\t", 1)
            _mode, typ, blob = meta.split(b" ", 2)
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

    proc = None
    try:
        proc = subprocess.Popen(
            ["git", "cat-file", "--batch"], cwd=audit.ROOT,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        assert proc.stdin is not None and proc.stdout is not None
        for blob, paths in blob_paths.items():
            proc.stdin.write((blob + "\n").encode("ascii")); proc.stdin.flush()
            header = proc.stdout.readline().decode("ascii", "replace").strip()
            parts = header.split()
            if len(parts) < 3 or parts[1] != "blob":
                continue
            remaining = int(parts[2]); h = hashlib.sha256()
            while remaining:
                chunk = proc.stdout.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise RuntimeError("unexpected EOF from git cat-file --batch")
                h.update(chunk); remaining -= len(chunk)
            proc.stdout.read(1)
            out[h.hexdigest()].extend(paths)
        proc.stdin.close(); proc.wait(timeout=60)
    except Exception:
        if proc is not None:
            try: proc.kill()
            except Exception: pass
        return defaultdict(list)
    return out


def _ts(value, fallback):
    if not value:
        return fallback
    try:
        return int(dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except Exception:
        return fallback


def _load_arweave_provenance():
    current_fp = None
    current = {}
    legacy = {}
    try:
        ledger = json.loads((audit.ROOT / "record-chain/arweave-wallet-ledger.json").read_text("utf-8"))
        current_fp = (ledger.get("wallet") or {}).get("wallet_address_sha256")
        for e in ledger.get("entries") or []:
            tx = e.get("tx_id") or e.get("arweave_tx")
            if tx:
                current[tx] = _ts(e.get("confirmed_at") or e.get("paid_at") or e.get("uploaded_at"), 1780000000)
    except Exception:
        pass
    try:
        legacy_manifest = json.loads((audit.ROOT / "arweave-backup/manifest.json").read_text("utf-8"))
        for e in legacy_manifest.get("entries") or []:
            tx = e.get("arweave_tx")
            if tx:
                legacy[tx] = _ts(e.get("uploaded_at"), 1760000000)
        # Parent of the original 4EVERLAND / ANS-104 public-covenant data item.
        legacy.setdefault("AuS0h1G8SYGPLbECyaceCqX6mB0xjFvny6bn1BUf2MI", 1754810547)
    except Exception:
        pass
    return current_fp, current, legacy


_current_fp, _current_txs, _legacy_txs = _load_arweave_provenance()
_legacy_fp = hashlib.sha256(b"trinityaccord:legacy-4everland-ans104-provenance").hexdigest()


def _checked_in_arweave_group(txid: str):
    if txid in _current_txs and _current_fp:
        return {"address_sha256": _current_fp, "block_height": None, "block_timestamp": _current_txs[txid]}
    if txid in _legacy_txs:
        return {"address_sha256": _legacy_fp, "block_height": None, "block_timestamp": _legacy_txs[txid]}
    return None


def _annotate_methodology():
    summary_path = audit.OUT / "summary.json"
    owners_path = audit.OUT / "arweave-owner-groups.json"
    if summary_path.exists():
        s = json.loads(summary_path.read_text("utf-8"))
        s.setdefault("storage_domains", {}).setdefault("arweave", {})["owner_group_method"] = (
            "checked-in provenance: legacy arweave-backup/manifest.json (4EVERLAND/ANS-104) "
            "versus record-chain/arweave-wallet-ledger.json (current native wallet); unknown TXs remain unresolved"
        )
        s.setdefault("limitations", []).append(
            "AR old/new grouping is based on checked-in preservation provenance rather than live owner lookups; this avoids network-dependent false negatives and respects the current wallet redaction policy."
        )
        summary_path.write_text(json.dumps(s, ensure_ascii=False, indent=2, default=str) + "\n", "utf-8")
    if owners_path.exists():
        o = json.loads(owners_path.read_text("utf-8"))
        o["group_method"] = "checked-in legacy manifest vs current wallet ledger; literal current wallet address not emitted"
        owners_path.write_text(json.dumps(o, ensure_ascii=False, indent=2) + "\n", "utf-8")


audit.scan_release_text_assets = _focused_release_metadata
audit.git_hash_index = _batch_git_hash_index
audit.arweave_owner_fingerprint = _checked_in_arweave_group
audit.main()
_annotate_methodology()
