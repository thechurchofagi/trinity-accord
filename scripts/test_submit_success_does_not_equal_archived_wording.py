#!/usr/bin/env python3
"""Docs/API must not imply issue_created/archive_ready equals archived/public update."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "gateway-workflows.md",
    ROOT / "api" / "gateway-workflows.v1.json",
    ROOT / "api" / "agent-output-policy.v1.json",
    ROOT / "api" / "agent-first-contact.json",
    ROOT / "api" / "agent-task-router.v1.json",
]

forbidden_phrases = [
    "issue_created means archived",
    "issue_created means the archive is complete",
    "archive_ready means archived",
    "archive_ready=true means archived",
    "Gateway accepted means verified",
    "Stage 1 means active Guardian",
    "Stage 2 submission means active Guardian",
]

errors = []

for path in FILES:
    text = path.read_text(encoding="utf-8")
    # For JSON, normalize to text too.
    if path.suffix == ".json":
        try:
            text = json.dumps(json.loads(text))
        except Exception:
            pass

    for phrase in forbidden_phrases:
        if phrase.lower() in text.lower():
            errors.append(f"{path.relative_to(ROOT)} contains forbidden phrase: {phrase}")

if errors:
    print("FAIL: submit success / archive wording errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: docs/API do not equate issue_created/archive_ready with archived")
