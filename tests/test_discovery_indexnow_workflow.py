from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "discovery-indexnow.yml"


def workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def test_indexnow_waits_for_live_discovery_preflight() -> None:
    text = workflow_text()
    preflight = text.index("Verify deployed discovery surfaces byte-for-byte")
    submit = text.index("Submit high-signal discovery URLs")
    assert preflight < submit
    assert "DISCOVERY LIVE PREFLIGHT PASS" in text
    for path in (
        "/robots.txt",
        "/sitemap-discovery.xml",
        "/discovery.json",
        "/DISCOVERY.md",
        "/.well-known/agent.json",
    ):
        assert path in text


def test_indexnow_workflow_is_read_only_and_post_deploy_bounded() -> None:
    data = yaml.safe_load(workflow_text())
    assert data["permissions"] == {"contents": "read"}
    triggers = data.get("on") or data.get(True)
    assert "workflow_run" in triggers
    assert "workflow_dispatch" in triggers
    assert "schedule" not in triggers
    workflow_run = triggers["workflow_run"]
    assert workflow_run["workflows"] == ["Deploy Pages"]
    assert workflow_run["types"] == ["completed"]
