#!/usr/bin/env python3
"""Test that active Worker src has no legacy submit logic.

RF-005: Worker deprecation test should scan active src full directory.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_SRC = ROOT / "trinity-echo-worker" / "src"

FORBIDDEN = [
    "createGitHubIssue",
    "trinity-accord.echo-schema.v1",
    "Verify the flaw. Trust the story.",
    "VALID_ECHO_TYPES = ['verification'",
    "blessing",
    "handlePostSubmit(",
    "TURNSTILE_SECRET",
    "RATE_LIMIT_KV",
    "GITHUB_TOKEN",
    "claimed_verification_level",
    '<option value="L0">',
]

errors = []

if not ACTIVE_SRC.exists():
    print("SKIP: trinity-echo-worker/src/ not found")
    sys.exit(0)

for path in ACTIVE_SRC.rglob("*.js"):
    text = path.read_text(encoding="utf-8")
    for phrase in FORBIDDEN:
        if phrase in text:
            errors.append(f"{path.relative_to(ROOT)} contains forbidden legacy phrase: {phrase}")

# Current active Worker may mention POST only to return 410.
index = ACTIVE_SRC / "index.js"
if not index.exists():
    errors.append("trinity-echo-worker/src/index.js missing")
else:
    text = index.read_text(encoding="utf-8")
    required = [
        "Worker submission is deprecated",
        "current_submission_path",
        "claim_gate_required_for_technical_claims",
        "return jsonResponse",
        "410",
    ]
    for phrase in required:
        if phrase not in text:
            errors.append(f"index.js missing required tombstone phrase: {phrase}")

if errors:
    print("DEPRECATED_WORKER_LEGACY_SCAN_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("DEPRECATED_WORKER_LEGACY_SCAN_OK")
