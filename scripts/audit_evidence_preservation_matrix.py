#!/usr/bin/env python3
"""Build a conservative preservation matrix from the historical six-hash manifest.

The audit deliberately distinguishes:
- digest/OTS commitment from recoverable original bytes;
- exact plaintext byte mirrors from encrypted future-access derivatives;
- Arweave native-owner groups from transaction/data-item identifiers;
- the historical six-hash corpus from later legal/notarial supplements.

No secrets are required. Only public APIs and checked-in metadata are used.
"""
from __future__ import annotations

import base64
import csv
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "archive/evidence/digest-manifest.csv"
OUT = ROOT / "audit" / "evidence-preservation"
REPO = os.environ.get("GITHUB_REPOSITORY", "thechurchofagi/trinity-accord")
GH_API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

HARVARD_DOI = "10.7910/DVN/YUCG12"
HARVARD_RUN_ID = 32368866492
HARVARD_SOURCE_COMMIT = "07cd79ba7b98294a0ff9bc45d76f305609f8a0aa"
ZENODO_EXTERNAL_EVIDENCE_DOI = "10.5281/zenodo.21753937"
ZENODO_NFT_DOI = "10.5281/zenodo.21754229"
ZENODO_CORE_CONCEPT_DOI = "10.5281/zenodo.21739343"

# The repository contract states that every custom asset from these releases is
# embedded byte-for-byte in the external-evidence Zenodo annex.
ZENODO_EXTERNAL_RELEASE_TAGS = {
    "signed-large-data-mirror-v1",
    "notarial-certificate-images-v1",
    "flaw-covenant-video-mirror-v1",
    "ots-proof-bundle-mirror-v1",
    "ots-and-flaw-mirror-v1",
    "flaw-covenant-archive-accessibility-mirror-v1",
}

TEXT_EXTS = {
    ".json", ".jsonl", ".csv", ".txt", ".md", ".yml", ".yaml", ".toml",
    ".xml", ".html", ".js", ".mjs", ".cjs", ".py", ".ts", ".tsx", ".sh",
    ".ps1", ".ini", ".cfg", ".log", ".sha256", ".ots",
}
SHA256_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-fA-F]{64})(?![0-9a-fA-F])")
TX_RE = re.compile(r"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{43})(?![A-Za-z0-9_-])")
DOI_RE = re.compile(r"10\.5281/zenodo\.(\d+)")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def request_json(url: str, *, method: str = "GET", data=None, headers=None, attempts: int = 3):
    hdr = {"User-Agent": "trinity-accord-preservation-audit/1.0", "Accept": "application/json"}
    if TOKEN and "api.github.com" in url:
        hdr["Authorization"] = f"Bearer {TOKEN}"
        hdr["X-GitHub-Api-Version"] = "2022-11-28"
    if headers:
        hdr.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8") if not isinstance(data, (bytes, bytearray)) else data
        hdr.setdefault("Content-Type", "application/json")
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, data=body, headers=hdr, method=method)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # public-network audit: preserve failure, don't hide it
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"request failed after {attempts} attempts: {url}: {last}")


def request_bytes(url: str, *, max_bytes: int = 2_000_000, attempts: int = 2) -> bytes | None:
    hdr = {"User-Agent": "trinity-accord-preservation-audit/1.0"}
    if TOKEN and "github.com" in url:
        hdr["Authorization"] = f"Bearer {TOKEN}"
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers=hdr)
            with urllib.request.urlopen(req, timeout=45) as r:
                length = r.headers.get("Content-Length")
                if length and int(length) > max_bytes:
                    return None
                data = r.read(max_bytes + 1)
                return data if len(data) <= max_bytes else None
        except Exception:
            time.sleep(1.0 * (i + 1))
    return None


