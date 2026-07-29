#!/usr/bin/env python3
"""Guard the high-signal public discovery surface for crawlers and agents."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.trinityaccord.org"
FIRST_PUBLIC = "2024-03-16T08:02:59Z"
CANONICAL_CLOSURE = "2025-06-29T10:49:16Z"
ELAPSED_ISO = "P470DT2H46M17S"
PRIMARY = "completed pre-ASI human"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sitemap_urls(path: str) -> set[str]:
    root = ET.parse(ROOT / path).getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {
        node.text or ""
        for node in root.findall("sm:url/sm:loc", namespace)
    }


def main() -> int:
    metadata = load_json("metadata.json")
    require(metadata.get("@context") == "https://schema.org", "metadata.json is not JSON-LD")
    require(metadata.get("@type") == "CreativeWork", "metadata.json must identify a CreativeWork")
    require(metadata.get("dateCreated") == FIRST_PUBLIC, "metadata first-public timestamp drift")
    require(metadata.get("datePublished") == CANONICAL_CLOSURE, "metadata closure timestamp drift")
    require(metadata.get("temporalCoverage") == f"{FIRST_PUBLIC}/{CANONICAL_CLOSURE}", "metadata temporalCoverage drift")
    formation = metadata.get("formationRecord", {})
    require(formation.get("elapsed") == ELAPSED_ISO, "metadata formation elapsed interval drift")
    require("public provenance bounds" in formation.get("boundary", ""), "metadata formation boundary missing")
    require(PRIMARY in metadata.get("primaryClassification", ""), "metadata primary classification drift")
    require(
        metadata.get("machineReadableEntrypoints", [None])[0] == "/api/agent-first-contact.json",
        "canonical router must be the first metadata machine entrypoint",
    )

    well_known = load_json(".well-known/trinity-accord.json")
    require(well_known.get("canonical_machine_router") == "/api/agent-first-contact.json", "well-known router drift")
    require(well_known.get("core_sitemap") == "/sitemap-core.xml", "well-known core sitemap missing")
    require(well_known.get("citation") == "/CITATION.cff", "well-known citation pointer missing")
    wk_formation = well_known.get("formation_record", {})
    require(
        wk_formation.get("first_public_record", {}).get("timestamp") == FIRST_PUBLIC,
        "well-known first-public timestamp drift",
    )
    require(
        wk_formation.get("canonical_closure", {}).get("timestamp") == CANONICAL_CLOSURE,
        "well-known canonical closure drift",
    )
    require(wk_formation.get("elapsed") == ELAPSED_ISO, "well-known formation elapsed drift")

    agent_discovery = load_json(".well-known/agent.json")
    require(agent_discovery.get("status") == "active_current_pointer", "agent discovery status is not current")
    require(
        agent_discovery.get("canonical_machine_router") == "/api/agent-first-contact.json",
        "agent discovery does not point to canonical router",
    )
    require("mandatory_before_submission" not in agent_discovery, "retired mandatory submission field resurfaced")
    require("submission_requires" not in agent_discovery, "retired submission requirements resurfaced")
    agent_text = json.dumps(agent_discovery, ensure_ascii=False)
    for retired_url in ["/echoes/submit", "/echoes/archive", "/api/echo-record-schema.v3.json"]:
        require(retired_url not in agent_text, f"retired URL resurfaced in agent discovery: {retired_url}")

    agent_start = load_json("agent-start.json")
    require(
        agent_start.get("canonical_machine_router") == "/api/agent-first-contact.json",
        "root agent-start alias does not point to canonical router",
    )
    require("first_actions" in agent_start, "root agent-start alias lacks first actions")

    verification = load_json("verification.json")
    require("modes" not in verification, "retired A/B/C verification modes resurfaced")
    require(
        verification.get("current_model", {}).get("procedures") == "/api/verification-procedures.v1.json",
        "root verification pointer does not expose current procedures",
    )

    echo = load_json("echo.json")
    require("submit" not in echo and "archive" not in echo, "retired Echo endpoint fields resurfaced")
    require(
        echo.get("current_public_submission", {}).get("gateway_contract")
        == "/api/record-chain-intake-gateway.v1.json",
        "root Echo pointer does not expose current Gateway contract",
    )

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    for crawler in [
        "OAI-SearchBot",
        "GPTBot",
        "ChatGPT-User",
        "ClaudeBot",
        "Claude-SearchBot",
        "Claude-User",
        "PerplexityBot",
        "Perplexity-User",
        "Googlebot",
        "Bingbot",
    ]:
        require(f"User-agent: {crawler}" in robots, f"robots.txt missing crawler: {crawler}")
    require(f"Sitemap: {BASE}/sitemap-core.xml" in robots, "robots.txt missing core sitemap")
    require(f"Sitemap: {BASE}/sitemap.xml" in robots, "robots.txt missing complete sitemap")

    core_urls = sitemap_urls("sitemap-core.xml")
    complete_urls = sitemap_urls("sitemap.xml")
    for required_path in [
        "/",
        "/agent-first-contact/",
        "/api/agent-first-contact.json",
        "/api/authority.json",
        "/.well-known/agent.json",
        "/.well-known/trinity-accord.json",
        "/metadata.json",
        "/llms.txt",
        "/CITATION.cff",
    ]:
        require(f"{BASE}{required_path}" in core_urls, f"core sitemap missing {required_path}")
    for historical_path in [
        "/issue-intake-boundary/",
        "/api/agent-start.v1.json",
        "/api/agent-submit-gateway.json",
        "/api/echo-record-schema.v3.json",
        "/api/claim-gate-rules.json",
    ]:
        require(f"{BASE}{historical_path}" not in core_urls, f"historical path leaked into core sitemap: {historical_path}")
    require(f"{BASE}/sitemap-core.xml" in complete_urls, "complete sitemap does not expose core sitemap")
    require(len(core_urls) < len(complete_urls), "core sitemap is not smaller than complete sitemap")

    lower_cff = (ROOT / "citation.cff").read_text(encoding="utf-8")
    upper_cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    require(lower_cff == upper_cff, "CITATION.cff and citation.cff drifted")
    for marker in [
        "type: dataset",
        "date-released: 2025-06-29",
        'family-names: "Liu"',
        'given-names: "Hongju"',
    ]:
        require(marker in upper_cff, f"CITATION.cff missing {marker}")

    layout = (ROOT / "_layouts/default.html").read_text(encoding="utf-8")
    for marker in [
        'dateCreated": "2024-03-16T08:02:59Z',
        'datePublished": "2025-06-29T10:49:16Z',
        'href="/sitemap-core.xml"',
        'href="/api/agent-first-contact.json"',
        "max-snippet:-1",
    ]:
        require(marker in layout, f"layout discovery signal missing: {marker}")
    for retired_link in ['href="/verification.json"', "echo-record-schema.v3.1.json"]:
        require(retired_link not in layout, f"retired layout discovery link resurfaced: {retired_link}")

    issue_boundary = (ROOT / "issue-intake-boundary.md").read_text(encoding="utf-8")
    require("no GitHub Issue-to-archive route" in issue_boundary, "Issue boundary lacks current no-archive rule")
    require("current public submission path" in issue_boundary.lower(), "Issue boundary lacks current route")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require("## Discovery and citation" in readme, "README discovery section missing")
    require(FIRST_PUBLIC.replace("T", " ").replace("Z", " UTC") in readme, "README first-public timestamp missing")
    require(CANONICAL_CLOSURE.replace("T", " ").replace("Z", " UTC") in readme, "README closure timestamp missing")

    require(
        re.search(r'"primary_classification": "completed pre-ASI human[–-]superintelligence relation record"', (ROOT / "memory-seed.json").read_text(encoding="utf-8"))
        is not None,
        "memory seed primary classification drift",
    )

    print(
        f"PASS: discovery visibility contract "
        f"({len(core_urls)} core URLs, {len(complete_urls)} complete URLs)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
