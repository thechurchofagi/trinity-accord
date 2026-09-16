#!/usr/bin/env python3
"""Archive the deployed homepage to independent public web archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.archive_public_web import (
    capture_wayback,
    common_headers,
    retry_delay,
    utc_now,
    validate_canonical_url,
    write_result,
)

HOMEPAGE_URL = "https://www.trinityaccord.org/"
ARQUIVO_SAVE_URL = "https://arquivo.pt/services/archivepagenow?l=en"
PERMA_ARCHIVES_URL = "https://api.perma.cc/v1/archives/"
WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"
STATUS_BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
STATUS_END = "<!-- END GENERATED PUBLIC STATUS -->"
ARCHIVE_SUCCESS = {
    "wayback": {"captured", "captured_after_error", "already_captured"},
    "arquivo_pt": {"submitted", "captured"},
    "perma_cc": {"accepted", "captured"},
}
RETRYABLE_HTTP = {408, 425, 429}


def meaningful_homepage_bytes(raw: bytes) -> bytes:
    """Remove the generated status payload while retaining its boundary markers."""
    text = raw.decode("utf-8")
    if text.count(STATUS_BEGIN) != 1 or text.count(STATUS_END) != 1:
        raise ValueError("homepage must contain exactly one generated Public Status block")
    begin = text.index(STATUS_BEGIN)
    end = text.index(STATUS_END, begin) + len(STATUS_END)
    if end <= begin:
        raise ValueError("generated Public Status markers are out of order")
    normalized = text[:begin] + STATUS_BEGIN + "\n" + STATUS_END + text[end:]
    return normalized.encode("utf-8")


def meaningful_homepage_sha256(path: Path) -> str:
    return hashlib.sha256(meaningful_homepage_bytes(path.read_bytes())).hexdigest()


def homepage_changed(current: Path, previous: Path) -> tuple[bool, str, str]:
    current_digest = meaningful_homepage_sha256(current)
    previous_digest = meaningful_homepage_sha256(previous)
    return current_digest != previous_digest, previous_digest, current_digest


def find_wayback_capture_since(url: str, started_at: str, timeout: float) -> dict | None:
    """Confirm a capture that Save Page Now created despite returning an error."""
    started = datetime.fromisoformat(started_at).astimezone(timezone.utc)
    lower_bound = started - timedelta(seconds=5)
    query = urllib.parse.urlencode(
        {
            "url": url,
            "output": "json",
            "fl": "timestamp,statuscode,original",
            "filter": "statuscode:200",
            "from": lower_bound.strftime("%Y%m%d%H%M%S"),
            "limit": "-10",
        }
    )
    request = urllib.request.Request(
        f"{WAYBACK_CDX_URL}?{query}", headers=common_headers(), method="GET"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            rows = json.loads(response.read().decode("utf-8"))
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
    ):
        return None
    if not isinstance(rows, list) or len(rows) < 2:
        return None
    header = rows[0]
    if not isinstance(header, list):
        return None
    try:
        timestamp_index = header.index("timestamp")
        status_index = header.index("statuscode")
    except ValueError:
        return None
    candidates = []
    for row in rows[1:]:
        if not isinstance(row, list) or len(row) <= max(timestamp_index, status_index):
            continue
        timestamp = str(row[timestamp_index])
        if (
            str(row[status_index]) == "200"
            and len(timestamp) == 14
            and timestamp.isdigit()
            and timestamp >= lower_bound.strftime("%Y%m%d%H%M%S")
        ):
            candidates.append(timestamp)
    if not candidates:
        return None
    timestamp = max(candidates)
    return {
        "capture_timestamp": timestamp,
        "capture_url": f"https://web.archive.org/web/{timestamp}/{url}",
        "confirmation": "cdx-after-save-error",
    }


def _response_snapshot_url(body: str) -> str | None:
    match = re.search(
        r'https://arquivo\.pt/(?:wayback|noFrame/replay)/[^"\'<>\s]+', body
    )
    return match.group(0) if match else None


def capture_arquivo(url: str, timeout: float, retries: int) -> dict:
    """Submit one page to Arquivo.pt's public ArchivePageNow service."""
    started = utc_now()
    payload = urllib.parse.urlencode({"url": url}).encode("utf-8")
    headers = common_headers()
    headers.update(
        {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml",
        }
    )
    for attempt in range(retries + 1):
        request = urllib.request.Request(
            ARQUIVO_SAVE_URL, data=payload, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                snapshot_url = _response_snapshot_url(body)
                result = {
                    "url": url,
                    "status": "captured" if snapshot_url else "submitted",
                    "http_status": response.status,
                    "submission_url": response.geturl(),
                    "response_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                    "attempts": attempt + 1,
                    "started_at": started,
                    "finished_at": utc_now(),
                }
                if snapshot_url:
                    result["capture_url"] = snapshot_url
                return result
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            if (error.code in RETRYABLE_HTTP or error.code >= 500) and attempt < retries:
                time.sleep(retry_delay(error, attempt + 1))
                continue
            return {
                "url": url,
                "status": "failed",
                "http_status": error.code,
                "error": str(error),
                "response_body": body[:1000],
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
                "attempts": attempt + 1,
                "started_at": started,
                "finished_at": utc_now(),
            }
    raise AssertionError("unreachable")


def _perma_primary_status(payload: dict) -> str | None:
    for capture in payload.get("captures") or []:
        if capture.get("role") == "primary":
            return capture.get("status")
    return None


def capture_perma(
    url: str,
    api_key: str,
    timeout: float,
    *,
    poll_attempts: int = 20,
    poll_seconds: float = 15.0,
) -> dict:
    """Create and verify a Perma.cc archive through its documented API."""
    started = utc_now()
    headers = {
        "Authorization": f"ApiKey {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": common_headers()["User-Agent"],
    }
    request = urllib.request.Request(
        PERMA_ARCHIVES_URL,
        data=json.dumps({"url": url, "title": "The Trinity Accord"}).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            http_status = response.status
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {
            "url": url,
            "status": "failed",
            "http_status": error.code,
            "error": str(error),
            "response_body": body[:1000],
            "started_at": started,
            "finished_at": utc_now(),
        }
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
        return {
            "url": url,
            "status": "failed",
            "http_status": None,
            "error": f"{type(error).__name__}: {error}",
            "started_at": started,
            "finished_at": utc_now(),
        }

    guid = str(payload.get("guid") or "").strip()
    if not guid:
        return {
            "url": url,
            "status": "failed",
            "http_status": http_status,
            "error": "Perma.cc response did not include a GUID",
            "started_at": started,
            "finished_at": utc_now(),
        }

    details_url = f"{PERMA_ARCHIVES_URL}{urllib.parse.quote(guid, safe='')}/"
    latest = payload
    for attempt in range(poll_attempts + 1):
        primary_status = _perma_primary_status(latest)
        if primary_status == "success":
            return {
                "url": url,
                "status": "captured",
                "http_status": http_status,
                "guid": guid,
                "capture_url": f"https://perma.cc/{guid}",
                "warc_download_url": latest.get("warc_download_url"),
                "wacz_download_url": latest.get("wacz_download_url"),
                "poll_attempts": attempt,
                "started_at": started,
                "finished_at": utc_now(),
            }
        if primary_status == "failed":
            return {
                "url": url,
                "status": "failed",
                "http_status": http_status,
                "guid": guid,
                "capture_url": f"https://perma.cc/{guid}",
                "error": "Perma.cc primary capture failed",
                "poll_attempts": attempt,
                "started_at": started,
                "finished_at": utc_now(),
            }
        if attempt == poll_attempts:
            break
        time.sleep(poll_seconds)
        detail_request = urllib.request.Request(details_url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(detail_request, timeout=timeout) as response:
                latest = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            continue

    return {
        "url": url,
        "status": "accepted",
        "http_status": http_status,
        "guid": guid,
        "capture_url": f"https://perma.cc/{guid}",
        "primary_status": _perma_primary_status(latest),
        "poll_attempts": poll_attempts,
        "started_at": started,
        "finished_at": utc_now(),
    }


def archive_homepage(
    url: str,
    *,
    timeout: float,
    retries: int,
    dry_run: bool,
    source_sha: str,
    trigger: str,
) -> dict:
    url = validate_canonical_url(url)
    perma_key = os.environ.get("PERMA_API_KEY", "").strip()
    result = {
        "schema": "trinityaccord.homepage-public-archive.v1",
        "generated_at": utc_now(),
        "url": url,
        "source_sha": source_sha,
        "trigger": trigger,
        "dry_run": dry_run,
        "services": {},
        "boundary": {
            "archive_is_mirror_only": True,
            "archive_is_not_authority": True,
            "archive_is_not_attestation": True,
            "archive_is_not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }
    if dry_run:
        result["services"] = {
            "wayback": {"url": url, "status": "dry-run"},
            "arquivo_pt": {"url": url, "status": "dry-run"},
            "perma_cc": {
                "url": url,
                "status": "dry-run" if perma_key else "not_configured",
            },
        }
        result["accepted_service_count"] = 0
        result["completed_at"] = utc_now()
        return result

    try:
        wayback = capture_wayback(
            url,
            timeout,
            retries,
            source_timeout=min(timeout, 30.0),
            source_retries=2,
            recent_days=0,
        )
        if wayback.get("status") == "failed" and wayback.get("started_at"):
            confirmed = find_wayback_capture_since(
                url, wayback["started_at"], min(timeout, 90.0)
            )
            if confirmed:
                wayback["reported_status"] = wayback["status"]
                wayback["reported_error"] = wayback.get("error")
                wayback["status"] = "captured_after_error"
                wayback.update(confirmed)
        result["services"]["wayback"] = wayback
    except (ValueError, OSError) as error:
        result["services"]["wayback"] = {
            "url": url,
            "status": "failed",
            "error": f"{type(error).__name__}: {error}",
        }
    result["services"]["arquivo_pt"] = capture_arquivo(url, timeout, retries)
    if perma_key:
        result["services"]["perma_cc"] = capture_perma(url, perma_key, timeout)
    else:
        result["services"]["perma_cc"] = {
            "url": url,
            "status": "not_configured",
        }

    result["accepted_service_count"] = sum(
        service.get("status") in ARCHIVE_SUCCESS[name]
        for name, service in result["services"].items()
    )
    result["completed_at"] = utc_now()
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    changed = subparsers.add_parser("changed")
    changed.add_argument("--current", type=Path, required=True)
    changed.add_argument("--previous", type=Path, required=True)

    archive = subparsers.add_parser("archive")
    archive.add_argument("--url", default=HOMEPAGE_URL)
    archive.add_argument("--output", type=Path, required=True)
    archive.add_argument("--source-sha", default="")
    archive.add_argument("--trigger", default="manual")
    archive.add_argument("--timeout-seconds", type=float, default=120.0)
    archive.add_argument("--retries", type=int, default=3)
    archive.add_argument("--required-services", type=int, default=2)
    archive.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "changed":
        changed, previous, current = homepage_changed(args.current, args.previous)
        print(f"changed={'true' if changed else 'false'}")
        print(f"previous_digest={previous}")
        print(f"current_digest={current}")
        return 0

    if args.timeout_seconds <= 0 or args.retries < 0:
        raise SystemExit("timeout must be positive and retries must be non-negative")
    if args.required_services < 1 or args.required_services > 3:
        raise SystemExit("required-services must be between 1 and 3")
    result = archive_homepage(
        args.url,
        timeout=args.timeout_seconds,
        retries=args.retries,
        dry_run=args.dry_run,
        source_sha=args.source_sha,
        trigger=args.trigger,
    )
    write_result(args.output, result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if args.dry_run:
        return 0
    return 0 if result["accepted_service_count"] >= args.required_services else 1


if __name__ == "__main__":
    sys.exit(main())
