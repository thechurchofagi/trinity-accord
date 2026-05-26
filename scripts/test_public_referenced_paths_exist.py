#!/usr/bin/env python3
"""Validate local public paths referenced inside core public JSON files."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CORE_JSON = [
    "api/agent-minimal-context.v1.json",
    "api/agent-output-policy.v1.json",
    "api/agent-task-router.v1.json",
    "api/agent-start.v1.json",
    "api/context-load-map.json",
    "api/gateway-builder-route-map.v1.json",
    "api/public-home-status.json",

    # Additional machine entrypoints / link roots.
    "api/agent-required-reading.json",
    "api/agent-entry-protocol.json",
    "api/agent-tasks.json",
    "api/links.json",
    "api/gateway-workflows.v1.json",
    "api/guardian-active-listing-policy.v1.json",
    "api/external-agent-quickstart.json",
    "api/agent-submit-gateway.json",
]

IGNORE_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
)

# Natural language markers / anchors that are not direct files.
IGNORE_VALUES = {
    "CC-1 loads (inherited)",
    "CC-2 loads (inherited)",
    "CC-3 loads (inherited)",
    "CC-4 loads (inherited)",
    "Gateway workflow overview",
    "Task-specific API schemas and verification recipes",
    "/gateway/preflight",
    "/healthz",
    "/readiness",
    "/chronicle/music",
    "/chronicle/human-witness",
    "/recovery",
}

def extract_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for x in obj:
            yield from extract_strings(x)
    elif isinstance(obj, dict):
        for x in obj.values():
            yield from extract_strings(x)

def normalize_public_path(value: str) -> str | None:
    value = value.strip()
    if not value or value in IGNORE_VALUES:
        return None
    if value.startswith(IGNORE_PREFIXES):
        return None

    # Split "path — description" style entries.
    value = re.split(r"\s+[—-]\s+", value, maxsplit=1)[0].strip()

    # Drop anchors/fragments.
    value = value.split("#", 1)[0].strip()

    # Only validate local public-looking paths.
    if value.startswith("/"):
        # Gateway service endpoints are not static files.
        if value.startswith("/gateway/"):
            return None
        return value

    # context-packs/foo.json in context-load-map means /api/context-packs/foo.json.
    if value.startswith("context-packs/"):
        return "/api/" + value

    # scripts are repository paths, not public pages.
    if value.startswith("scripts/"):
        return None

    return None

def candidates(path: str) -> list[Path]:
    p = path.lstrip("/")
    if not p:
        return [ROOT / "index.md", ROOT / "index.html"]

    if "." in Path(p).name:
        return [ROOT / p]

    clean = p.rstrip("/")
    return [
        ROOT / clean / "index.md",
        ROOT / clean / "index.html",
        ROOT / f"{clean}.md",
        ROOT / f"{clean}.html",
    ]

errors = []

for rel in CORE_JSON:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"core JSON missing: {rel}")
        continue
    data = json.loads(path.read_text(encoding="utf-8"))

    for s in extract_strings(data):
        public_path = normalize_public_path(s)
        if not public_path:
            continue
        if not any(c.exists() for c in candidates(public_path)):
            errors.append(f"{rel}: referenced public path missing: {public_path} from {s!r}")

if errors:
    print("FAIL: public referenced path errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: core public JSON references resolve to local sources/artifacts")
