#!/usr/bin/env python3
"""Read-only Epoch II inventory. No publishing, payload download or Canon changes.

Inventory success is not preservation completion. External large payloads remain
locator_only until a separate hash-bound capture and cold restore is performed.
Only Python's standard library is required.
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = "thechurchofagi/trinity-accord"
API = "https://api.github.com"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
CANON = {"97631551", "98369145", "98387475"}
PROGRAM_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
SOURCE_PATHS = [
    "api/final-evidence-inventory.v1.json", "nft-identity-index.json",
    "api/recovery-index.json", "preservation/recovery-catalog.json",
    "preservation/harvard-dataverse-state.json", "preservation/zenodo-state.json",
    "preservation/external-binary-annex-state.json",
    "archive/chronicle-sidechain-zenodo-state.json",
    "archive/chronicle-sidechain-finality-zenodo-state.json",
    "archive/encrypted-witness-archives.v1.json",
    "evidence/chronicle-sidechain-seven-root-provenance.json",
    "evidence/chronicle-sidechain-historical-payload-exceptions.json",
    "api/core-object-alpha-shenzhen-notary-2026-05-06.json",
    "api/gz2-notarial-certificate-redacted-attachments-2026-05-14.json",
    "evidence/notarial-certificate-2026-05-13/sealed-disc-custody-record.json",
    "archive/evidence/digest-manifest.json",
]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def log(message):
    print(f"[epoch-ii] {now()} {message}", flush=True)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def require(condition, message):
    if not condition:
        raise ValueError(message)


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old = urllib.parse.urlsplit(req.full_url)
        new = urllib.parse.urlsplit(newurl)
        arweave_sandbox = old.hostname == "arweave.net" and (new.hostname or "").endswith(".arweave.net") and not req.has_header("Authorization")
        require(new.scheme == "https" and (new.hostname == old.hostname or arweave_sandbox) and new.port in {None, 443}, "cross-host API redirect is not permitted")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Client:
    def __init__(self, capture, token="", replay=False):
        self.capture = capture
        self.token = token
        self.replay = replay

    def get(self, url, phase="sources", text_payload=False):
        host = urllib.parse.urlsplit(url).hostname
        require(host in {"api.github.com", "zenodo.org", "dataverse.harvard.edu", "arweave.net"}, "unexpected API host")
        key = hashlib.sha256(url.encode()).hexdigest()
        target = self.capture / phase / f"{key}.json"
        if self.replay:
            saved = json.loads(target.read_text())
            require(saved["url"] == url, "capture URL mismatch")
            require(saved["status"] == "ok", f"captured API failure: {url}")
            return saved["response"]
        headers = {"User-Agent": "TrinityAccord-EpochII-read-only/1", "Accept": "application/json"}
        if host == "api.github.com":
            headers["X-GitHub-Api-Version"] = "2022-11-28"
            if self.token:
                headers["Authorization"] = "Bearer " + self.token
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=headers, method="GET")
                opener = urllib.request.build_opener(SameHostRedirect())
                with opener.open(req, timeout=30) as response:
                    if text_payload:
                        raw = response.read(4097)
                        require(len(raw) <= 4096, "public notice exceeds bounded text size")
                        value = {"text": raw.decode("utf-8"), "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}
                    else:
                        value = json.load(response)
                    effective_url = response.geturl()
                write_json(target, {"url": url, "effective_url": effective_url, "observed_at_utc": now(), "status": "ok", "response": value})
                return value
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                if isinstance(exc, urllib.error.HTTPError) and exc.code in {401, 403, 404, 429}:
                    break
                if attempt < 2:
                    time.sleep(attempt + 1)
        write_json(target, {"url": url, "observed_at_utc": now(), "status": "unavailable"})
        raise RuntimeError(f"API unavailable: {url}")


def paginated(client, path, phase):
    rows, seen = [], set()
    for page in range(1, 1001):
        result = client.get(f"{API}/repos/{REPO}/{path}?per_page=100&page={page}", phase)
        require(isinstance(result, list), f"non-list pagination: {path}")
        for item in result:
            require(isinstance(item, dict) and isinstance(item.get("id"), int), "invalid paginated item")
            require(item["id"] not in seen, f"duplicate item during pagination: {path}")
            seen.add(item["id"])
            rows.append(item)
        if len(result) < 100:
            return sorted(rows, key=lambda x: x["id"])
    raise ValueError("pagination limit exceeded without a terminal page")


def release_signature(rows):
    return [(r["id"], r["tag_name"], r["draft"], r["prerelease"], r["published_at"], r.get("body")) for r in rows]


def asset_signature(rows):
    return [(x["id"], x["name"], x["size"], x.get("digest"), x.get("updated_at"), x.get("state")) for x in rows]


def release_census(client, phase):
    releases = paginated(client, "releases", phase)
    log(f"{phase}: releases={len(releases)}; enumerating each asset endpoint")
    require(all(not x["draft"] for x in releases), "public census unexpectedly includes a draft")
    def collect(release):
        return release["id"], paginated(client, f"releases/{release['id']}/assets", phase)
    assets = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for index, (rid, items) in enumerate(pool.map(collect, releases), 1):
            assets[rid] = items
            if index % 10 == 0 or index == len(releases):
                log(f"{phase}: asset lists {index}/{len(releases)}")
    return releases, assets


def stable_census(before, after):
    require(release_signature(before[0]) == release_signature(after[0]), "release set changed during capture")
    for rid in before[1]:
        require(asset_signature(before[1][rid]) == asset_signature(after[1][rid]), f"release assets changed: {rid}")


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def hash_source_tree(root, sha):
    entries = git(root, "ls-tree", "-rz", "--full-tree", sha).split(b"\0")
    proc = subprocess.Popen(["git", "-C", str(root), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    objects, rows = {}, []
    try:
        for index, entry in enumerate(filter(None, entries), 1):
            meta, raw_path = entry.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            path = raw_path.decode("utf-8")
            require(kind == "blob", f"unresolved non-blob Git entry: {path}")
            if oid not in objects:
                proc.stdin.write(oid.encode() + b"\n")
                proc.stdin.flush()
                header = proc.stdout.readline().decode().strip().split()
                require(len(header) == 3 and header[:2] == [oid, "blob"], "Git object unavailable")
                size = remaining = int(header[2])
                digest = hashlib.sha256()
                identity = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
                while remaining:
                    chunk = proc.stdout.read(min(1024 * 1024, remaining))
                    require(chunk, "truncated Git object")
                    digest.update(chunk)
                    identity.update(chunk)
                    remaining -= len(chunk)
                require(proc.stdout.read(1) == b"\n" and identity.hexdigest() == oid, "Git blob identity mismatch")
                objects[oid] = (digest.hexdigest(), size)
            digest, size = objects[oid]
            rows.append({"object_id": "git:" + path, "path": path, "git_mode": mode, "git_blob_oid": oid,
                         "content_sha256": digest, "size_bytes": size, "capture": "bytes_verified_in_source_git",
                         "candidate_payload_present": False, "verification": "verified_this_run"})
            if index % 500 == 0:
                log(f"source bytes hashed: {index}")
    finally:
        proc.stdin.close()
        proc.stdout.close()
        proc.wait()
    return rows


def validate_sets(inventory, nft, provenance):
    btc = inventory["evidence_sets"]["bitcoin_inscriptions"]["items"]
    require(len(btc) == len({r["txid"] for r in btc}) == 12, "Bitcoin identity set is not 12 unique records")
    require({str(r["inscription_number"]) for r in btc if r["classification"] == "canonical_original"} == CANON, "Canon changed")
    require(collections.Counter(r["classification"] for r in btc) == {"pre_canonical_formation": 4, "canonical_original": 3, "non_amending_ancillary": 5}, "Bitcoin historical classes changed")
    assets = nft["assets"]
    require(len(assets) == len({a["asset_id"] for a in assets}) == 175, "NFT identity set is not 175 unique records")
    require(len({a["contract_address"] for a in assets}) == 4, "NFT contract set changed")
    refs = []
    for a in assets:
        for role, ref in [("metadata", a["content"]["metadata"]), *[("media", r) for r in a["content"]["media"]]]:
            require(HEX64.fullmatch(ref.get("car_sha256", "")), "missing/invalid CAR SHA-256")
            require(ref.get("root_cid") and ref.get("arweave_txid"), "missing NFT content locator")
            refs.append({"asset_id": a["asset_id"], "role": role, "container_sha256": ref["car_sha256"],
                         "container_size_bytes": ref["car_size"], "member_path": ref.get("leaf_path"),
                         "root_cid": ref["root_cid"], "arweave_txid": ref["arweave_txid"],
                         "content_sha256": None, "capture": "locator_only", "verification": "not_run"})
    scope = provenance["scope"]
    require(scope["declared_historical_roots"] == scope["externally_delivered_not_self_minted"] == 7, "external root scope mismatch")
    require(scope["project_content_gap_count"] == 0 and scope["payload_recovery_claimed"] is False, "external bytes recovery or gap misclaimed")
    require(len(provenance["items"]) == 7, "external root rows missing")
    items = provenance["items"]
    require(len({i["root_cid"] for i in items}) == len({i["asset_id"] for i in items}) == 7, "duplicate external root or asset")
    target = scope["target_address"].lower()
    official = {a["contract_address"].lower() for a in assets}
    for item in items:
        require(item["transfer_to"].lower() == target, "external item is not inbound to target")
        require(item["transaction_initiator"].lower() != target and item["transfer_from"].lower() != target, "external item was target initiated")
        require(item["contract"].lower() not in official, "external item uses project contract")
        require(item["classification"] == "externally_delivered_not_self_minted", "external classification changed")
    require(sum(i["transfer_from"] == "0x" + "0" * 40 for i in items) == 2, "external zero mint count changed")
    return btc, refs


def classify_release(tag, current_museum):
    if tag.startswith("museum-"):
        return ("presentation_current", "proposed_required") if tag == current_museum else ("presentation_history", "optional_history")
    if tag.startswith("bitcoin-consensus-checkpoint-"):
        return "bitcoin_operational_checkpoint", "review_recovery_dependency"
    if "encrypted-archive" in tag:
        return "encrypted_witness_ciphertext", "proposed_required_ciphertext_only"
    if "finality" in tag:
        return "sidechain_finality", "proposed_required"
    if any(x in tag for x in ["notar", "flaw", "ots", "nft", "signed-large", "large-assets", "sidechain", "settlement"]):
        return "evidence_or_content", "proposed_required"
    if tag.startswith("ta-tr-"):
        return "research_context", "optional_context"
    return "historical_release", "review_required"


def release_rows(releases, by_release):
    versions = [r["tag_name"] for r in releases if re.fullmatch(r"museum-v\d+\.\d+\.\d+", r["tag_name"])]
    current = max(versions, key=lambda s: tuple(map(int, s.split("-v")[1].split("."))), default=None)
    out = []
    for r in releases:
        family, scope = classify_release(r["tag_name"], current)
        for a in by_release[r["id"]]:
            require(isinstance(a["size"], int) and a["size"] >= 0, "invalid asset size")
            require(a["state"] == "uploaded", "asset not uploaded")
            supplied = a.get("digest") or ""
            digest = supplied[7:] if supplied.startswith("sha256:") and HEX64.fullmatch(supplied[7:]) else None
            out.append({"object_id": f"github-asset:{a['id']}", "release_id": r["id"], "release_tag": r["tag_name"],
                        "asset_id": a["id"], "filename": a["name"], "source_locator": a["browser_download_url"],
                        "size_bytes": a["size"], "declared_sha256": digest, "declared_digest_raw": supplied,
                        "digest_basis": "github_api_not_recomputed", "updated_at": a["updated_at"],
                        "family": family, "scope": scope, "access": "public_ciphertext" if "ciphertext" in family else "public",
                        "capture": "locator_only", "verification": "not_run"})
    require(len(out) == len({a["asset_id"] for a in out}), "duplicate asset identity")
    return out


def capacity(rows):
    known, unknown, families = {}, [], collections.defaultdict(lambda: {"assets": 0, "logical_bytes": 0})
    for r in rows:
        families[r["family"]]["assets"] += 1
        families[r["family"]]["logical_bytes"] += r["size_bytes"]
        h = r["declared_sha256"]
        if not h:
            unknown.append(r)
        else:
            require(h not in known or known[h] == r["size_bytes"], "same declared SHA-256 has conflicting sizes")
            known[h] = r["size_bytes"]
    return {"logical_bytes": sum(r["size_bytes"] for r in rows), "assets": len(rows),
            "known_hash_groups": len(known), "assets_missing_declared_sha256": len(unknown),
            "api_digest_deduplicated_planning_bytes": sum(known.values()) + sum(r["size_bytes"] for r in unknown),
            "deduplication_is_byte_verified": False, "families": dict(families)}


def find_dois(value):
    found = set()
    if isinstance(value, dict):
        for v in value.values():
            found.update(find_dois(v))
    elif isinstance(value, list):
        for v in value:
            found.update(find_dois(v))
    elif isinstance(value, str):
        found.update(re.findall(r"10\.5281/zenodo\.\d+", value))
    return found


def doi_census(client, sources):
    identifiers = sorted(set().union(*(find_dois(v) for v in sources.values())))
    def one(doi):
        try:
            d = client.get("https://zenodo.org/api/records/" + doi.rsplit(".", 1)[1])
            require(isinstance(d.get("files"), list), "Zenodo files list missing")
            return {"requested_doi": doi, "resolved_doi": d.get("doi"), "record_id": d["id"],
                    "metadata_status": "observed", "is_alias_to_resolved_record": doi != d.get("doi"), "bytes_readback_this_run": False,
                    "files": [{"filename": f["key"], "size_bytes": f["size"], "declared_checksum": f.get("checksum"),
                               "source_locator": f.get("links", {}).get("self"), "capture": "locator_only"} for f in d["files"]]}
        except (RuntimeError, ValueError, KeyError, OSError) as exc:
            return {"requested_doi": doi, "metadata_status": "unavailable", "bytes_readback_this_run": False,
                    "error_type": type(exc).__name__}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(one, identifiers))
    log(f"Zenodo metadata records={len(rows)} available={sum(x['metadata_status']=='observed' for x in rows)}")
    try:
        raw = client.get("https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/YUCG12")
        require(raw.get("status") == "OK", "Harvard API did not return OK")
        harvard = {"doi": "10.7910/DVN/YUCG12", "metadata_status": "observed", "response": raw, "bytes_readback_this_run": False}
    except (RuntimeError, ValueError, OSError):
        harvard = {"doi": "10.7910/DVN/YUCG12", "metadata_status": "unavailable", "bytes_readback_this_run": False}
    return rows, harvard


def inspect_harvard_metadata(observation, frozen):
    if observation["metadata_status"] != "observed":
        return {"status": "unavailable", "public_payload_readback_this_run": False}
    dataset = observation["response"]["data"]
    version = dataset["latestVersion"]
    rows = [{"file_id": f["dataFile"]["id"], "filename": f["dataFile"]["filename"],
             "size_bytes": f["dataFile"]["filesize"], "declared_checksum": f["dataFile"].get("checksum"),
             "restricted": bool(f.get("restricted"))} for f in version["files"]]
    match = [r for r in rows if r["file_id"] == frozen["archive_file_id"]]
    require(len(match) == 1, "Harvard original frozen archive missing or duplicated")
    archive = match[0]
    require(archive["size_bytes"] == frozen["source"]["artifact_bytes"], "Harvard frozen archive size changed")
    checksum = archive["declared_checksum"] or {}
    require(checksum.get("type") == "SHA-256" and checksum.get("value") == frozen["source"]["artifact_sha256"], "Harvard archive metadata SHA-256 changed")
    terms = version.get("termsOfUse") or ""
    license_value = version.get("license")
    terms_complete = bool(license_value) or bool(terms.strip())
    return {"status": "metadata_matches_frozen_archive", "version_state": version["versionState"],
            "version_number": version.get("versionNumber"), "version_minor_number": version.get("versionMinorNumber"),
            "locks": dataset.get("locks", []), "file_count": len(rows), "files": rows,
            "license_or_custom_terms_present": terms_complete, "terms_of_use_nonempty": bool(terms.strip()),
            "archive_declared_sha256_matches": True, "public_payload_readback_this_run": False,
            "automatic_modification_allowed": False, "automatic_resubmission_allowed": False,
            "institutional_submission_ready": False}


def physical_census(client, source):
    index_url = source["arweave"]["index_json"]["url"]
    manifest_txid = source["arweave"].get("manifest_txid")
    manifest_url = "https://arweave.net/raw/" + manifest_txid if manifest_txid else source["arweave"]["manifest_url"]
    index, path_manifest = client.get(index_url), client.get(manifest_url)
    entries = index["files"]
    require(len(entries) == index["fileCount"] == source["arweave"]["uploaded_file_count"], "physical index count changed")
    require(len({r["path"] for r in entries}) == len(entries), "duplicate physical path")
    result, notices = [], []
    for row in entries:
        require(HEX64.fullmatch(row["sha256"]) and isinstance(row["size"], int), "physical file identity missing")
        require(path_manifest["paths"][row["path"]]["id"] == row["txid"], "physical index / path-manifest mismatch")
        require(re.fullmatch(r"[A-Za-z0-9_-]{43}", row["txid"]), "invalid physical TXID")
        path = row["path"]
        role = "recorded_video" if path.lower().endswith((".avi", ".mp4")) else "public_evidence_file"
        entry = {"object_id": "physical:2026-05-06:" + path, "logical_path": path,
                 "declared_sha256": row["sha256"], "size_bytes": row["size"], "arweave_txid": row["txid"],
                 "source_locator": "https://arweave.net/" + row["txid"], "role": role,
                 "capture": "locator_only", "verification": "not_run"}
        if path.endswith(".avi.txt"):
            notice = client.get(entry["source_locator"], text_payload=True)
            require(notice["sha256"] == row["sha256"] and notice["size_bytes"] == row["size"], "physical private-evidence notice bytes mismatch")
            require("非公开证据" in notice["text"] and "物理介质" in notice["text"], "notice does not declare private physical custody")
            entry.update(role="public_notice_for_nonpublic_original", capture="small_notice_bytes_verified", verification="verified_this_run", notice=notice)
            notices.append({"original_path": path[:-4], "scope": "nonpublic_physical_custody", "original_bytes_read": False,
                            "public_notice_txid": row["txid"], "public_notice_sha256": row["sha256"]})
        result.append(entry)
    return {"status": "file_metadata_expanded", "index_url": index_url, "path_manifest_url": manifest_url,
            "public_files": len(result), "logical_bytes": sum(r["size_bytes"] for r in result),
            "public_video_files": sum(r["role"] == "recorded_video" for r in result),
            "private_original_notices": notices, "files": result,
            "full_payload_readback_this_run": False}


def digest_crosswalk(digests, source_rows, releases, physical):
    local, remote = collections.defaultdict(list), collections.defaultdict(list)
    for r in source_rows:
        local[r["content_sha256"]].append(r["path"])
    for r in releases:
        if r["declared_sha256"]:
            remote[r["declared_sha256"]].append(r["object_id"])
    for r in physical["files"]:
        remote[r["declared_sha256"]].append(r["object_id"])
    rows = []
    for index, item in enumerate(digests["items"]):
        require(HEX64.fullmatch(item["sha256"]), "invalid historical digest")
        sha = item["sha256"]
        restricted = "不公开" in item["path"]
        rows.append({"object_id": f"historical-digest:{index}", "historical_path": item["path"],
                     "declared_sha256": sha, "size_bytes": item["size_bytes"], "historical_status": item.get("status"),
                     "historical_nonpublic_label": restricted, "matching_current_source_paths": local[sha],
                     "matching_public_asset_metadata": remote[sha],
                     "capture": "source_bytes_match" if local[sha] else "public_locator_only" if remote[sha] else "commitment_only",
                     "access_review": "preserve_restriction_history" if restricted else "scope_review",
                     "new_payload_disclosure_authorized": False})
    return {"rows": rows, "summary": dict(collections.Counter(r["capture"] for r in rows)),
            "boundary": "Unmatched commitments are not automatically missing project files: expand preserved container members and review protected scope first."}


def copy_canonical_bodies(root, sha, btc, source_rows, out):
    copied = []
    for item in btc:
        if item["classification"] != "canonical_original":
            continue
        candidates = [r for r in source_rows if r["content_sha256"] == item["body_sha256"]]
        require(candidates, f"canonical body bytes absent from source: {item['inscription_number']}")
        source = candidates[0]["path"]
        raw = git(root, "show", f"{sha}:{source}")
        require(hashlib.sha256(raw).hexdigest() == item["body_sha256"], "canonical body copy changed")
        destination = out / "canon" / (item["inscription_number"] + ".txt")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        copied.append({"inscription_number": item["inscription_number"], "inscription_id": item["derived_inscription_id"],
                       "source_path": source, "audit_copy_path": destination.relative_to(out).as_posix(),
                       "sha256": item["body_sha256"], "size_bytes": len(raw), "verification": "exact_source_copy_against_pinned_inventory"})
    require(len(copied) == 3, "canonical body copy set incomplete")
    return copied


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repository-root", type=Path, default=Path("."))
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--capture-dir", type=Path, required=True)
    p.add_argument("--replay", action="store_true", help="Replay captured API metadata without contacting services")
    args = p.parse_args()
    root, out = args.repository_root.resolve(), args.output_dir.resolve()
    require(not out.exists() or not any(out.iterdir()), "output directory must be new or empty")
    out.mkdir(parents=True, exist_ok=True)
    sha = git(root, "rev-parse", "HEAD").decode().strip()
    require(re.fullmatch(r"[0-9a-f]{40}", sha), "invalid source SHA")
    started = now()
    client = Client(args.capture_dir.resolve(), os.environ.get("GITHUB_TOKEN", ""), args.replay)
    log(f"fixed source={sha}; metadata audit only; no external mutation")
    source_rows = hash_source_tree(root, sha)
    source_map = {r["path"]: r for r in source_rows}
    sources = {path: json.loads(git(root, "show", f"{sha}:{path}")) for path in SOURCE_PATHS}
    btc, nft_refs = validate_sets(sources[SOURCE_PATHS[0]], sources["nft-identity-index.json"], sources["evidence/chronicle-sidechain-seven-root-provenance.json"])
    canonical_copies = copy_canonical_bodies(root, sha, btc, source_rows, out)
    write_json(out / "CANON-EXACT-COPY-REPORT.json", canonical_copies)
    write_json(out / "SOURCE-FILES.json", source_rows)
    write_json(out / "NFT-IDENTITY-INDEX.json", sources["nft-identity-index.json"])
    write_json(out / "NFT-CONTENT-REFERENCES.json", nft_refs)
    write_json(out / "BITCOIN-IDENTITIES.json", btc)
    write_json(out / "EXTERNAL-ROOT-SCOPE.json", sources["evidence/chronicle-sidechain-seven-root-provenance.json"])
    # Snapshot source documents only. Original protected material is never discovered or decoded.
    for path, value in sources.items():
        write_json(out / "source-records" / path, {"original_source_sha256": source_map[path]["content_sha256"],
                                                  "note": "Parsed source record; this wrapper is not the original file bytes.", "record": value})
    before = release_census(client, "before")
    dois, harvard = doi_census(client, sources)
    harvard_check = inspect_harvard_metadata(harvard, sources["preservation/harvard-dataverse-state.json"])
    physical = physical_census(client, sources["api/core-object-alpha-shenzhen-notary-2026-05-06.json"])
    after = release_census(client, "after")
    stable_census(before, after)
    releases = release_rows(*after)
    cap = capacity(releases)
    crosswalk = digest_crosswalk(sources["archive/evidence/digest-manifest.json"], source_rows, releases, physical)
    write_json(out / "PHYSICAL-EVIDENCE-FILES.json", physical)
    write_json(out / "HISTORICAL-DIGEST-CROSSWALK.json", crosswalk)
    write_json(out / "RELEASE-ASSETS.json", releases)
    write_json(out / "DOI-RECORDS.json", dois)
    write_json(out / "HARVARD-OBSERVATION.json", harvard)
    write_json(out / "HARVARD-FROZEN-BASELINE-CHECK.json", harvard_check)
    gaps = [
        {"id": "external-payload-capture", "status": "not_run", "blocks_content_candidate": True,
         "detail": "Release, DOI and NFT references were enumerated; their payload bytes were not downloaded by this audit."},
        {"id": "physical-payload-capture", "status": "metadata_expanded_payloads_not_captured", "blocks_content_candidate": True,
         "detail": "The 153-file public index is cross-bound to its Arweave path manifest. Three public videos and one private-original notice are distinct. Full payload download remains outstanding."},
        {"id": "historical-container-expansion", "status": "crosswalk_created_container_members_pending", "blocks_content_candidate": True,
         "detail": "The 884-row historical digest inventory is mapped to current source hashes and public asset metadata. Unmatched rows require container-member and access-scope review, not an automatic missing-file claim."},
        {"id": "physical-correspondence", "status": "unresolved", "blocks_content_candidate": False,
         "detail": "Preserve source differences in material description, inscription coordinate and document transcription; no forensic identity claim."},
        {"id": "sealed-and-confidential", "status": "intentionally_restricted", "blocks_content_candidate": False,
         "detail": "Ciphertext and public custody/commitment records only. Do not open sealed discs or discover/publish unlock material."},
        {"id": "all-release-scope-selection", "status": "proposed_not_final", "blocks_content_candidate": True,
         "detail": "Older museum editions and operational checkpoints remain in the census; select payload scope using dependency closure."},
        {"id": "cold-restore", "status": "not_run", "blocks_content_candidate": True,
         "detail": "The metadata audit must not be presented as an Epoch II content recovery or publication PASS."},
        {"id": "harvard-live-metadata", "status": harvard["metadata_status"], "blocks_content_candidate": False,
         "detail": "Historical public readback record is preserved separately from this observation."},
    ]
    coverage = {"schema": "trinityaccord.epoch-ii-coverage.v1", "source_commit_sha": sha,
                "audit_status": "metadata_census_complete" if all(d["metadata_status"] == "observed" for d in dois) and harvard["metadata_status"] == "observed" else "metadata_census_with_unavailable_sources",
                "candidate_content_complete": False, "harvard_mutated": False, "release_assets_stable_across_two_complete_enumerations": True,
                "source_files_verified": len(source_rows), "source_logical_bytes": sum(r["size_bytes"] for r in source_rows),
                "bitcoin_identities": len(btc), "canonical_originals": 3, "nft_identities": 175,
                "canonical_body_copies_verified_against_source_inventory": len(canonical_copies),
                "nft_content_references": len(nft_refs), "nft_references_with_container_digest": len(nft_refs),
                "nft_leaf_bytes_verified_this_run": 0, "releases_enumerated": len(after[0]), "release_capacity": cap,
                "physical_public_files": physical["public_files"], "physical_public_video_files": physical["public_video_files"],
                "physical_private_original_notice_count": len(physical["private_original_notices"]),
                "historical_digest_rows": len(crosswalk["rows"]), "historical_digest_crosswalk": crosswalk["summary"],
                "zenodo_identifiers_enumerated": len(dois), "zenodo_unique_resolved_records": len({d['record_id'] for d in dois if d['metadata_status'] == 'observed'}),
                "zenodo_records_unavailable": sum(d["metadata_status"] != "observed" for d in dois), "harvard_frozen_baseline_metadata_check": harvard_check,
                "external_payload_bytes_verified_this_run": sum(r["size_bytes"] for r in physical["files"] if r["capture"] == "small_notice_bytes_verified"),
                "external_large_payload_bytes_verified_this_run": 0, "epoch_ii_required_payload_denominator": None,
                "raw_wallet_payload_recovery": {"verified_historically": 250, "observed": 257, "unavailable_external": 7},
                "project_gap_attributable_to_seven_external_roots": 0, "gaps": gaps}
    write_json(out / "COVERAGE-REPORT.json", coverage)
    manifest = {"schema": "trinityaccord.preservation-epoch-ii-inventory.v1", "source_commit_sha": sha,
                "audit_program_sha256": PROGRAM_SHA256,
                "started_at_utc": started, "completed_at_utc": now(), "authority": "three Bitcoin Originals only",
                "role": "non_amending_prepublication_metadata_audit", "candidate_payload_present": False,
                "source_records": [{"path": path, "source_sha256": source_map[path]["content_sha256"]} for path in SOURCE_PATHS],
                "coverage": coverage, "input_capture_mode": "replay" if args.replay else "live_get_only"}
    write_json(out / "DATASET-MANIFEST.json", manifest)
    lines = ["# Epoch II candidate inventory audit", "", f"Source: `{sha}`.", "",
             "This is a read-only metadata census, not a completed preservation bundle. Bitcoin Originals remain authoritative.", "",
             "| Item | Result |", "|---|---:|", f"| Source files hashed | {len(source_rows)} |",
             f"| Public Releases | {len(after[0])} |", f"| Release assets | {len(releases)} |",
             f"| Release logical bytes | {cap['logical_bytes']} |",
             f"| API-digest deduplicated planning bytes (not byte-verified) | {cap['api_digest_deduplicated_planning_bytes']} |",
             f"| Assets missing declared SHA-256 | {cap['assets_missing_declared_sha256']} |",
             f"| NFT identities / content references | 175 / {len(nft_refs)} |",
             f"| Public custody-notice bytes verified this run | {coverage['external_payload_bytes_verified_this_run']} |",
             "| External large-payload bytes verified this run | 0 |", "",
             "## Release families", "", "| Family | Assets | Logical bytes |", "|---|---:|---:|"]
    for family, counts in sorted(cap["families"].items()):
        lines.append(f"| {family} | {counts['assets']} | {counts['logical_bytes']} |")
    lines.extend(["", "## Remaining work", ""] + [f"- {g['id']}: {g['status']}. {g['detail']}" for g in gaps])
    (out / "COVERAGE-REPORT.md").write_text("\n".join(lines) + "\n")
    (out / "START-HERE.md").write_text("# Trinity Accord Preservation Epoch II research inventory\n\nThis inventory describes fixed, citable research artifacts documenting a human-led, generative-AI-assisted archival and creative project. The data consist of original texts, creative works, machine-readable identities, provenance records, verification software and recorded preservation observations. Researchers can inspect how the project developed and independently test specific byte, identity and evidence relationships.\n\nGenerative AI participated in project content and assists the creation of this inventory and audit software. The human project initiator and guardian remains responsible for scope, source attribution, rights review and institutional submission decisions; AI outputs are not independent institutional attestations.\n\nStart with COVERAGE-REPORT.md. DATASET-MANIFEST.json binds the source version and audit program. SOURCE-FILES.json records source-byte hashes; RELEASE-ASSETS.json and DOI-RECORDS.json enumerate remote metadata. NFT-CONTENT-REFERENCES.json distinguishes CAR digests from leaf bytes. See SOFTWARE-REVIEW-GUIDE.md and HARVARD-REVIEW-CONSTRAINTS.md for review and submission boundaries.\n\nThis is the metadata stage of the research corpus, not the completed content deposit. The three Bitcoin Originals remain authoritative.\n")
    (out / "HARVARD-REVIEW-CONSTRAINTS.md").write_text("# Institutional review constraints\n\nBasis: owner-supplied instructions from the Sonia Barbosa correspondence, Ticket 423683; this audit did not independently retrieve that email thread.\n\n- Describe fixed, citable, independently inspectable research data positively. Disclose AI participation and human responsibility.\n- Supply exact-commit source, README, a review guide, CITATION.cff, dependency files, Git tree, provenance manifest and SHA-256 before a submission is considered ready.\n- License, Custom Terms and Terms of Use must be complete and consistent. Selecting custom terms with an empty body must block submission. This audit grants no new license.\n- Keep the frozen Harvard v1.0 DOI, original archive bytes, size and SHA-256 unchanged. This workflow creates no v1.1 or new DOI.\n- InReview forbids automated modifications, resubmission or repeated submit-for-review calls. Sonia's recorded arrangement is direct publication by the curator upon approval without resubmission. A return to draft is not automatically a rejection or permission to resubmit.\n- After publication, independently read the public file list and original downloads and recompute size and SHA-256. Preserve that new receipt outside the frozen dataset.\n")
    (out / "SOFTWARE-REVIEW-GUIDE.md").write_text(f"# Reviewable research software\n\nSource commit: {sha}\nAudit program SHA-256: {manifest['audit_program_sha256']}\n\nThe audit uses Python 3 standard library and Git. SOURCE-FILES.json preserves the complete source tree, file modes, blob identities, SHA-256 and sizes. The source capsule must be built from this exact safe commit using the existing repository preservation builder before institutional submission; this metadata output does not include the full source ZIP. Preserve the root README.md, CITATION.cff, package.json, package-lock.json and relevant requirements files with that capsule.\n\nRun scripts/audit_preservation_epoch_ii.py with --repository-root, --output-dir and --capture-dir. Use --replay for captured API metadata. A successful audit means the enumerations and source identities were checked, not that external payload bytes or all cryptographic proofs were verified. Review rights separately; no new blanket software or content license is granted.\n")
    (out / "LIMITATIONS-AND-EXCLUSIONS.md").write_text("# Limitations and exclusions\n\n" + "\n".join(f"- {g['id']}: {g['detail']}" for g in gaps) + "\n\nHistorical verification claims remain source reports. Ethereum proofs retain weak subjectivity. Hashes do not establish philosophical truth or physical identity. Public encrypted witnesses do not authorize plaintext or key disclosure. A successful metadata audit does not permit Harvard publication.\n")
    sums = [f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(out).as_posix()}" for f in sorted(out.rglob("*")) if f.is_file() and f.name != "SHA256SUMS"]
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    log(f"audit complete: releases={len(after[0])} assets={len(releases)} logical_bytes={cap['logical_bytes']} content_candidate=NOT_BUILT")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, KeyError) as exc:
        log(f"AUDIT FAILED CLOSED: {type(exc).__name__}: {exc}")
        raise SystemExit(1)
