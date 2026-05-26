#!/usr/bin/env python3
"""Diagnose mismatch between repository discovery source and live Pages JSON.

v19: compares canonical and cache-busted live JSON to detect CDN/edge inconsistency.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.trinityaccord.org"


def fetch_json(path: str) -> Any:
    url = SITE.rstrip("/") + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "trinity-accord-pages-diagnose/1.0",
            "Accept": "application/json,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def with_cache_bust(path: str, token: str) -> str:
    sep = "&" if "?" in path else "?"
    return f"{path}{sep}cb={urllib.parse.quote(token)}"


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    local_links = load_json("api/links.json")
    local_wk = load_json(".well-known/trinity-accord.json")

    token = str(local_links.get("source_digest") or int(time.time()))

    live_links = fetch_json("/api/links.json")
    live_links_busted = fetch_json(with_cache_bust("/api/links.json", token))
    live_wk = fetch_json("/.well-known/trinity-accord.json")
    live_wk_busted = fetch_json(with_cache_bust("/.well-known/trinity-accord.json", token))

    print("== links.json ==")
    print("local source_digest:", local_links.get("source_digest"))
    print("live canonical source_digest:", live_links.get("source_digest"))
    print("live cache-busted source_digest:", live_links_busted.get("source_digest"))

    if live_links.get("source_digest") != live_links_busted.get("source_digest"):
        print("FAIL: canonical and cache-busted live links.json differ; likely CDN/edge/cache split")
        return 1

    local_machine = set(local_links.get("machine", []))
    live_machine = set(live_links.get("machine", []))
    print("machine entries missing live:", sorted(local_machine - live_machine))
    print("machine entries extra live:", sorted(live_machine - local_machine))

    local_pages = set(local_links.get("key_pages", []))
    live_pages = set(live_links.get("key_pages", []))
    print("key_pages missing live:", sorted(local_pages - live_pages))
    print("key_pages extra live:", sorted(live_pages - local_pages))

    print("\n== .well-known/trinity-accord.json ==")
    for key in [
        "agent_first_contact",
        "gateway_workflows",
        "gateway_workflows_json",
        "agent_submit_gateway",
        "gateway_builder_route_map",
    ]:
        print(f"{key}: local={local_wk.get(key)!r} live={live_wk.get(key)!r}")

    local_api = local_wk.get("api", {})
    live_api = live_wk.get("api", {})
    for key in [
        "agent_first_contact",
        "gateway_workflows",
        "agent_submit_gateway",
        "gateway_builder_route_map",
    ]:
        print(f"api.{key}: local={local_api.get(key)!r} live={live_api.get(key)!r}")

    if local_links.get("source_digest") != live_links.get("source_digest"):
        print("\nFAIL: live Pages discovery is stale or serving a different artifact")
        return 1

    print("\nPASS: live Pages discovery source_digest matches local source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
