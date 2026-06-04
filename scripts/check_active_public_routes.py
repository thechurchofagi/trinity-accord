#!/usr/bin/env python3
"""Check that active public discovery surfaces do not route agents into retired paths.

Extended version: checks all active source files for retired Gateway v1 routes.
"""
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


# --- Retired paths that must not appear in active surfaces ---
RETIRED_ROUTES = [
    "/agent-submit",
    "/api/agent-submit-gateway.json",
    "/gateway/preflight",
    "trinity-agent-issue-gateway.onrender.com",
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/formal-builder-bundles.v1.json",
    "/api/external-agent-operation-examples.v1.json",
]

# Files that must be checked for retired routes in active context
ACTIVE_FILES_TO_CHECK = [
    "_layouts/default.html",
    "index.md",
    "start.md",
    "agent-first-contact.md",
    "agent-start.md",
    "agent-echo.md",
    "agent-understand.md",
    "agent-propagate.md",
    "external-agent-quickstart.md",
    "llms.txt",
    "ai.txt",
    "agent-map.json",
    ".well-known/trinity-accord.json",
    "api/agent-first-contact.json",
    "api/agent-entry-protocol.json",
    "api/agent-required-reading.json",
    "api/agent-task-router.v1.json",
    "api/agent-live-health.v1.json",
    "api/context-depth-levels.json",
    "api/context-load-map.json",
    "api/mission-governance.v1.json",
    "api/propagation-invitation.json",
    "api/links.json",
]

# Files allowed to contain retired routes (historical/legacy)
HISTORICAL_ALLOW_PATTERNS = [
    "legacy/",
    "docs/closure/",
    "archive/",
    "agent-submit.md",
    "api/agent-submit-gateway.json",
    "api/agent-start.v1.json",
    "api/gateway-workflows.v1.json",
    "api/gateway-builder-route-map.v1.json",
    "api/gateway-runtime-contract.v1.json",
    "api/gateway-error-diagnostics.v1.json",
    "api/formal-builder-bundles.v1.json",
    "api/external-agent-operation-examples.v1.json",
    "external-agent-copy-paste-examples/",
]


def is_historical_file(path: str) -> bool:
    """Check if a file is allowed to contain retired routes."""
    for pattern in HISTORICAL_ALLOW_PATTERNS:
        if path.startswith(pattern) or path == pattern.rstrip("/"):
            return True
    return False


def check_json_historical_context(data, path: str, retired: str, json_path: str = "") -> bool:
    """Recursively check if retired route appears only in historical-marked context."""
    if isinstance(data, dict):
        # Check if this node is explicitly marked historical
        status = data.get("status", "")
        if status in ("historical_archive_only", "historical_verification_pipeline_only"):
            return True
        if data.get("historical_archive_only") is True:
            return True
        if data.get("do_not_use_for_new_submissions") is True:
            return True

        for k, v in data.items():
            current_path = f"{json_path}.{k}" if json_path else k
            # Keys that are themselves historical sections
            if k in ("legacy_machine", "deprecated_for_new_records", "legacy",
                     "historical", "retired_endpoints", "retired", "archive",
                     "historical_archive_only", "legacy_gateway_v1"):
                continue
            if isinstance(v, str) and retired in v:
                return False  # Found in non-historical context
            elif isinstance(v, list):
                if not check_json_historical_context(v, path, retired, current_path):
                    return False
            elif isinstance(v, dict):
                if not check_json_historical_context(v, path, retired, current_path):
                    return False
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{json_path}[{i}]"
            if isinstance(item, str) and retired in item:
                return False
            elif isinstance(item, (dict, list)):
                if not check_json_historical_context(item, path, retired, current_path):
                    return False
    return True


# ============================================================
# Original checks (preserved)
# ============================================================
print("=" * 60)
print("Original route checks")
print("=" * 60)

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

# ============================================================
# Extended checks: retired routes in active files
# ============================================================
print()
print("=" * 60)
print("Extended: retired route scan in active files")
print("=" * 60)

