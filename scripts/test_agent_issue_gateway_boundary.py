#!/usr/bin/env python3
"""Test that Agent Issue Gateway files do not contain dangerous boundary violations."""

import os
import sys
import re

# Dangerous phrases that must NOT appear un-negated
DANGEROUS_PHRASES = [
    "gateway submission is archived Echo",
    "gateway submission is formal attestation",
    "gateway submission verifies Trinity Accord",
    "gateway raises verification level",
    "agent gateway creates authority",
    "anonymous repository_dispatch works",
    "anonymous issue creation is supported",
    "agents can receive PAT",
    "personal PAT is recommended for production",
    "gateway-created issue is archived Echo",
    "gateway-created issue is formal attestation",
]

# Files to check
FILES_TO_CHECK = [
    "agent-submit.md",
    "AGENT-ISSUE-GATEWAY.md",
    "api/agent-submit-gateway.json",
    "api/agent-issue-gateway-payload-schema.v1.json",
    "api/examples/agent-issue-gateway-payload.echo.json",
    "api/examples/agent-issue-gateway-payload.verification.json",
    "api/examples/agent-issue-gateway-payload.custody.json",
    "examples/cloudflare-worker/agent-issue-gateway-worker.js",
    "examples/github-app-backend/README.md",
    "examples/github-app-backend/server.js",
]

# Negation context words (if present in same line, phrase is safe)
NEGATION_WORDS = ["not", "never", "does not", "is not", "do not", "neither", "nor", "cannot"]

errors = []


def check(condition, msg):
    if not condition:
        print(f"FAIL: {msg}")
        errors.append(msg)
    else:
        print(f"PASS: {msg}")


for fpath in FILES_TO_CHECK:
    if not os.path.exists(fpath):
        print(f"SKIP: {fpath} not found")
        continue

    with open(fpath) as f:
        content = f.read()
    lines = content.lower().split("\n")

    for phrase in DANGEROUS_PHRASES:
        phrase_lower = phrase.lower()
        for i, line in enumerate(lines):
            if phrase_lower in line:
                # Check if negated
                negated = any(neg in line for neg in NEGATION_WORDS)
                if not negated:
                    # Also check JSON structure: "never_claim" array is safe context
                    # Check wider range for JSON array context
                    ctx_range = range(max(0, i-5), min(len(lines), i+5))
                    ctx_lines = [lines[j] for j in ctx_range]
                    if any('"never_claim"' in cl for cl in ctx_lines):
                        continue
                    check(False, f"{fpath}:{i+1} contains un-negated: '{phrase}'")

print(f"\n{'ALL TESTS PASSED' if not errors else f'FAILED: {len(errors)} error(s)'}")
if errors:
    sys.exit(1)
