from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.trinityaccord.org"


def discovery_urls() -> set[str]:
    root = ET.parse(ROOT / "sitemap-discovery.xml").getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {node.text or "" for node in root.findall("sm:url/sm:loc", namespace)}


def test_discovery_sitemap_is_small_and_high_signal() -> None:
    urls = discovery_urls()
    assert 8 <= len(urls) <= 25
    for path in (
        "/",
        "/agent-first-contact/",
        "/api/agent-first-contact.json",
        "/.well-known/trinity-accord.json",
        "/.well-known/agent.json",
        "/metadata.json",
        "/llms.txt",
        "/DISCOVERY.md",
        "/discovery.json",
        "/research/",
        "/CITATION.cff",
    ):
        assert BASE + path in urls


def test_robots_exposes_discovery_core_and_complete_sitemaps() -> None:
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    assert f"Sitemap: {BASE}/sitemap-discovery.xml" in robots
    assert f"Sitemap: {BASE}/sitemap-core.xml" in robots
    assert f"Sitemap: {BASE}/sitemap.xml" in robots