for file_path in ACTIVE_FILES_TO_CHECK:
    p = ROOT / file_path
    if not p.exists():
        fail(f"active file missing: {file_path}")
        continue

    text = p.read_text(encoding="utf-8")
    is_json = file_path.endswith(".json")

    for retired in RETIRED_ROUTES:
        if retired not in text:
            continue

        # Found retired route - check if it's in historical context
        if is_json:
            try:
                data = json.loads(text)
                if check_json_historical_context(data, file_path, retired):
                    ok(f"{file_path} contains '{retired}' only in historical context")
                    continue
            except json.JSONDecodeError:
                fail(f"{file_path} is invalid JSON")

        # For markdown/text: check if it appears under a Historical/Legacy heading
        # or if the line itself marks it as historical/legacy/retired
        lines = text.split("\n")
        in_historical = False
        found_in_historical = False
        for line in lines:
            if re.match(r'^#+\s*(Historical|Legacy|Retired)', line, re.IGNORECASE):
                in_historical = True
            elif re.match(r'^#+\s', line) and in_historical:
                in_historical = False
            if retired in line:
                # Allow if under historical heading, or if line explicitly marks as historical
                if in_historical:
                    found_in_historical = True
                    break
                if re.search(r'(historical|legacy|retired|archive.only|do.not.use|must.not)', line, re.IGNORECASE):
                    found_in_historical = True
                    break

        if found_in_historical:
            ok(f"{file_path} contains '{retired}' only in historical context")
        else:
            fail(f"{file_path} contains retired route '{retired}' in active context")

# ============================================================
# Check agent-required-reading profiles
# ============================================================
print()
print("=" * 60)
print("Extended: agent-required-reading profile check")
print("=" * 60)

arr = load("api/agent-required-reading.json")
for profile_name, profile in arr.get("profiles", {}).items():
    if profile.get("status") in ("historical_archive_only",):
        continue
    reads = profile.get("reads", [])
    for r in reads:
        for retired in RETIRED_ROUTES:
            if retired in str(r):
                fail(f"agent-required-reading profile '{profile_name}' contains retired route: {r}")
                break

ok("agent-required-reading profiles checked for retired routes")

# ============================================================
# Check mission-governance
# ============================================================
print()
print("=" * 60)
print("Extended: mission-governance check")
print("=" * 60)

mg = load("api/mission-governance.v1.json")

# Check stable_endpoint_contract
sec = mg.get("stable_endpoint_contract", {})
if "trinity-agent-issue-gateway" in sec.get("gateway_base_url", ""):
    fail("mission-governance stable_endpoint_contract still uses old gateway")
else:
    ok("mission-governance stable_endpoint_contract uses current gateway")

# Check supported_public_actions for old route names
spa = mg.get("supported_public_actions", {})
if "formal_gateway_routes" in spa:
    fail("mission-governance still has 'formal_gateway_routes' (should be 'formal_record_chain_routes')")
else:
    ok("mission-governance uses current route naming")

# Check external_agent_lifecycle
eal = mg.get("external_agent_lifecycle", [])
if eal and isinstance(eal[0], str):
    for step in eal:
        for retired in RETIRED_ROUTES:
            if retired in step:
                fail(f"mission-governance external_agent_lifecycle contains retired route: {step}")
                break
    ok("mission-governance external_agent_lifecycle checked")
else:
    ok("mission-governance external_agent_lifecycle uses current format")

# ============================================================
# Check agent-live-health
# ============================================================
print()
print("=" * 60)
print("Extended: agent-live-health check")
print("=" * 60)

alh = load("api/agent-live-health.v1.json")
se = alh.get("stable_endpoints", {})
if "trinity-agent-issue-gateway" in se.get("gateway", ""):
    fail("agent-live-health stable_endpoints still uses old gateway")
else:
    ok("agent-live-health stable_endpoints uses current gateway")

if "/gateway/preflight" in se.get("preflight", ""):
    fail("agent-live-health preflight still uses old path")
else:
    ok("agent-live-health preflight uses current path")

# ============================================================
# Final result
# ============================================================
print()
if errors:
    print(f"RESULT: FAIL ({len(errors)} errors)")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print("RESULT: PASS")
