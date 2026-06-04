#!/usr/bin/env python3
"""Check active public discovery surfaces for retired/historical routes.

The scan is occurrence-based: one historical mention in a file does not make a
second active mention safe. JSON scans also recurse through every value and only
suppress findings in explicitly historical subtrees.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

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
    "/zero-clone-builders/",
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
    "zero-clone-builders.md",
]

HISTORICAL_JSON_KEYS = {
    "legacy_machine",
    "deprecated_for_new_records",
    "legacy",
    "historical",
    "retired_endpoints",
    "retired",
    "archive",
    "historical_archive_only",
    "legacy_gateway_v1",
    "historical_gateway_v1_inputs",
    "_legacy_note",
}

HISTORICAL_STATUSES = {
    "historical_archive_only",
    "historical_verification_pipeline_only",
    "deprecated_for_new_records",
    "legacy_gateway_v1",
}

HISTORICAL_LINE_RE = re.compile(
    r"(historical|legacy|retired|archive[ -]?only|deprecated|do not use|must not use|not for new)",
    re.IGNORECASE,
)


def is_historical_file(path: str) -> bool:
    """Check if a file is allowed to contain retired routes."""
    for pattern in HISTORICAL_ALLOW_PATTERNS:
        if path.startswith(pattern) or path == pattern.rstrip("/"):
            return True
    return False


def json_node_is_historical(data: dict[str, Any]) -> bool:
    """Return True when a JSON object explicitly marks its whole subtree historical."""
    status = str(data.get("status", ""))
    return (
        status in HISTORICAL_STATUSES
        or data.get("historical_archive_only") is True
        or data.get("do_not_use_for_new_submissions") is True
    )


def find_active_json_occurrences(
    data: Any,
    retired: str,
    json_path: str = "$",
    in_historical_context: bool = False,
) -> list[str]:
    """Return JSON paths where a retired route appears outside historical context."""
    findings: list[str] = []
    if isinstance(data, dict):
        node_historical = in_historical_context or json_node_is_historical(data)
        for key, value in data.items():
            child_path = f"{json_path}.{key}"
            child_historical = node_historical or key in HISTORICAL_JSON_KEYS
            if isinstance(value, str):
                if retired in value and not child_historical:
                    findings.append(child_path)
            else:
                findings.extend(find_active_json_occurrences(value, retired, child_path, child_historical))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            child_path = f"{json_path}[{index}]"
            if isinstance(item, str):
                if retired in item and not in_historical_context:
                    findings.append(child_path)
            else:
                findings.extend(find_active_json_occurrences(item, retired, child_path, in_historical_context))
    return findings


def line_is_heading(line: str) -> re.Match[str] | None:
    return re.match(r"^(#{1,6})\s+(.+?)\s*$", line)


def find_active_text_occurrences(text: str, retired: str) -> list[int]:
    """Return 1-indexed line numbers where a retired route appears in active text."""
    findings: list[int] = []
    # Stack entries are (heading_level, is_historical_scope).
    heading_stack: list[tuple[int, bool]] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        heading = line_is_heading(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2)
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            parent_historical = any(item[1] for item in heading_stack)
            heading_stack.append((level, parent_historical or bool(HISTORICAL_LINE_RE.search(title))))

        if retired not in line:
            continue

        in_historical_section = any(item[1] for item in heading_stack)
        line_marks_historical = bool(HISTORICAL_LINE_RE.search(line))
        if not (in_historical_section or line_marks_historical):
            findings.append(lineno)
    return findings


def check_retired_routes_in_active_files() -> None:
    for file_path in ACTIVE_FILES_TO_CHECK:
        p = ROOT / file_path
        if not p.exists():
            fail(f"active file missing: {file_path}")
            continue

        if is_historical_file(file_path):
            ok(f"{file_path} is a historical file; retired-route scan skipped")
            continue

        text = p.read_text(encoding="utf-8")
        is_json = file_path.endswith(".json")

        for retired in RETIRED_ROUTES:
            if retired not in text:
                continue

            if is_json:
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    fail(f"{file_path} is invalid JSON")
                    continue
                findings = find_active_json_occurrences(data, retired)
                if findings:
                    for finding in findings:
                        fail(f"{file_path} contains retired route '{retired}' in active JSON context at {finding}")
                else:
                    ok(f"{file_path} contains '{retired}' only in historical JSON context")
                continue

            findings = find_active_text_occurrences(text, retired)
            if findings:
                for lineno in findings:
                    fail(f"{file_path}:{lineno} contains retired route '{retired}' in active context")
            else:
                ok(f"{file_path} contains '{retired}' only in historical text context")


def run_regression_self_tests() -> None:
    mixed_text = """# Current\nUse /agent-submit now.\n## Legacy Gateway v1\n/agent-submit is historical only.\n"""
    if find_active_text_occurrences(mixed_text, "/agent-submit") != [2]:
        fail("regression: mixed historical/active markdown route was not detected line-by-line")
    else:
        ok("regression: mixed historical/active markdown route detected line-by-line")

    mixed_json = {
        "active": {"submit": "/agent-submit"},
        "historical_gateway_v1_inputs": {"submit": "/agent-submit"},
    }
    if find_active_json_occurrences(mixed_json, "/agent-submit") != ["$.active.submit"]:
        fail("regression: mixed historical/active JSON route was not detected per occurrence")
    else:
        ok("regression: mixed historical/active JSON route detected per occurrence")


def main() -> int:
    errors.clear()
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

    print()
    print("=" * 60)
    print("Regression: occurrence-scoped retired route detection")
    print("=" * 60)
    run_regression_self_tests()

    print()
    print("=" * 60)
    print("Extended: retired route scan in active files")
    print("=" * 60)
    check_retired_routes_in_active_files()

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

    sec = mg.get("stable_endpoint_contract", {})
    if "trinity-agent-issue-gateway" in sec.get("gateway_base_url", ""):
        fail("mission-governance stable_endpoint_contract still uses old gateway")
    else:
        ok("mission-governance stable_endpoint_contract uses current gateway")

    spa = mg.get("supported_public_actions", {})
    if "formal_gateway_routes" in spa:
        fail("mission-governance still has 'formal_gateway_routes' (should be 'formal_record_chain_routes')")
    else:
        ok("mission-governance uses current route naming")

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

    print()
    if errors:
        print(f"RESULT: FAIL ({len(errors)} errors)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
