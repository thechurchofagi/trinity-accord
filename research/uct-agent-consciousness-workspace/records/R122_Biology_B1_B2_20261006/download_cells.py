#!/usr/bin/env python3
"""Fetch or verify the exact public Figshare v1 rat recording archive.

Uses Python's standard library only. No credentials or author lab access.
Signed redirect query strings are never saved. Existing completed files are
verified, not overwritten. Partial transfers support HTTP Range when offered.
"""
import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit
import zipfile

DOI = "10.6084/m9.figshare.30369064.v1"
URL = "https://ndownloader.figshare.com/files/58773835"
SIZE = 1929137550
MD5 = "3b0ab5c964fb492ec36ee0f55a5d53de"
SHA256 = "e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494"

def verify(path):
    if path.stat().st_size != SIZE:
        raise ValueError(f"Size mismatch: {path.stat().st_size}, expected {SIZE}")
    md5, sha = hashlib.md5(), hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(8 * 1024 * 1024):
            md5.update(block)
            sha.update(block)
    if md5.hexdigest() != MD5 or sha.hexdigest() != SHA256:
        raise ValueError("Archive digest mismatch; preserved for inspection")
    return {"bytes": SIZE, "md5": md5.hexdigest(), "sha256": sha.hexdigest(),
            "status": "VERIFIED_FULL_ARCHIVE"}

def download(outdir, attempts):
    target, partial = outdir / "Cells.zip", outdir / "Cells.zip.part"
    if target.exists():
        return target, [dict(verify(target), action="verify_existing")]
    ledger = []
    for i in range(attempts):
        offset = partial.stat().st_size if partial.exists() else 0
        item = {"attempt": i + 1, "source": URL, "resume_offset": offset,
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        ledger.append(item)
        # Refresh the public redirect only after an unsuccessful standard request.
        url = URL if i == 0 else URL + "?download=1&request_time=" + str(int(time.time()))
        headers = {"User-Agent": "UCT-public-data-reanalysis/1.0"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                item.update(http_status=r.status, final_host=urlsplit(r.url).hostname,
                            content_length=r.headers.get("Content-Length"),
                            content_range=r.headers.get("Content-Range"))
                if r.status == 206:
                    if not r.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
                        raise ValueError("Resume range mismatch")
                    mode = "ab"
                elif r.status == 200:
                    mode, offset = "wb", 0
                else:
                    raise ValueError(f"Unexpected status {r.status}")
                last = time.monotonic()
                with partial.open(mode) as f:
                    while block := r.read(1024 * 1024):
                        if offset == 0 and not block.startswith(b"PK"):
                            raise ValueError("The public download response is not a ZIP stream")
                        f.write(block)
                        offset += len(block)
                        if offset > SIZE:
                            raise ValueError("Stream exceeded expected archive size")
                        if time.monotonic() - last > 15:
                            print(json.dumps({"downloaded_bytes": offset, "total_bytes": SIZE}), flush=True)
                            last = time.monotonic()
            item.update(verify(partial))
            partial.rename(target)
            break
        except Exception as exc:
            item.update(status="FAILED", error_type=type(exc).__name__,
                        error=str(exc).split("?")[0][:300])
        finally:
            (outdir / "download_attempts.json").write_text(json.dumps(ledger, indent=2) + "\n")
    if not target.exists():
        raise RuntimeError("Download incomplete; inspect download_attempts.json and retain partial file")
    return target, ledger

def extract(archive, destination):
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    manifest = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            p = Path(info.filename)
            if not info.filename.endswith(".mat") or any(s.startswith(".") or s == "__MACOSX" for s in p.parts):
                continue
            target = (destination / p).resolve()
            if not target.is_relative_to(destination):
                raise ValueError("Unsafe archive member path")
            target.parent.mkdir(parents=True, exist_ok=True)
            # Reading ZipExtFile to EOF validates the ZIP member CRC.
            if target.exists():
                raise FileExistsError(f"Refusing to replace existing extracted session: {target}")
            h = hashlib.sha256()
            with z.open(info) as src, target.open("wb") as dst:
                while b := src.read(8 * 1024 * 1024):
                    dst.write(b)
                    h.update(b)
            manifest.append({"member": info.filename, "bytes": info.file_size,
                             "crc32": f"{info.CRC:08x}", "sha256": h.hexdigest()})
    (destination / "extracted_session_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if len(manifest) != 12:
        raise ValueError(f"Expected exactly 12 session MAT files, found {len(manifest)}")
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data"))
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--extract-to", type=Path)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.verify_only:
        target = args.out / "Cells.zip"
        result = {"doi": DOI, "archive": str(target), **verify(target)}
    else:
        target, ledger = download(args.out, args.attempts)
        result = {"doi": DOI, "archive": str(target), "attempts": ledger}
    if args.extract_to:
        result["session_manifest"] = extract(target, args.extract_to)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