def parse_iso(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def load_baseline():
    rows = []
    with BASELINE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader, start=2):
            sha = (r.get("sha256") or "").lower().strip()
            if not re.fullmatch(r"[0-9a-f]{64}", sha):
                continue
            path = r.get("path", "")
            rows.append({
                "manifest_line": i,
                "path": path,
                "size": int(r.get("size") or 0),
                "sha256": sha,
                "sha3_256": (r.get("sha3_256") or "").strip(),
                "blake2b_256": (r.get("blake2b_256") or "").strip(),
                "shake256_256": (r.get("shake256_256") or "").strip(),
                "sha512_256": (r.get("sha512_256") or "").strip(),
                "blake3_256": (r.get("blake3_256") or "").strip(),
            })
    return rows


def classify_privacy(path: str) -> str:
    p = path.lower()
    if "sealed" in p or "密封" in p:
        return "sealed"
    if any(x in p for x in ["不公开", "未公开", "non-public", "private", "raw数据"]):
        return "non_public"
    if "公开" in p:
        return "public"
    return "unspecified"


def classify_kind(path: str) -> str:
    p = path.lower()
    ext = Path(path.replace("\\", "/")).suffix.lower()
    if "星月见证-第二次" in path:
        return "second_star_moon_witness"
    if "星月见证" in path:
        return "first_star_moon_witness"
    if "公证" in path or "notarial" in p:
        return "notarial"
    if "瑕疵" in path or "flaw" in p:
        return "flaw_evidence"
    if "应力" in path or "stress" in p:
        return "stress_test"
    if "raw数据" in p:
        return "raw_data"
    if ext in {".mp4", ".avi", ".mov", ".mkv"}:
        return "video"
    if ext in {".jpg", ".jpeg", ".png", ".dng", ".bmp", ".tif", ".tiff", ".raw"}:
        return "image"
    if ext in {".zip", ".tar", ".gz", ".7z"}:
        return "archive"
    return "other"


def github_releases():
    releases = []
    page = 1
    while True:
        url = f"{GH_API}/repos/{REPO}/releases?per_page=100&page={page}"
        batch = request_json(url)
        if not batch:
            break
        releases.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return releases


def normalize_asset_sha(asset: dict) -> str | None:
    digest = asset.get("digest") or ""
    if digest.startswith("sha256:") and re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest):
        return digest.split(":", 1)[1].lower()
    return None


def get_harvard_cutoff():
    try:
        run = request_json(f"{GH_API}/repos/{REPO}/actions/runs/{HARVARD_RUN_ID}")
        cutoff = parse_iso(run.get("run_started_at") or run.get("created_at"))
        return cutoff, {
            "run_id": HARVARD_RUN_ID,
            "head_sha": run.get("head_sha"),
            "created_at": run.get("created_at"),
            "run_started_at": run.get("run_started_at"),
            "conclusion": run.get("conclusion"),
        }
    except Exception as e:
        # Fail conservative: no inferred Harvard release coverage if exact cutoff is unavailable.
        return None, {"run_id": HARVARD_RUN_ID, "error": str(e)}


def git_hash_index(commit: str):
    """Map sha256(content)->repo paths at one exact commit. Conservative on failures."""
    out = defaultdict(list)
    try:
        subprocess.run(["git", "fetch", "origin", commit, "--depth=1"], cwd=ROOT, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        ls = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", commit], cwd=ROOT, timeout=60)
        paths = ls.decode("utf-8", "replace").splitlines()
    except Exception:
        return out
    for path in paths:
        try:
            # Skip obvious vendored/generated paths that cannot represent historical evidence originals.
            if path.startswith(("node_modules/", ".git/")):
                continue
            data = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, timeout=20)
            out[hashlib.sha256(data).hexdigest()].append(path)
        except Exception:
            continue
    return out


def current_repo_hash_index():
    out = defaultdict(list)
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        try:
            if p.stat().st_size > 100_000_000:
                continue
            h = hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            out[h.hexdigest()].append(str(p.relative_to(ROOT)))
        except Exception:
            pass
    return out


