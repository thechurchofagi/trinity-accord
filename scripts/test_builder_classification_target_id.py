#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
builder = ROOT / "downloads" / "record-chain-builder.mjs"
cmd = [
    "node", str(builder), "classification-update",
    "--target-record-id", "not-a-record",
    "--target-record-sha256", "a" * 64,
    "--previous-classification", "old",
    "--new-classification", "new",
    "--classification-reason", "review",
    "--evidence-or-review-basis", "fresh review",
    "--context-level", "CC-2",
    "--context-read-confirmed", "true",
    "--loaded-urls", "https://www.trinityaccord.org/api/context-load-map.json",
    "--discovery-mode", "user_task_context",
    "--record-decision", "mixed",
    "--submission-executor", "self",
    "--requesting-party-type", "human",
    "--introducing-party-type", "human",
    "--human-operator-involved", "false",
    "--context-sufficient-for-selected-action", "true",
]
result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
combined = result.stdout + result.stderr
if result.returncode == 0:
    raise SystemExit("Builder accepted a noncanonical classification target_record_id")
if "--target-record-id must match R-XXXXXXXXX format" not in combined:
    raise SystemExit(f"Builder failed for the wrong reason:
{combined}")
print("PASS: Builder rejects noncanonical classification target_record_id")
