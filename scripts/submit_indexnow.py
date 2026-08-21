#!/usr/bin/env python3
"""Submit Trinity Accord high-signal discovery URLs to IndexNow.

This is a non-amending discoverability utility. It reads the dedicated
high-signal discovery sitemap, verifies that every URL belongs to the configured
public host, verifies the already-public root IndexNow key when running live,
and submits one bounded batch.

The script intentionally has no secrets and no hidden URL generation. Use
--dry-run to inspect the exact URL set without network access.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = "https://www.trinityaccord.org"
DEFAULT_ENDPOINT = "https://api.indexnow.org/indexnow"
DEFAULT_SITEMAP = ROOT / "sitemap-discovery.xml"
DEFAULT_KEY_FILE = ROOT / "4c23c01d8a12d488d40469e5e5d01941.txt"
DEFAULT_EXTRA_PATHS: tuple[str, ...] = ()
KEY_PATTERN = re.compile(r"^[A-Za-z0-9-]{8,128}$")
MAX_URLS = 10_000


def normalize_site(value: str) -> str:
    site = value.strip().rstrip("/")
    parsed = urllib.parse.urlsplit(site)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"invalid site URL: {value!r}")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("site URL must be an origin without path/query/fragment")
    return site


def read_key(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"IndexNow key file does not exist: {path}")
    key = path.read_text(encoding="utf-8").strip()
    if not KEY_PATTERN.fullmatch(key):
        raise ValueError("IndexNow key must be 8-128 ASCII letters, digits, or hyphens")
    if path.stem != key:
        raise ValueError(
            f"root key filename stem must equal the public key: {path.stem!r} != {key!r}"
        )
    return key


def sitemap_urls(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError(f"sitemap does not exist: {path}")
    root = ET.parse(path).getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for node in root.findall("sm:url/sm:loc", namespace):
        if node.text and node.text.strip():
            urls.append(node.text.strip())
    if not urls:
        raise ValueError(f"sitemap contains no URL entries: {path}")
    return urls


def validate_same_host(url: str, expected_hostname: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"non-HTTP URL in discovery batch: {url}")
    if parsed.hostname != expected_hostname:
        raise ValueError(
            f"cross-host URL rejected: {url} (expected hostname {expected_hostname})"
        )
    if parsed.username or parsed.password:
        raise ValueError(f"credential-bearing URL rejected: {url}")
    return url


def collect_urls(site: str, sitemap: Path, extra_paths: list[str]) -> list[str]:
    hostname = urllib.parse.urlsplit(site).hostname
    if not hostname:
        raise ValueError("site hostname is empty")

    candidates = sitemap_urls(sitemap)
    for path in extra_paths:
        path = path.strip()
        if not path:
            continue
        if path.startswith("http://") or path.startswith("https://"):
            candidates.append(path)
        else:
            if not path.startswith("/"):
                path = "/" + path
            candidates.append(site + path)

    result = sorted({validate_same_host(url, hostname) for url in candidates})
    if len(result) > MAX_URLS:
        raise ValueError(f"IndexNow batch has {len(result)} URLs; maximum is {MAX_URLS}")
    return result


def fetch_bytes(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "trinity-accord-indexnow/1.1",
            "Accept": "text/plain,*/*",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            print(f"LIVE CHECK {response.status}: {url}")
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"live check HTTP {exc.code} for {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"live check failed for {url}: {exc.reason}") from exc


def verify_live_key(site: str, key_file: Path, key: str, timeout: int) -> str:
    key_location = f"{site}/{key_file.name}"
    live = fetch_bytes(key_location, timeout).decode("utf-8", errors="strict").strip()
    if live != key:
        raise RuntimeError(
            f"live IndexNow key mismatch at {key_location}: expected repository key"
        )
    print(f"PASS live IndexNow key: {key_location}")
    return key_location


def submit(endpoint: str, payload: dict, timeout: int) -> int:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "trinity-accord-indexnow/1.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")[:1000]
            print(f"INDEXNOW HTTP {response.status}")
            if response_body:
                print(f"INDEXNOW BODY {response_body}")
            return response.status
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")[:1000]
        print(f"INDEXNOW HTTP {exc.code}")
        if response_body:
            print(f"INDEXNOW BODY {response_body}")
        return exc.code
    except urllib.error.URLError as exc:
        raise RuntimeError(f"IndexNow request failed: {exc.reason}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit high-signal Trinity Accord URLs to IndexNow")
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--sitemap", type=Path, default=DEFAULT_SITEMAP)
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--extra-url", action="append", default=[], help="Additional same-host URL or path")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-live-key-check", action="store_true")
    args = parser.parse_args()

    try:
        site = normalize_site(args.site)
        key = read_key(args.key_file)
        extras = list(DEFAULT_EXTRA_PATHS) + list(args.extra_url)
        urls = collect_urls(site, args.sitemap, extras)
    except (ValueError, ET.ParseError, UnicodeError) as exc:
        print(f"FAIL preflight: {exc}")
        return 2

    parsed_site = urllib.parse.urlsplit(site)
    key_location = f"{site}/{args.key_file.name}"
    payload = {
        "host": parsed_site.netloc,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls,
    }

    print(f"IndexNow endpoint: {args.endpoint}")
    print(f"Public host: {parsed_site.netloc}")
    print(f"Key location: {key_location}")
    print(f"Source sitemap: {args.sitemap}")
    print(f"URL count: {len(urls)}")
    for url in urls:
        print(f"  URL {url}")

    if args.dry_run:
        print("DRY RUN PASS: payload validated; no network submission performed")
        return 0

    try:
        if not args.skip_live_key_check:
            verify_live_key(site, args.key_file, key, args.timeout)
        status = submit(args.endpoint, payload, args.timeout)
    except (RuntimeError, UnicodeError) as exc:
        print(f"FAIL network: {exc}")
        return 3

    if status == 200:
        print("PASS: IndexNow accepted the URL batch")
        return 0
    if status == 202:
        print("PASS WITH PENDING KEY VALIDATION: IndexNow received the URL batch")
        return 0

    meanings = {
        400: "bad request / invalid format",
        403: "key invalid or key file unavailable",
        422: "URL host mismatch or protocol/schema mismatch",
        429: "rate limited / too many requests",
    }
    print(f"FAIL: IndexNow rejected the batch: {meanings.get(status, 'unexpected response')}")
    return 4


if __name__ == "__main__":
    sys.exit(main())
