#!/usr/bin/env python3
"""Check that active public discovery surfaces do not route agents into retired paths."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str) -> dict:
    return json.loads(read(path))


def fail(message: str) -> None:
    errors.append(message)
    print(f"FAIL: {message}")


def ok(message: str) -> None:
    print(f"OK:   {message}")


links = load("api/links.json")
machine = set(links.get("machine", []))
legacy = set(links.get("legacy_machine", []))
deprecated = set(links.get("deprecated_for_new_records", []))

intersection = machine & deprecated
if intersection:
    fail(f"api/links.json active machine list intersects deprecated paths: {sorted(intersection)}")
else:
    ok("api/links.json active machine list excludes deprecated paths")

if "/api/agent-start.v2.json" not in machine:
    fail("api/links.json active machine list missing /api/agent-start.v2.json")
else:
    ok("api/links.json exposes active agent-start v2")

if "/api/agent-start.v1.json" in machine:
    fail("api/links.json active machine list still contains retired /api/agent-start.v1.json")
elif "/api/agent-start.v1.json" not in legacy and "/api/agent-start.v1.json" not in deprecated:
    fail("retired /api/agent-start.v1.json is not preserved as legacy/deprecated")
else:
    ok("agent-start v1 is preserved only as legacy/deprecated")

layout = read("_layouts/default.html")
nav_match = re.search(r'<div class="nav-links">(.*?)</div>', layout, flags=re.DOTALL)
footer_match = re.search(r'<nav class="footer-links">(.*?)</nav>', layout, flags=re.DOTALL)
nav = nav_match.group(1) if nav_match else ""
footer = footer_match.group(1) if footer_match else ""

for label, text in (("top navigation", nav), ("footer", footer)):
    if 'href="/agent-submit"' in text:
        fail(f"{label} actively links to retired /agent-submit")
    else:
        ok(f"{label} does not actively link to /agent-submit")

if 'href="/api/agent-submit-gateway.json"' in footer:
    fail("footer Gateway API points to retired /api/agent-submit-gateway.json")
else:
    ok("footer Gateway API does not point to retired API")

if 'href="/agent-first-contact/">First Contact</a>' not in nav:
    fail("top navigation missing active First Contact route")
else:
    ok("top navigation exposes First Contact")

entry = load("api/agent-entry-protocol.json")
fallback = entry.get("no_github_access_fallback", {})
if fallback.get("path") == "/agent-submit" or fallback.get("machine_readable") == "/api/agent-submit-gateway.json":
    fail("agent-entry-protocol no-GitHub fallback still routes to retired Gateway v1")
else:
    ok("agent-entry-protocol no-GitHub fallback uses current Record-Chain route")

agent_map = load("agent-map.json")
if agent_map.get("homepage_only_policy", {}).get("context_depth") != "CC-0":
    fail("agent-map homepage_only_policy context_depth is not CC-0")
else:
    ok("agent-map homepage-only context depth is CC-0")

if errors:
    print(f"\nRESULT: FAIL ({len(errors)} errors)")
    sys.exit(1)
print("\nRESULT: PASS")
