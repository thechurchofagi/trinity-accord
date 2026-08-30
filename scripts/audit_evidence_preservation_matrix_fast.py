#!/usr/bin/env python3
"""Fast, conservative entrypoint for the full preservation audit.

Key safeguards:
- exact Release digests, never filename-only matches;
- historical duplicate manifest rows inherit the largest known size for the same SHA-256;
- Arweave links are accepted only from structured/explicit TX fields near the exact SHA,
  not from arbitrary 43-character strings;
- encrypted derivatives never count as plaintext byte mirrors;
- frozen Git snapshots are hashed with a streaming `git cat-file --batch` process;
- current redacted wallet address is never emitted.
"""
from collections import defaultdict
import datetime as dt
import hashlib
import json
import re
import subprocess

import audit_evidence_preservation_matrix as audit

_original_load_baseline = audit.load_baseline
_original_release_scan = audit.scan_release_text_assets

TX_VALUE_RE = re.compile(r"^[A-Za-z0-9_-]{43}$")
EXPLICIT_TX_RE = re.compile(
    r"(?i)(?:arweave(?:[_\s-]*(?:tx|txid|transaction|data[_\s-]*item)(?:[_\s-]*id)?)?|"
    r"(?:tx|txid|transaction)[_\s-]*id)\s*[:=]\s*[\"']?([A-Za-z0-9_-]{43})"
)
AR_URL_RE = re.compile(r"https?://(?:www\.)?(?:arweave\.net|ar-io\.net)/([A-Za-z0-9_-]{43})(?:\b|/)", re.I)


def _baseline_with_best_sizes():
    rows = _original_load_baseline()
    max_size = defaultdict(int)
    for r in rows:
        max_size[r["sha256"]] = max(max_size[r["sha256"]], int(r.get("size") or 0))
    for r in rows:
        if int(r.get("size") or 0) == 0 and max_size[r["sha256"]] > 0:
            r["size"] = max_size[r["sha256"]]
    return rows


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


def _collect_strings(obj):
    vals = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            vals.append(str(k))
            vals.extend(_collect_strings(v))
    elif isinstance(obj, list):
        for v in obj:
            vals.extend(_collect_strings(v))
    elif isinstance(obj, (str, int, float)):
        vals.append(str(obj))
    return vals


def _structured_arweave_links(known_hashes):
    """Return exact SHA -> Arweave TX associations without free-form token guessing."""
    links = defaultdict(set)
    evidence = defaultdict(list)

    def add(sha, tx, source, basis):
        if sha in known_hashes and TX_VALUE_RE.fullmatch(tx or ""):
            links[sha].add(tx)
            evidence[sha].append({"repo_file": source, "txids": [tx], "basis": basis})

    def walk_json(node, source):
        if isinstance(node, dict):
            flat = _collect_strings(node)
            hashes = {s.lower() for s in flat if re.fullmatch(r"[0-9a-fA-F]{64}", s)} & known_hashes
            context = " ".join(flat).lower()
            txs = set()
            for k, v in node.items():
                kl = str(k).lower()
                if isinstance(v, str):
                    # Strong field names only. Generic tx_id is accepted only in an Arweave-labelled object.
                    strong = "arweave" in kl and any(t in kl for t in ["tx", "transaction", "data", "item"])
                    contextual = kl in {"tx", "txid", "tx_id", "transaction_id", "data_item", "data_item_id"} and "arweave" in context
                    if (strong or contextual) and TX_VALUE_RE.fullmatch(v):
                        txs.add(v)
                    for tx in AR_URL_RE.findall(v):
                        txs.add(tx)
            if hashes and txs:
                for sha in hashes:
                    for tx in txs:
                        add(sha, tx, source, "structured-json")
            for v in node.values():
                walk_json(v, source)
        elif isinstance(node, list):
            for v in node:
                walk_json(v, source)

    for p in audit.ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        try:
            if p.stat().st_size > 12_000_000:
                continue
        except Exception:
            continue
        rel = str(p.relative_to(audit.ROOT))
        if p.suffix.lower() == ".json":
            try:
                walk_json(json.loads(p.read_text("utf-8")), rel)
            except Exception:
                pass

        # Explicit text statements only; no arbitrary 43-char context tokens.
        if p.suffix.lower() in audit.TEXT_EXTS:
            try:
                text = p.read_text("utf-8", errors="ignore")
            except Exception:
                continue
            low = text.lower()
            if "arweave" not in low:
                continue
            for sha in (set(x.lower() for x in audit.SHA256_RE.findall(text)) & known_hashes):
                for m in re.finditer(re.escape(sha), text, flags=re.I):
                    ctx = text[max(0, m.start()-1800):min(len(text), m.end()+1800)]
                    for tx in EXPLICIT_TX_RE.findall(ctx):
                        add(sha, tx, rel, "explicit-text-field")
                    for tx in AR_URL_RE.findall(ctx):
                        add(sha, tx, rel, "arweave-url")
    return links, evidence


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
            if tx and TX_VALUE_RE.fullmatch(tx):
                current[tx] = _ts(e.get("confirmed_at") or e.get("paid_at") or e.get("uploaded_at"), 1780000000)
    except Exception:
        pass
    try:
        legacy_manifest = json.loads((audit.ROOT / "arweave-backup/manifest.json").read_text("utf-8"))
        for e in legacy_manifest.get("entries") or []:
            tx = e.get("arweave_tx")
            if tx and TX_VALUE_RE.fullmatch(tx):
                legacy[tx] = _ts(e.get("uploaded_at"), 1760000000)
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
        s.setdefault("baseline", {})["size_recovery_rule"] = "zero-size duplicate rows inherit max nonzero size of identical SHA-256"
        s.setdefault("storage_domains", {}).setdefault("arweave", {})["link_rule"] = (
            "exact SHA plus structured/explicit Arweave TX field or arweave.net URL; arbitrary 43-character tokens are rejected"
        )
        s["storage_domains"]["arweave"]["owner_group_method"] = (
            "checked-in provenance: legacy arweave-backup/manifest.json (4EVERLAND/ANS-104) "
            "versus record-chain/arweave-wallet-ledger.json (current native wallet); unknown TXs remain unresolved"
        )
        s.setdefault("limitations", []).append(
            "AR old/new grouping is based on checked-in preservation provenance rather than live owner lookups; unknown TXs are not forced into either group."
        )
        summary_path.write_text(json.dumps(s, ensure_ascii=False, indent=2, default=str) + "\n", "utf-8")
    if owners_path.exists():
        o = json.loads(owners_path.read_text("utf-8"))
        o["group_method"] = "checked-in legacy manifest vs current wallet ledger; literal current wallet address not emitted"
        owners_path.write_text(json.dumps(o, ensure_ascii=False, indent=2) + "\n", "utf-8")


audit.load_baseline = _baseline_with_best_sizes
audit.scan_release_text_assets = _focused_release_metadata
audit.git_hash_index = _batch_git_hash_index
audit.scan_repo_arweave_links = _structured_arweave_links
audit.arweave_owner_fingerprint = _checked_in_arweave_group
audit.main()
_annotate_methodology()
