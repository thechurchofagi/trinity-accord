from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "discovery-indexnow.yml"


def workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def test_indexnow_waits_for_production_discovery_bytes() -> None:
    text = workflow_text()
    preflight = text.index("Wait for production discovery surfaces to match source byte-for-byte")
    submit = text.index("Submit high-signal discovery URLs")
    receipt = text.index("Publish public discovery receipt")
    assert preflight < submit < receipt
    assert "DISCOVERY LIVE PREFLIGHT PASS" in text
    assert "max_attempts = 30" in text
    assert "retry_seconds = 10" in text
    assert "FAILED after bounded production wait" in text
    assert "ThreadPoolExecutor" in text
    for path in (
        "/robots.txt",
        "/sitemap-discovery.xml",
        "/discovery.json",
        "/DISCOVERY.md",
        "/.well-known/agent.json",
    ):
        assert path in text


def test_indexnow_workflow_is_main_push_driven_and_publicly_observable() -> None:
    text = workflow_text()
    data = yaml.safe_load(text)
    assert data["permissions"] == {"contents": "read", "issues": "write"}
    triggers = data.get("on") or data.get(True)
    assert "push" in triggers
    assert "workflow_dispatch" in triggers
    assert "workflow_run" not in triggers
    assert "schedule" not in triggers
    assert triggers["push"]["branches"] == ["main"]
    paths = set(triggers["push"]["paths"])
    for path in (
        "robots.txt",
        "sitemap-discovery.xml",
        "discovery.json",
        "DISCOVERY.md",
        ".well-known/**",
        ".github/workflows/discovery-indexnow.yml",
        "scripts/submit_indexnow.py",
    ):
        assert path in paths
    assert data["concurrency"]["cancel-in-progress"] is True
    assert "discovery-indexnow-main" in data["concurrency"]["group"]
    job = data["jobs"]["submit-high-signal-urls"]
    assert job["timeout-minutes"] == 12
    assert 'DISCOVERY_STATUS_ISSUE: "1062"' in text
    assert "always()" in text
    assert "issues/{issue}/comments" in text
    assert "operational submission evidence only" in text
    assert "not proof of indexing, ranking, or endorsement" in text


def test_indexnow_push_source_is_exact_commit_not_workflow_run_metadata() -> None:
    text = workflow_text()
    assert "workflow_run" not in text
    assert "git rev-parse HEAD" in text
    assert 'mode=main-push-production-byte-gate' in text
    assert "production discovery bytes" in text