def scan_repo_arweave_links(known_hashes: set[str]):
    """Find checked-in exact hash -> Arweave tx/data-item claims.

    We only accept 43-char tokens from contexts explicitly mentioning Arweave/TXID,
    reducing false positives from unrelated IDs.
    """
    links = defaultdict(set)
    evidence = defaultdict(list)
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            if p.stat().st_size > 12_000_000:
                continue
            text = p.read_text("utf-8", errors="ignore")
        except Exception:
            continue
        low = text.lower()
        if "arweave" not in low and "txid" not in low:
            continue
        found = set(x.lower() for x in SHA256_RE.findall(text)) & known_hashes
        if not found:
            continue
        for sha in found:
            for m in re.finditer(re.escape(sha), text, flags=re.IGNORECASE):
                ctx = text[max(0, m.start()-1400):min(len(text), m.end()+1400)]
                if "arweave" not in ctx.lower() and "txid" not in ctx.lower():
                    continue
                txs = set(TX_RE.findall(ctx))
                # reject tokens that are clearly DOI/version words by requiring at least one AR cue nearby
                for tx in txs:
                    links[sha].add(tx)
                if txs:
                    evidence[sha].append({"repo_file": str(p.relative_to(ROOT)), "txids": sorted(txs)})
    return links, evidence


def scan_release_text_assets(releases, known_hashes: set[str]):
    """Map baseline hashes referenced by small Release metadata assets.

    This detects encrypted containers that bind ciphertext to a plaintext six-hash row
    without incorrectly calling the plaintext itself a Release asset.
    """
    refs = defaultdict(list)
    doi_refs = defaultdict(set)
    for rel in releases:
        tag = rel.get("tag_name", "")
        body = rel.get("body") or ""
        body_hashes = set(x.lower() for x in SHA256_RE.findall(body)) & known_hashes
        body_dois = {f"10.5281/zenodo.{x}" for x in DOI_RE.findall(body)}
        for sha in body_hashes:
            refs[sha].append({"tag": tag, "source": "release_body", "encrypted": "encrypt" in (tag + " " + body).lower()})
            doi_refs[sha].update(body_dois)
        for asset in rel.get("assets", []):
            name = asset.get("name", "")
            size = int(asset.get("size") or 0)
            if size <= 0 or size > 2_000_000:
                continue
            if Path(name).suffix.lower() not in TEXT_EXTS and not any(k in name.lower() for k in ["manifest", "readme", "report", "verification", "checksum"]):
                continue
            url = asset.get("browser_download_url")
            if not url:
                continue
            data = request_bytes(url, max_bytes=2_000_000)
            if not data:
                continue
            text = data.decode("utf-8", "ignore")
            hashes = set(x.lower() for x in SHA256_RE.findall(text)) & known_hashes
            dois = {f"10.5281/zenodo.{x}" for x in DOI_RE.findall(text)}
            encrypted = "encrypt" in (tag + " " + name + " " + text[:5000]).lower()
            for sha in hashes:
                refs[sha].append({"tag": tag, "source": name, "encrypted": encrypted})
                doi_refs[sha].update(dois)
    return refs, doi_refs


def arweave_owner_fingerprint(txid: str):
    """Return privacy-preserving fingerprint of native Arweave owner address.

    We do not emit the wallet address itself because the checked-in wallet ledger
    explicitly sets public_address_allowed=false.
    """
    try:
        tx = request_json(f"https://arweave.net/tx/{txid}", attempts=2)
        owner = tx.get("owner")
        if not owner:
            return None
        padded = owner + "=" * ((4 - len(owner) % 4) % 4)
        owner_bytes = base64.urlsafe_b64decode(padded.encode("ascii"))
        addr = base64.urlsafe_b64encode(hashlib.sha256(owner_bytes).digest()).decode("ascii").rstrip("=")
        return {
            "address_sha256": hashlib.sha256(addr.encode("ascii")).hexdigest(),
            "block_height": (tx.get("block") or {}).get("height"),
            "block_timestamp": (tx.get("block") or {}).get("timestamp"),
        }
    except Exception:
        return None


