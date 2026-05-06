#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ARCHIVE_ID = "core-object-alpha-shenzhen-notary-2026-05-06"
RELEASE_TAG = "core-object-alpha-shenzhen-notary-arweave-backup-v1"

INDEX_JSON_URL = "https://arweave.net/7jx4hMydXh7jXv-3WdAgFJDriZeT4e1IPfAJB_zMYT4"
INDEX_TSV_URL = "https://arweave.net/sWXq28jv1DrqUb388Q-HMEiEWDA234mZxXOrnHKXMxM"
INDEX_HTML_URL = "https://arweave.net/CfzH1KeWePNoR9ZFNgBuXI2keBmX8vIb_0Z8oMN-gdE"
ARWEAVE_MANIFEST_URL = "https://arweave.net/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE"
ARWEAVE_MANIFEST_RAW_URL = "https://arweave.net/raw/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE"

MANIFEST_TXID = "_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE"
OTS_BLOCK = 948161
EXPECTED_FILE_COUNT = 153
EXPECTED_CHECKED_TX_COUNT = 157
EXPECTED_CONFIRMED_OK = 157

PAYLOAD_ZIP_NAME = f"{ARCHIVE_ID}-arweave-payload.zip"
BACKUP_MANIFEST_NAME = f"{ARCHIVE_ID}-github-release-backup-manifest.json"
ASSET_SHA256_NAME = f"{ARCHIVE_ID}-release-assets.sha256"
RELEASE_NOTES_NAME = f"{ARCHIVE_ID}-release-notes.md"
PAYLOAD_SHA256_NAME = "payload-files.sha256"

