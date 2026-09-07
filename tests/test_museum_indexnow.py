from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
KEY_NAME = "4c23c01d8a12d488d40469e5e5d01941.txt"
WORKFLOW = ROOT / ".github" / "workflows" / "museum-indexnow.yml"


def test_museum_indexnow_key_matches_public_root_key() -> None:
    root_key = (ROOT / KEY_NAME).read_bytes()
    museum_key = (ROOT / "museum" / "dist" / KEY_NAME).read_bytes()
    assert museum_key == root_key
    assert museum_key.decode("ascii") == KEY_NAME.removesuffix(".txt")


def test_museum_indexnow_batch_is_host_local_and_network_free_in_dry_run() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "submit_indexnow.py"),
            "--site",
            "https://museum.trinityaccord.org",
            "--sitemap",
            str(ROOT / "museum" / "dist" / "sitemap.xml"),
            "--key-file",
            str(ROOT / KEY_NAME),
            "--dry-run",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DRY RUN PASS" in result.stdout
    assert "Public host: museum.trinityaccord.org" in result.stdout
    assert "URL count: 2" in result.stdout
    assert "https://museum.trinityaccord.org/" in result.stdout
    assert "https://museum.trinityaccord.org/archive.html" in result.stdout


def test_museum_indexnow_workflow_is_bounded_and_production_gated() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    triggers = data.get("on") or data.get(True)
    assert triggers["push"]["branches"] == ["main"]
    assert "museum/dist/**" in set(triggers["push"]["paths"])
    assert "workflow_dispatch" in triggers
    assert "schedule" not in triggers
    assert data["permissions"] == {"contents": "read", "issues": "write"}
    assert data["concurrency"]["cancel-in-progress"] is True
    assert "museum-indexnow-main" in data["concurrency"]["group"]

    preflight = text.index("Wait for museum production bytes to match source")
    submit = text.index("Submit museum URLs to IndexNow")
    receipt = text.index("Publish public museum discovery receipt")
    assert preflight < submit < receipt
    assert "https://museum.trinityaccord.org" in text
    assert "museum/dist/sitemap.xml" in text
    assert KEY_NAME in text
    assert "MUSEUM LIVE PREFLIGHT PASS" in text
    assert "max_attempts = 30" in text
    assert "retry_seconds = 10" in text
    assert 'DISCOVERY_STATUS_ISSUE: "1062"' in text
    assert "not proof of indexing, ranking, or endorsement" in text