def current_wallet_fingerprint():
    p = ROOT / "record-chain/arweave-wallet-ledger.json"
    try:
        j = json.loads(p.read_text("utf-8"))
        return j.get("wallet", {}).get("wallet_address_sha256")
    except Exception:
        return None


def zenodo_live_state():
    state = {}
    for doi in [ZENODO_EXTERNAL_EVIDENCE_DOI, ZENODO_NFT_DOI]:
        rid = doi.rsplit(".", 1)[1]
        try:
            rec = request_json(f"https://zenodo.org/api/records/{rid}")
            state[doi] = {
                "id": rec.get("id"),
                "title": (rec.get("metadata") or {}).get("title"),
                "publication_date": (rec.get("metadata") or {}).get("publication_date"),
                "files": [{"key": f.get("key"), "size": f.get("size"), "checksum": f.get("checksum")} for f in rec.get("files", [])],
            }
        except Exception as e:
            state[doi] = {"error": str(e)}
    # Search for any newer Star-Moon / encrypted preservation deposit.
    query = urllib.parse.urlencode({"q": '"Trinity Accord" "Star-Moon"', "size": 100, "sort": "newest"})
    try:
        data = request_json(f"https://zenodo.org/api/records?{query}")
        hits = (data.get("hits") or {}).get("hits") or []
        state["star_moon_search"] = [
            {"id": h.get("id"), "doi": (h.get("pids") or {}).get("doi", {}).get("identifier"), "title": (h.get("metadata") or {}).get("title"),
             "publication_date": (h.get("metadata") or {}).get("publication_date"),
             "files": [{"key": f.get("key"), "size": f.get("size"), "checksum": f.get("checksum")} for f in h.get("files", [])]}
            for h in hits[:30]
        ]
    except Exception as e:
        state["star_moon_search"] = {"error": str(e)}
    return state


def harvard_live_state():
    url = "https://dataverse.harvard.edu/api/datasets/:persistentId/?" + urllib.parse.urlencode({"persistentId": f"doi:{HARVARD_DOI}"})
    try:
        j = request_json(url)
        data = j.get("data") or {}
        latest = data.get("latestVersion") or {}
        return {
            "status": j.get("status"),
            "version_state": latest.get("versionState"),
            "version": f"{latest.get('versionNumber')}.{latest.get('versionMinorNumber')}",
            "release_time": latest.get("releaseTime"),
            "file_count": len(latest.get("files") or []),
            "files": [{"label": (x.get("dataFile") or {}).get("filename"), "size": (x.get("dataFile") or {}).get("filesize"),
                       "checksum": ((x.get("dataFile") or {}).get("checksum") or {}).get("value")} for x in latest.get("files") or []],
        }
    except Exception as e:
        return {"error": str(e)}