def log(msg):
    print(msg, flush=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

def fetch_bytes(url, tries=5, delay=3):
    last = None
    for i in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-github-release-backup/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                status = getattr(r, "status", 200)
                data = r.read()
                if status != 200:
                    raise RuntimeError(f"HTTP {status}")
                return data
        except Exception as e:
            last = e
            log(f"FETCH RETRY {i}/{tries}: {url} :: {e}")
            if i < tries:
                time.sleep(delay * i)
    raise RuntimeError(f"Failed to fetch {url}: {last}")

def safe_rel_path(rel):
    rel = str(rel).replace("\\", "/").lstrip("/")
    if not rel or rel.startswith("../") or "/../" in rel or rel == "..":
        raise ValueError(f"Unsafe relative path: {rel!r}")
    return rel

def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def make_zip(src_dir, zip_path):
    if zip_path.exists():
        zip_path.unlink()
    files = sorted([p for p in src_dir.rglob("*") if p.is_file()])
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            arc = p.relative_to(src_dir).as_posix()
            z.write(p, arc)
    return zip_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist/shenzhen-notary-github-release-backup")
    ap.add_argument("--skip-payload", action="store_true", help="Fetch index files and build metadata only; for smoke tests.")
    args = ap.parse_args()

    out = Path(args.out)
    work = out / "work"
    release_dir = out / "release-assets"

    if work.exists():
        shutil.rmtree(work)
    if release_dir.exists():
        shutil.rmtree(release_dir)

    work.mkdir(parents=True, exist_ok=True)
    release_dir.mkdir(parents=True, exist_ok=True)

    log("Fetching archive-index.json")
    index_bytes = fetch_bytes(INDEX_JSON_URL)
    index = json.loads(index_bytes.decode("utf-8"))

    files = index.get("files", [])
    if len(files) != EXPECTED_FILE_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_FILE_COUNT} files, got {len(files)}")

    if "Trinity Accord" not in index.get("archiveName", ""):
        raise RuntimeError("archiveName does not contain Trinity Accord")

    indices_dir = work / "indices"
    payload_dir = work / "payload"
    metadata_dir = work / "metadata"

    write_bytes(indices_dir / "archive-index.json", index_bytes)
    write_bytes(indices_dir / "archive-index.tsv", fetch_bytes(INDEX_TSV_URL))
    write_bytes(indices_dir / "index.html", fetch_bytes(INDEX_HTML_URL))

    raw_manifest_bytes = fetch_bytes(ARWEAVE_MANIFEST_RAW_URL)
    raw_manifest = json.loads(raw_manifest_bytes.decode("utf-8"))
    if raw_manifest.get("manifest") != "arweave/paths":
        raise RuntimeError("raw arweave manifest does not have manifest=arweave/paths")
    write_bytes(indices_dir / "arweave-manifest.json", raw_manifest_bytes)

    downloaded = []
    hard_failures = []
    payload_sha_lines = []

    if args.skip_payload:
        log("Skipping payload downloads by request.")
    else:
        for idx, row in enumerate(files, start=1):
            rel = safe_rel_path(row["path"])
            expected_sha = row["sha256"]
            url = row["url"]
            expected_size = int(row.get("size", 0))

            log(f"[{idx}/{len(files)}] Download {rel}")
            data = fetch_bytes(url)
            dst = payload_dir / rel
            write_bytes(dst, data)

            actual_sha = sha256_file(dst)
            actual_size = dst.stat().st_size
            ok = actual_sha == expected_sha and (expected_size == 0 or actual_size == expected_size)

            payload_sha_lines.append(f"{actual_sha}  {rel}")

            downloaded.append({
                "path": rel,
                "url": url,
                "txid": row["txid"],
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "expected_size": expected_size,
                "actual_size": actual_size,
                "ok": ok
            })

            if not ok:
                hard_failures.append(downloaded[-1])

    release_manifest = {
        "schema": "trinityaccord.github-release-backup.v1",
        "archive_id": ARCHIVE_ID,
        "release_tag": RELEASE_TAG,
        "source": {
            "arweave_manifest_txid": MANIFEST_TXID,
            "arweave_manifest_url": ARWEAVE_MANIFEST_URL,
            "arweave_manifest_raw_url": ARWEAVE_MANIFEST_RAW_URL,
            "arweave_index_json_url": INDEX_JSON_URL,
            "arweave_index_tsv_url": INDEX_TSV_URL,
            "arweave_index_html_url": INDEX_HTML_URL,
            "ots_bitcoin_block_height": OTS_BLOCK,
            "uploaded_file_count": EXPECTED_FILE_COUNT,
            "checked_tx_count": EXPECTED_CHECKED_TX_COUNT,
            "confirmed_ok": EXPECTED_CONFIRMED_OK
        },
        "downloaded_file_count": len(downloaded),
        "hard_failures": hard_failures,
        "payload_skipped": bool(args.skip_payload),
        "boundary": "Non-amending GitHub Release availability mirror. Bitcoin Originals and Arweave source records prevail.",
        "files": downloaded
    }

    if hard_failures:
        write_text(metadata_dir / "github-release-backup-manifest.json", json.dumps(release_manifest, indent=2, ensure_ascii=False))
        raise RuntimeError(f"Hard failures: {len(hard_failures)}")

    notes = f"""# Core Object Alpha Shenzhen Notary Arweave Backup v1

This GitHub Release is a verified availability mirror of the 2026-05-06 Shenzhen notary Arweave archive for Core Object Alpha.

It is non-amending. It does not modify, interpret, replace, extend, or supersede the Bitcoin Originals.

## Source Arweave archive

- Manifest TXID: `{MANIFEST_TXID}`
- Manifest URL: {ARWEAVE_MANIFEST_URL}
- Raw manifest URL: {ARWEAVE_MANIFEST_RAW_URL}
- Manifest index URL: https://arweave.net/{MANIFEST_TXID}/index.html
- Index JSON URL: {INDEX_JSON_URL}
- OTS Bitcoin block: `{OTS_BLOCK}`

## Verification summary

- Expected file count: {EXPECTED_FILE_COUNT}
- Downloaded file count: {len(downloaded)}
- Hard failures: {len(hard_failures)}
- Checked TX count from original Arweave acceptance: {EXPECTED_CHECKED_TX_COUNT}
- Confirmed OK from original Arweave acceptance: {EXPECTED_CONFIRMED_OK}

## Boundary

This is a GitHub Release backup mirror only. Bitcoin Originals prevail. All mirrors are non-amending.
"""

    write_text(metadata_dir / "github-release-backup-manifest.json", json.dumps(release_manifest, indent=2, ensure_ascii=False))
    write_text(metadata_dir / PAYLOAD_SHA256_NAME, "\n".join(sorted(payload_sha_lines)) + ("\n" if payload_sha_lines else ""))
    write_text(metadata_dir / "release-notes.md", notes)

    zip_path = release_dir / PAYLOAD_ZIP_NAME
    make_zip(work, zip_path)

    write_text(release_dir / BACKUP_MANIFEST_NAME, json.dumps(release_manifest, indent=2, ensure_ascii=False))
    write_text(release_dir / RELEASE_NOTES_NAME, notes)

    sha_lines = []
    for p in sorted(release_dir.iterdir()):
        if p.is_file() and p.name != ASSET_SHA256_NAME:
            sha_lines.append(f"{sha256_file(p)}  {p.name}")
    write_text(release_dir / ASSET_SHA256_NAME, "\n".join(sha_lines) + "\n")

    log("")
    log("Release assets created:")
    for p in sorted(release_dir.iterdir()):
        if p.is_file():
            log(f"{sha256_file(p)}  {p.name}  {p.stat().st_size} bytes")

    if args.skip_payload:
        log("SMOKE TEST COMPLETE: payload was skipped.")
    else:
        log("BACKUP BUILD PASS")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
