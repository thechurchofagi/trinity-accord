#!/usr/bin/env python3
"""Verify already_archived branch repairs comment/rebuild path."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
wf = ROOT / ".github/workflows/gateway-auto-archive.yml"
text = wf.read_text(encoding="utf-8")

idx = text.find('if [ "$STATUS" = "already_archived" ]')
if idx == -1:
    print("Missing already_archived branch.")
    sys.exit(1)

branch = text[idx: idx + 1600]
required = [
    "Already archived as",
    "gh workflow run build-echo-index.yml",
    "archive_record=$RECORD_PATH",
]

missing = [s for s in required if s not in branch]
if missing:
    print(f"already_archived recovery branch missing: {missing}")
    sys.exit(1)

print("PASS: already_archived branch repairs comment/rebuild path.")