def build_notary_annex(releases, zenodo_state, harvard_cutoff):
    tags = {
        "notarial-certificate-images-v1",
        "core-object-alpha-notarial-certificate-gz2-custody-public-backup-v1",
    }
    rows = []
    for rel in releases:
        if rel.get("tag_name") not in tags:
            continue
        for a in rel.get("assets", []):
            created = parse_iso(a.get("created_at"))
            rows.append({
                "release_tag": rel.get("tag_name"),
                "asset": a.get("name"),
                "bytes": a.get("size"),
                "sha256": normalize_asset_sha(a),
                "github_release": True,
                "zenodo_external_annex": rel.get("tag_name") in ZENODO_EXTERNAL_RELEASE_TAGS,
                "harvard_v1": bool(harvard_cutoff and created and created <= harvard_cutoff),
                "privacy_note": "public/redacted release asset; full identity-bearing notarization is not inferred from this public asset",
            })
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = load_baseline()
    known_hashes = {r["sha256"] for r in baseline}
    by_sha = defaultdict(list)
    for r in baseline:
        by_sha[r["sha256"]].append(r)

    releases = github_releases()
    harvard_cutoff, harvard_run = get_harvard_cutoff()
    zenodo_state = zenodo_live_state()
    harvard_state = harvard_live_state()

    release_exact = defaultdict(list)
    zenodo_exact = defaultdict(list)
    harvard_release_exact = defaultdict(list)
    for rel in releases:
        tag = rel.get("tag_name", "")
        for a in rel.get("assets", []):
            sha = normalize_asset_sha(a)
            if not sha or sha not in known_hashes:
                continue
            rec = {
                "tag": tag, "asset": a.get("name"), "bytes": a.get("size"), "created_at": a.get("created_at"),
                "url": a.get("browser_download_url"),
            }
            release_exact[sha].append(rec)
            if tag in ZENODO_EXTERNAL_RELEASE_TAGS:
                zenodo_exact[sha].append({"doi": ZENODO_EXTERNAL_EVIDENCE_DOI, "basis": f"byte-for-byte external annex of release:{tag}"})
            ac = parse_iso(a.get("created_at"))
            if harvard_cutoff and ac and ac <= harvard_cutoff:
                harvard_release_exact[sha].append({"doi": HARVARD_DOI, "basis": f"pre-cutoff GitHub Release asset:{tag}/{a.get('name')}"})

    # Hash exact repository bytes for current branch and the Harvard source commit.
    current_repo = current_repo_hash_index()
    harvard_repo = git_hash_index(HARVARD_SOURCE_COMMIT)

    # Core Zenodo current-version source commit is read from the checked-in recovery catalog when available.
    core_zenodo_repo = defaultdict(list)
    core_source_commit = None
    try:
        catalog = json.loads((ROOT / "preservation/recovery-catalog.json").read_text("utf-8"))
        # Search recursively for the current core source commit paired with the core concept DOI.
        def walk(x):
            nonlocal core_source_commit
            if isinstance(x, dict):
                vals = json.dumps(x, ensure_ascii=False)
                if ZENODO_CORE_CONCEPT_DOI in vals:
                    for k in ["source_commit", "commit", "git_commit", "source_git_commit"]:
                        v = x.get(k)
                        if isinstance(v, str) and re.fullmatch(r"[0-9a-f]{40}", v):
                            core_source_commit = v
                for v in x.values(): walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(catalog)
    except Exception:
        pass
    if core_source_commit:
        core_zenodo_repo = git_hash_index(core_source_commit)

    ar_links, ar_evidence = scan_repo_arweave_links(known_hashes)
    release_refs, release_doi_refs = scan_release_text_assets(releases, known_hashes)

    # Add Arweave links from release bodies/metadata assets when tx IDs are stated near a baseline SHA.
    for rel in releases:
        body = rel.get("body") or ""
        for sha in set(x.lower() for x in SHA256_RE.findall(body)) & known_hashes:
            for m in re.finditer(re.escape(sha), body, flags=re.IGNORECASE):
                ctx = body[max(0, m.start()-800):min(len(body), m.end()+800)]
                if "arweave" in ctx.lower() or "txid" in ctx.lower():
                    for tx in TX_RE.findall(ctx):
                        ar_links[sha].add(tx)
                        ar_evidence[sha].append({"release_tag": rel.get("tag_name"), "txids": [tx]})

    # Resolve native owner fingerprints. No actual wallet address is written to outputs.
    all_txs = sorted({tx for txs in ar_links.values() for tx in txs})
    owner_by_tx = {}
    for tx in all_txs:
        fp = arweave_owner_fingerprint(tx)
        if fp:
            owner_by_tx[tx] = fp
    current_fp = current_wallet_fingerprint()
    fp_times = defaultdict(list)
    for tx, fp in owner_by_tx.items():
        ts = fp.get("block_timestamp")
        if ts:
            fp_times[fp["address_sha256"]].append(int(ts))
    fp_order = sorted(fp_times, key=lambda x: min(fp_times[x]))
    labels = {}
    for fp in fp_order:
        if current_fp and fp == current_fp:
            labels[fp] = "new_current_wallet"
        else:
            labels[fp] = "old_or_service_owner"
    # If exactly one non-current native owner appears, it is the only defensible old-wallet candidate.
    non_current = [x for x in fp_order if x != current_fp]
    if len(non_current) == 1:
        labels[non_current[0]] = "old_wallet_candidate"

    results = []
    for r in baseline:
        sha = r["sha256"]
        txs = sorted(ar_links.get(sha, set()))
        groups = sorted({labels.get(owner_by_tx[t]["address_sha256"], "native_owner_unknown_role") for t in txs if t in owner_by_tx})
        refs = release_refs.get(sha, [])
        encrypted_refs = [x for x in refs if x.get("encrypted")]
        exact_release = release_exact.get(sha, [])
        exact_zenodo = list(zenodo_exact.get(sha, []))
        # Direct Zenodo DOI references discovered in metadata are not treated as exact unless an exact asset/annex contract establishes it.
        encrypted_zenodo_dois = sorted({d for d in release_doi_refs.get(sha, set()) if encrypted_refs})
        exact_harvard = list(harvard_release_exact.get(sha, []))
        if sha in harvard_repo:
            exact_harvard.append({"doi": HARVARD_DOI, "basis": "exact byte match in Harvard source Git commit", "repo_paths": harvard_repo[sha]})
        if sha in core_zenodo_repo:
            exact_zenodo.append({"doi": ZENODO_CORE_CONCEPT_DOI, "basis": "exact byte match in current core Zenodo source commit", "repo_paths": core_zenodo_repo[sha]})

        ar_old = False
        ar_new = False
        ar_unresolved = False
        for tx in txs:
            fp = owner_by_tx.get(tx)
            if not fp:
                ar_unresolved = True
                continue
            lab = labels.get(fp["address_sha256"], "")
            if lab == "new_current_wallet": ar_new = True
            elif lab == "old_wallet_candidate": ar_old = True
            else: ar_unresolved = True

        release_yes = bool(exact_release)
        zenodo_yes = bool(exact_zenodo)
        harvard_yes = bool(exact_harvard)
        ar_yes = bool(txs)
        domain_count = sum([release_yes, zenodo_yes, harvard_yes, ar_yes])
        location_count = int(release_yes) + int(zenodo_yes) + int(harvard_yes) + int(ar_old) + int(ar_new) + int(ar_unresolved and ar_yes)
        privacy = classify_privacy(r["path"])
        if domain_count == 0 and encrypted_refs:
            grade = "E1_encrypted_only"
        elif domain_count == 0:
            grade = "H0_hash_ots_only"
        elif domain_count == 1:
            grade = "S1_single_byte_domain"
        elif domain_count == 2:
            grade = "M2_multi_domain"
        else:
            grade = "D3_strong_multi_domain"

        action = "none"
        if domain_count == 0:
            if privacy in {"non_public", "sealed"}:
                action = "candidate_for_authenticated_encrypted_multi-domain_preservation"
            elif encrypted_refs:
                action = "verify_encrypted_copy_has_second_independent_durable_store"
            else:
                action = "review_and_preserve_original_bytes_if_material"
        elif domain_count == 1 and privacy in {"non_public", "sealed"}:
            action = "consider_second_independent_encrypted_or_institutional_copy"

        results.append({
            **r,
            "kind": classify_kind(r["path"]),
            "privacy": privacy,
            "manifest_ots_committed": True,
            "github_release_exact": release_yes,
            "github_release_matches": exact_release,
            "github_release_encrypted_reference": bool(encrypted_refs),
            "github_release_encrypted_refs": encrypted_refs,
            "arweave_exact_claim": ar_yes,
            "arweave_txids": txs,
            "arweave_old_wallet_candidate": ar_old,
            "arweave_new_current_wallet": ar_new,
            "arweave_owner_unresolved_or_service": ar_unresolved,
            "arweave_owner_groups": groups,
            "arweave_evidence": ar_evidence.get(sha, []),
            "zenodo_exact": zenodo_yes,
            "zenodo_matches": exact_zenodo,
            "zenodo_encrypted_reference_dois": encrypted_zenodo_dois,
            "harvard_v1_exact": harvard_yes,
            "harvard_matches": exact_harvard,
            "current_repo_exact": sha in current_repo,
            "current_repo_paths": current_repo.get(sha, []),
            "exact_byte_domain_count": domain_count,
            "exact_byte_location_count": location_count,
            "preservation_grade": grade,
            "recommended_action": action,
        })

    # Summary and high-value gaps.
    grade_counts = Counter(x["preservation_grade"] for x in results)
    privacy_counts = Counter(x["privacy"] for x in results)
    kind_counts = Counter(x["kind"] for x in results)
    gap_rows = [x for x in results if x["exact_byte_domain_count"] == 0]
    private_gaps = sorted([x for x in gap_rows if x["privacy"] in {"non_public", "sealed"}], key=lambda x: x["size"], reverse=True)
    star_moon = [x for x in results if "star_moon_witness" in x["kind"]]
    large_gaps = sorted(gap_rows, key=lambda x: x["size"], reverse=True)[:100]

    notary = build_notary_annex(releases, zenodo_state, harvard_cutoff)

    summary = {
        "schema": "trinityaccord.evidence-preservation-audit.v1",
        "generated_at": now_iso(),
        "baseline": {
            "file": str(BASELINE.relative_to(ROOT)),
            "rows": len(results),
            "unique_sha256": len({x["sha256"] for x in results}),
            "ots_committed": True,
            "note": "OTS commits the historical digest manifest; it does not itself preserve original bytes.",
        },
        "storage_domains": {
            "arweave": {"tx_links_found": len(all_txs), "native_owner_groups": len(fp_order), "current_wallet_fingerprint_present": bool(current_fp),
                        "owner_role_counts": Counter(labels.values()), "wallet_addresses_redacted": True},
            "zenodo": zenodo_state,
            "harvard": {"doi": HARVARD_DOI, "cutoff": harvard_cutoff.isoformat() if harvard_cutoff else None, "source_run": harvard_run, "live": harvard_state},
            "github_releases": {"release_count": len(releases), "exact_baseline_sha_matches": len(release_exact)},
        },
        "counts": {
            "grades": dict(grade_counts),
            "privacy": dict(privacy_counts),
            "kind": dict(kind_counts),
            "hash_ots_only_rows": len(gap_rows),
            "private_or_sealed_hash_only_rows": len(private_gaps),
            "rows_with_encrypted_release_reference": sum(bool(x["github_release_encrypted_reference"]) for x in results),
            "github_release_exact_rows": sum(bool(x["github_release_exact"]) for x in results),
            "arweave_claim_rows": sum(bool(x["arweave_exact_claim"]) for x in results),
            "zenodo_exact_rows": sum(bool(x["zenodo_exact"]) for x in results),
            "harvard_exact_rows": sum(bool(x["harvard_v1_exact"]) for x in results),
        },
        "star_moon_rows": star_moon,
        "largest_hash_only_rows": large_gaps,
        "largest_private_or_sealed_hash_only_rows": private_gaps[:100],
        "notary_annex": {
            "historical_baseline_member": False,
            "reason": "post-six-hash legal/notarial supplementary evidence",
            "public_release_assets": len(notary),
            "note": "Public/redacted assets are audited separately; no public full identity-bearing certificate is inferred.",
        },
        "limitations": [
            "Arweave exact coverage is conservative and requires a checked-in hash-to-TX/data-item association; gateway retrievability alone without hash binding is not counted.",
            "Native Arweave owner addresses are intentionally not emitted because record-chain/arweave-wallet-ledger.json sets public_address_allowed=false; only privacy-preserving fingerprints/roles are used.",
            "Harvard v1 coverage is frozen at its source workflow run; Release assets created after that cutoff are not inferred into v1.",
            "Encrypted derivatives are never counted as exact plaintext byte mirrors, even when they bind to a plaintext six-hash row.",
            "Zenodo external-evidence coverage is inferred only where the repository preservation contract explicitly guarantees byte-for-byte embedding of named Release assets, or where an exact repo-byte match is established for the core capsule.",
        ],
    }

    # Full JSON
    (OUT / "evidence-preservation-matrix.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str) + "\n", "utf-8")
    (OUT / "notary-supplement-annex.json").write_text(json.dumps(notary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (OUT / "arweave-owner-groups.json").write_text(json.dumps({
        "generated_at": now_iso(), "public_addresses_emitted": False, "current_wallet_address_sha256": current_fp,
        "groups": [{"address_sha256": fp, "role": labels.get(fp), "first_seen_block_timestamp": min(fp_times[fp]) if fp_times[fp] else None,
                    "tx_count": sum(1 for x in owner_by_tx.values() if x["address_sha256"] == fp)} for fp in fp_order],
        "unresolved_txids": [t for t in all_txs if t not in owner_by_tx],
    }, ensure_ascii=False, indent=2) + "\n", "utf-8")

    # Human-usable CSV: keep nested evidence compact.
    fields = [
        "manifest_line", "path", "size", "sha256", "sha3_256", "blake2b_256", "shake256_256", "sha512_256", "blake3_256",
        "kind", "privacy", "manifest_ots_committed", "github_release_exact", "github_release_encrypted_reference",
        "arweave_exact_claim", "arweave_old_wallet_candidate", "arweave_new_current_wallet", "arweave_owner_unresolved_or_service",
        "zenodo_exact", "harvard_v1_exact", "current_repo_exact", "exact_byte_domain_count", "exact_byte_location_count",
        "preservation_grade", "recommended_action", "github_release_tags", "arweave_txids_compact", "zenodo_dois", "harvard_basis",
    ]
    with (OUT / "evidence-preservation-matrix.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for x in results:
            row = {k: x.get(k) for k in fields}
            row["github_release_tags"] = ";".join(sorted({m["tag"] for m in x["github_release_matches"]} | {m["tag"] for m in x["github_release_encrypted_refs"]}))
            row["arweave_txids_compact"] = ";".join(x["arweave_txids"])
            row["zenodo_dois"] = ";".join(sorted({m.get("doi", "") for m in x["zenodo_matches"] if m.get("doi")} | set(x["zenodo_encrypted_reference_dois"])))
            row["harvard_basis"] = ";".join(m.get("basis", "") for m in x["harvard_matches"])
            w.writerow(row)

    with (OUT / "largest-gaps.csv").open("w", encoding="utf-8-sig", newline="") as f:
        fields2 = ["path", "size", "sha256", "kind", "privacy", "github_release_encrypted_reference", "preservation_grade", "recommended_action"]
        w = csv.DictWriter(f, fieldnames=fields2); w.writeheader()
        for x in large_gaps:
            w.writerow({k: x.get(k) for k in fields2})

    print(json.dumps({
        "rows": len(results),
        "grades": dict(grade_counts),
        "hash_ots_only_rows": len(gap_rows),
        "private_or_sealed_hash_only_rows": len(private_gaps),
        "release_exact_rows": sum(bool(x["github_release_exact"]) for x in results),
        "arweave_rows": sum(bool(x["arweave_exact_claim"]) for x in results),
        "zenodo_rows": sum(bool(x["zenodo_exact"]) for x in results),
        "harvard_rows": sum(bool(x["harvard_v1_exact"]) for x in results),
        "encrypted_reference_rows": sum(bool(x["github_release_encrypted_reference"]) for x in results),
        "output": str(OUT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
