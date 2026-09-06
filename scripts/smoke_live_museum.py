#!/usr/bin/env python3
"""Verify the canonical museum export, without unrelated main-site requests."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "data/release-manifest.json"


def inventory(raw: bytes) -> dict:
    data = json.loads(raw)
    result = {}
    for item in data["files"]:
        path = item["path"]
        if (not isinstance(path, str) or not path or path.startswith("/")
                or ".." in PurePosixPath(path).parts or "\\" in path
                or str(PurePosixPath(path)) != path or path in result
                or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
                or type(item["bytes"]) is not int or item["bytes"] < 0):
            raise ValueError("invalid or duplicate museum inventory entry")
        result[path] = item
    if not {"index.html", "archive.html", "museum.js"} <= result.keys():
        raise ValueError("museum entrypoints missing from inventory")
    return result


def selected_files(current: dict, previous: dict) -> list[dict]:
    # Recheck all small runtime/data files; download large media only when changed.
    return [item for path, item in current.items()
            if item["bytes"] <= 262144 or previous.get(path) != item]


def verify_url(url: str, expected: dict, *, attempts: int = 4, delay: float = 5,
               opener=urllib.request.urlopen, pause=time.sleep) -> None:
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={
                "User-Agent": "Trinity-Museum-Verification/1.0",
                "Cache-Control": "no-cache", "Accept-Encoding": "identity",
            })
            with opener(request, timeout=20) as response:
                if response.status != 200 or response.geturl() != url:
                    raise ValueError("unexpected status or redirect")
                size = 0
                digest = hashlib.sha256()
                while chunk := response.read(65536):
                    size += len(chunk)
                    if size > expected["bytes"]:
                        raise ValueError("response exceeds expected file size")
                    digest.update(chunk)
            if size != expected["bytes"] or digest.hexdigest() != expected["sha256"]:
                raise ValueError("size or SHA-256 mismatch")
            return
        except (OSError, ValueError) as exc:
            if attempt + 1 == attempts:
                raise ValueError(f"{url}: {type(exc).__name__}: verification failed after {attempts} attempts") from exc
            pause(delay)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default="https://www.trinityaccord.org")
    parser.add_argument("--baseline", default="")
    args = parser.parse_args()
    if args.site.rstrip("/") != "https://www.trinityaccord.org":
        parser.error("museum publication must use the canonical custom domain")
    raw = (ROOT / "museum/dist" / MANIFEST).read_bytes()
    current = inventory(raw)
    previous = {}
    if args.baseline:
        try:
            from museum_change_scope import ensure_commit, git
            ensure_commit(args.baseline)
            previous = inventory(git("show", args.baseline + ":museum/dist/" + MANIFEST))
        except Exception:
            # Missing/invalid old inventory increases checks; never suppresses them.
            print("Baseline inventory unavailable; verifying every museum file", flush=True)
    base = args.site.rstrip("/") + "/museum/"
    verify_url(base + MANIFEST, {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    verify_url(base, current["index.html"])
    selected = selected_files(current, previous)

    def check(item):
        verify_url(base + urllib.parse.quote(item["path"], safe="/"), item)

    # Bounded concurrency and per-file retries avoid restarting the whole scan
    # because one CDN connection was reset.
    print(f"Checking {len(selected)} museum files at {base}", flush=True)
    pool = ThreadPoolExecutor(max_workers=4)
    futures = [pool.submit(check, item) for item in selected]
    try:
        for count, future in enumerate(as_completed(futures), 1):
            future.result()
            if count % 10 == 0 or count == len(selected):
                print(f"Verified {count}/{len(selected)} museum files", flush=True)
    finally:
        # A failed file cancels queued requests, instead of waiting through all
        # their retries while the workflow appears stuck.
        pool.shutdown(wait=True, cancel_futures=True)
    print(json.dumps({"result": "PASS", "scope": "museum", "url": base,
                      "edition": json.loads(raw)["edition"],
                      "verified_files": len(selected) + 1,
                      "unchanged_large_files": len(current) - len(selected)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
