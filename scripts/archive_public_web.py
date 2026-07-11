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
WAYBACK_AVAILABLE_PREFIX = "https://archive.org/wayback/available?url="
SWH_SAVE_PREFIX = "https://archive.softwareheritage.org/api/1/origin/save/git/url/"
ALLOWED_ORIGIN = "https://www.trinityaccord.org"
DEFAULT_REPOSITORY = "https://github.com/thechurchofagi/trinity-accord"
SUCCESS_STATUSES = {"captured", "already_captured", "dry-run"}
RETRYABLE_WAYBACK_HTTP = {404, 408, 409, 425, 429}

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


def validate_canonical_url(url: str) -> str:
    value = url.strip()
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or parsed.netloc != "www.trinityaccord.org":
        raise ValueError(f"refusing non-canonical URL: {value}")
    if parsed.fragment:
        raise ValueError(f"refusing URL with fragment: {value}")
    return value


def load_sitemap(path: Path) -> tuple[list[str], str]:
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    urls: list[str] = []
    seen: set[str] = set()
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "loc" or not element.text:
            continue
        url = validate_canonical_url(element.text)
        if url not in seen:
            urls.append(url)
            seen.add(url)
    if not urls:
        raise ValueError("sitemap contains no URLs")
    return urls, hashlib.sha256(raw).hexdigest()


def load_url_file(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = [line.strip() for line in raw.splitlines() if line.strip()]
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError("URL file must contain a JSON string array or one URL per line")
    urls: list[str] = []
    seen: set[str] = set()
    for item in payload:
        url = validate_canonical_url(item)
        if url not in seen:
            urls.append(url)
            seen.add(url)
    if not urls:
        raise ValueError("URL file contains no URLs")
    return urls


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


def common_headers() -> dict[str, str]:
    return {
        "User-Agent": "TrinityAccordArchive/1.1 (+https://www.trinityaccord.org/)",
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
    }


def wayback_headers() -> dict[str, str]:
    headers = common_headers()
    access = os.environ.get("WAYBACK_ACCESS_KEY", "").strip()
    secret = os.environ.get("WAYBACK_SECRET_KEY", "").strip()
    if bool(access) != bool(secret):
        raise ValueError("WAYBACK_ACCESS_KEY and WAYBACK_SECRET_KEY must be set together")
    if access:
        headers["Authorization"] = f"LOW {access}:{secret}"
    return headers


def retry_delay(error: urllib.error.HTTPError | None, attempt: int) -> float:
    if error is not None:
        value = error.headers.get("Retry-After", "").strip()
        if value.isdigit():
            return min(float(value), 900.0)
    return min(30.0 * (2 ** max(attempt - 1, 0)), 300.0)


def is_retryable_http(code: int, *, source_probe: bool = False) -> bool:
    if source_probe:
        return code in {408, 425, 429} or 500 <= code < 600
    return code in RETRYABLE_WAYBACK_HTTP or 500 <= code < 600


def probe_source(url: str, timeout: float, retries: int) -> dict:
    started = utc_now()
    headers = common_headers()
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, headers=headers, method="HEAD")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return {
                    "available": 200 <= response.status < 400,
                    "http_status": response.status,
                    "attempts": attempt + 1,
                    "started_at": started,
                    "finished_at": utc_now(),
                }
        except urllib.error.HTTPError as error:
            if error.code in {403, 405}:
                fallback_headers = dict(headers)
                fallback_headers["Range"] = "bytes=0-0"
                fallback = urllib.request.Request(url, headers=fallback_headers, method="GET")
                try:
                    with urllib.request.urlopen(fallback, timeout=timeout) as response:
                        return {
                            "available": 200 <= response.status < 400,
                            "http_status": response.status,
                            "attempts": attempt + 1,
                            "started_at": started,
                            "finished_at": utc_now(),
                        }
                except urllib.error.HTTPError as fallback_error:
                    error = fallback_error
            if is_retryable_http(error.code, source_probe=True) and attempt < retries:
                time.sleep(retry_delay(error, attempt + 1))
                continue
            return {
                "available": False,
                "http_status": error.code,
                "attempts": attempt + 1,
                "error": str(error),
                "started_at": started,
                "finished_at": utc_now(),
            }
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if attempt < retries:
                time.sleep(retry_delay(None, attempt + 1))
                continue
            return {
                "available": False,
                "http_status": None,
                "attempts": attempt + 1,
                "error": f"{type(error).__name__}: {error}",
                "started_at": started,
                "finished_at": utc_now(),
            }
    raise AssertionError("unreachable")


