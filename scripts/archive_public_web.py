#!/usr/bin/env python3
"""Archive public Trinity Accord URLs with auditable, rate-limited requests."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

WAYBACK_SAVE_PREFIX = "https://web.archive.org/save/"
SWH_SAVE_PREFIX = "https://archive.softwareheritage.org/api/1/origin/save/git/url/"
ALLOWED_ORIGIN = "https://www.trinityaccord.org"
DEFAULT_REPOSITORY = "https://github.com/thechurchofagi/trinity-accord"

CORE_PATHS = {
    "/",
    "/agent-brief/",
    "/agent-first-contact/",
    "/archive_legacy_index_2025_09/",
    "/authority/",
    "/covenant-proof/",
    "/inscriptions/",
    "/llms.txt",
    "/api/authority.json",
    "/api/evidence-manifest.json",
    "/api/hashes.json",
    "/api/links.json",
    "/api/record-chain-status.json",
    "/api/waiting-heartbeat-status.json",
    "/sitemap.xml",
    "/verify/",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_sitemap(path: Path) -> tuple[list[str], str]:
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    urls: list[str] = []
    seen: set[str] = set()
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "loc" or not element.text:
            continue
        url = element.text.strip()
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != "www.trinityaccord.org":
            raise ValueError(f"refusing non-canonical sitemap URL: {url}")
        if parsed.fragment:
            raise ValueError(f"refusing sitemap URL with fragment: {url}")
        if url not in seen:
            urls.append(url)
            seen.add(url)
    if not urls:
        raise ValueError("sitemap contains no URLs")
    return urls, hashlib.sha256(raw).hexdigest()


def select_urls(
    urls: Iterable[str], scope: str, maximum: int, offset: int = 0
) -> list[str]:
    selected: list[str] = []
    for url in urls:
        path = urllib.parse.urlsplit(url).path
        if scope == "pages":
            leaf = path.rsplit("/", 1)[-1]
            if path.endswith("/") or "." not in leaf:
                selected.append(url)
        elif scope == "core":
            if path in CORE_PATHS:
                selected.append(url)
        else:
            selected.append(url)
    selected = selected[offset:]
    if maximum > 0:
        selected = selected[:maximum]
    return selected


def wayback_headers() -> dict[str, str]:
    headers = {
        "User-Agent": "TrinityAccordArchive/1.0 (+https://www.trinityaccord.org/)",
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
    }
    access = os.environ.get("WAYBACK_ACCESS_KEY", "").strip()
    secret = os.environ.get("WAYBACK_SECRET_KEY", "").strip()
    if bool(access) != bool(secret):
        raise ValueError("WAYBACK_ACCESS_KEY and WAYBACK_SECRET_KEY must be set together")
    if access:
        headers["Authorization"] = f"LOW {access}:{secret}"
    return headers


def retry_delay(error: urllib.error.HTTPError, attempt: int) -> float:
    value = error.headers.get("Retry-After", "").strip()
    if value.isdigit():
        return min(float(value), 300.0)
    return min(2 ** attempt * 5.0, 120.0)


def capture_wayback(url: str, timeout: float, retries: int) -> dict:
    save_url = WAYBACK_SAVE_PREFIX + url
    headers = wayback_headers()
    started = utc_now()
    for attempt in range(retries + 1):
        request = urllib.request.Request(save_url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                capture = response.headers.get("Content-Location") or response.geturl()
                if capture.startswith("/"):
                    capture = "https://web.archive.org" + capture
                return {
                    "url": url,
                    "status": "captured",
                    "http_status": response.status,
                    "capture_url": capture,
                    "attempts": attempt + 1,
                    "started_at": started,
                    "finished_at": utc_now(),
                }
        except urllib.error.HTTPError as error:
            retryable = error.code == 429 or 500 <= error.code < 600
            if retryable and attempt < retries:
                time.sleep(retry_delay(error, attempt + 1))
                continue
            return {
                "url": url,
                "status": "failed",
                "http_status": error.code,
                "error": str(error),
                "attempts": attempt + 1,
                "started_at": started,
                "finished_at": utc_now(),
            }
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if attempt < retries:
                time.sleep(min(2 ** (attempt + 1) * 5.0, 120.0))
                continue
            return {
                "url": url,
                "status": "failed",
                "http_status": None,
                "error": f"{type(error).__name__}: {error}",
                "attempts": attempt + 1,
                "started_at": started,
                "finished_at": utc_now(),
            }
    raise AssertionError("unreachable")


def request_software_heritage(repository: str, timeout: float) -> dict:
    encoded = urllib.parse.quote(repository, safe="")
    request = urllib.request.Request(
        SWH_SAVE_PREFIX + encoded + "/",
        data=b"",
        headers={
            "User-Agent": "TrinityAccordArchive/1.0 (+https://www.trinityaccord.org/)",
            "Accept": "application/json",
        },
        method="POST",
    )
    started = utc_now()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {"raw_body": body[:2000]}
            return {
                "repository": repository,
                "status": "requested",
                "http_status": response.status,
                "response": payload,
                "started_at": started,
                "finished_at": utc_now(),
            }
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {
            "repository": repository,
            "status": "failed",
            "http_status": error.code,
            "error": str(error),
            "response_body": body[:2000],
            "started_at": started,
            "finished_at": utc_now(),
        }
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {
            "repository": repository,
            "status": "failed",
            "http_status": None,
            "error": f"{type(error).__name__}: {error}",
            "started_at": started,
            "finished_at": utc_now(),
        }


def write_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sitemap", type=Path, default=Path("sitemap.xml"))
    parser.add_argument("--output", type=Path, default=Path("internet-archive-results.json"))
    parser.add_argument("--scope", choices=("core", "pages", "all"), default="core")
    parser.add_argument("--max-urls", type=int, default=0)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--delay-seconds", type=float, default=15.0)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--request-software-heritage", action="store_true")
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if (
        args.max_urls < 0
        or args.offset < 0
        or args.delay_seconds < 0
        or args.timeout_seconds <= 0
        or args.retries < 0
    ):
        raise SystemExit("numeric arguments must be non-negative and timeout must be positive")

    all_urls, sitemap_sha256 = load_sitemap(args.sitemap)
    scoped_urls = select_urls(all_urls, args.scope, 0)
    selected = select_urls(all_urls, args.scope, args.max_urls, args.offset)
    result = {
        "schema": "trinityaccord.public-internet-archive-results.v1",
        "generated_at": utc_now(),
        "dry_run": args.dry_run,
        "scope": args.scope,
        "sitemap": str(args.sitemap),
        "sitemap_sha256": sitemap_sha256,
        "sitemap_url_count": len(all_urls),
        "scoped_url_count": len(scoped_urls),
        "selected_start_index": args.offset,
        "selected_url_count": len(selected),
        "wayback": [],
        "software_heritage": None,
        "boundary": {
            "archive_is_mirror_only": True,
            "archive_is_not_authority": True,
            "archive_is_not_attestation": True,
            "archive_is_not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }

    if args.dry_run:
        result["wayback"] = [{"url": url, "status": "dry-run"} for url in selected]
        if args.request_software_heritage:
            result["software_heritage"] = {
                "repository": args.repository,
                "status": "dry-run",
            }
    else:
        for index, url in enumerate(selected):
            print(f"[{index + 1}/{len(selected)}] {url}", flush=True)
            item = capture_wayback(url, args.timeout_seconds, args.retries)
            result["wayback"].append(item)
            write_result(args.output, result)
            if index + 1 < len(selected) and args.delay_seconds:
                time.sleep(args.delay_seconds)
        if args.request_software_heritage:
            result["software_heritage"] = request_software_heritage(
                args.repository, args.timeout_seconds
            )

    counts: dict[str, int] = {}
    for item in result["wayback"]:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    result["summary"] = counts
    result["completed_at"] = utc_now()
    write_result(args.output, result)
    print(json.dumps(result["summary"], sort_keys=True))

    if args.dry_run:
        return 0
    return 1 if counts.get("failed", 0) else 0


if __name__ == "__main__":
    sys.exit(main())