def find_recent_capture(url: str, timeout: float, recent_days: int) -> dict | None:
    if recent_days <= 0:
        return None
    query = WAYBACK_AVAILABLE_PREFIX + urllib.parse.quote(url, safe="")
    request = urllib.request.Request(query, headers=common_headers(), method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None
    closest = payload.get("archived_snapshots", {}).get("closest") or {}
    if not closest.get("available") or str(closest.get("status")) != "200":
        return None
    timestamp = str(closest.get("timestamp", ""))
    if len(timestamp) < 8 or not timestamp[:8].isdigit():
        return None
    try:
        captured_at = datetime.strptime(timestamp[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    age_seconds = (datetime.now(timezone.utc) - captured_at).total_seconds()
    if age_seconds < 0 or age_seconds > recent_days * 86400:
        return None
    return {
        "capture_url": closest.get("url"),
        "capture_timestamp": timestamp,
        "capture_age_seconds": int(age_seconds),
    }


def capture_wayback(
    url: str,
    timeout: float,
    retries: int,
    *,
    source_timeout: float = 30.0,
    source_retries: int = 2,
    recent_days: int = 7,
) -> dict:
    started = utc_now()
    source = probe_source(url, source_timeout, source_retries)
    if not source.get("available"):
        return {
            "url": url,
            "status": "source_unavailable",
            "source": source,
            "attempts": 0,
            "started_at": started,
            "finished_at": utc_now(),
        }

    recent = find_recent_capture(url, min(timeout, 60.0), recent_days)
    if recent:
        return {
            "url": url,
            "status": "already_captured",
            "http_status": 200,
            "source": source,
            **recent,
            "attempts": 0,
            "started_at": started,
            "finished_at": utc_now(),
        }

    save_url = WAYBACK_SAVE_PREFIX + url
    headers = wayback_headers()
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
                    "source": source,
                    "attempts": attempt + 1,
                    "started_at": started,
                    "finished_at": utc_now(),
                }
        except urllib.error.HTTPError as error:
            if is_retryable_http(error.code) and attempt < retries:
                time.sleep(retry_delay(error, attempt + 1))
                continue
            return {
                "url": url,
                "status": "failed",
                "http_status": error.code,
                "error": str(error),
                "source": source,
                "attempts": attempt + 1,
                "started_at": started,
                "finished_at": utc_now(),
            }
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if attempt < retries:
                time.sleep(retry_delay(None, attempt + 1))
                continue
            return {
                "url": url,
                "status": "failed",
                "http_status": None,
                "error": f"{type(error).__name__}: {error}",
                "source": source,
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
            "User-Agent": "TrinityAccordArchive/1.1 (+https://www.trinityaccord.org/)",
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
    temporary.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sitemap", type=Path, default=Path("sitemap.xml"))
    parser.add_argument("--urls-file", type=Path)
    parser.add_argument("--output", type=Path, default=Path("internet-archive-results.json"))
    parser.add_argument("--scope", choices=("core", "pages", "all"), default="core")
    parser.add_argument("--max-urls", type=int, default=0)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--delay-seconds", type=float, default=30.0)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--source-timeout-seconds", type=float, default=30.0)
    parser.add_argument("--source-retries", type=int, default=2)
    parser.add_argument("--recent-days", type=int, default=7)
    parser.add_argument("--run-kind", choices=("initial", "retry"), default="initial")
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
        or args.source_timeout_seconds <= 0
        or args.source_retries < 0
        or args.recent_days < 0
    ):
        raise SystemExit("numeric arguments must be non-negative and timeouts must be positive")

    all_urls, sitemap_sha256 = load_sitemap(args.sitemap)
    source_urls = load_url_file(args.urls_file) if args.urls_file else all_urls
    scoped_urls = select_urls(source_urls, args.scope, 0)
    selected = select_urls(source_urls, args.scope, args.max_urls, args.offset)
    result = {
        "schema": "trinityaccord.public-internet-archive-results.v1",
        "generated_at": utc_now(),
        "run_kind": args.run_kind,
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
            item = capture_wayback(
                url,
                args.timeout_seconds,
                args.retries,
                source_timeout=args.source_timeout_seconds,
                source_retries=args.source_retries,
                recent_days=args.recent_days,
            )
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
    unresolved = sum(
        count for status, count in counts.items() if status not in SUCCESS_STATUSES
    )
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
