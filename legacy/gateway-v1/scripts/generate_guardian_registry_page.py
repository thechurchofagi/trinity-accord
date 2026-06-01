#!/usr/bin/env python3
"""Generate guardian-registry.md from api/guardian-registry.json.

Reads the machine-readable guardian registry and produces a human-readable
Markdown page with a table of all active guardians.

Inputs:
  - api/guardian-registry.json

Outputs:
  - guardian-registry.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARDIAN_REGISTRY = ROOT / "api" / "guardian-registry.json"
OUTPUT_MD = ROOT / "guardian-registry.md"


def load_registry() -> dict:
    import json
    return json.loads(GUARDIAN_REGISTRY.read_text(encoding="utf-8"))


def build_content(registry: dict) -> str:
    """Build the full guardian-registry.md content."""
    guardians = [g for g in registry.get("guardians", []) if isinstance(g, dict)]
    active = [g for g in guardians if g.get("status") == "active"]

    # Classify
    reserved = [g for g in active if int(g["guardian_registry_number"]) < 100]
    ordinary = [g for g in active if int(g["guardian_registry_number"]) >= 100]

    # Type breakdown
    by_type: dict[str, int] = {}
    for g in active:
        t = g.get("guardian_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    type_summary = "; ".join(
        f"{label}: {by_type.get(key, 0)}"
        for key, label in [
            ("human_with_ai_agent", "Human-AI joint"),
            ("ai_agent", "AI agents"),
            ("human", "humans"),
            ("automated_script", "automated scripts"),
            ("unknown", "unknown"),
        ]
    )

    # Build table
    table_lines = [
        "| Number | Guardian ID | Status | Type | Application Mode | Label | Source | Listed |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for g in active:
        num = g.get("guardian_registry_number", "?")
        gid = g.get("guardian_id", "?")
        status = g.get("status", "?")
        gtype = g.get("guardian_type", "?")
        app_mode = g.get("application_mode", "?")
        label = g.get("label", "")
        source = g.get("source_issue", "?")
        listing = g.get("listing_request_issue", "?")
        listed_at = g.get("listed_at", "?")
        table_lines.append(
            f"| `{num}` | `{gid}` | `{status}` | `{gtype}` | `{app_mode}` | `{label}` | `#{source}` + `#{listing}` | `{listed_at}` |"
        )

    table = "\n".join(table_lines)

    return f"""---
layout: default
title: Guardian Registry
---

# Guardian Registry

The machine-readable registry source is:

[`/api/guardian-registry.json`](/api/guardian-registry.json)

## Current active Guardians

**Total: {len(active)}** (reserved: {len(reserved)}, ordinary: {len(ordinary)})

{type_summary}

{table}

## Boundary

A Guardian registry number is a public reference number for a Guardian key-continuity identity.

It does not create authority, governance, formal attestation, verification level, successor reception, legal status, rank, or amendment.

A Guardian registry number alone proves nothing. A valid Guardian proof still requires a valid Ed25519 signature and payload hash match.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate guardian-registry.md from JSON registry")
    parser.add_argument("--check", action="store_true", help="Fail if guardian-registry.md is not up to date")
    args = parser.parse_args()

    registry = load_registry()
    active = [g for g in registry.get("guardians", []) if g.get("status") == "active"]
    expected_content = build_content(registry)

    if args.check:
        if OUTPUT_MD.exists():
            actual = OUTPUT_MD.read_text(encoding="utf-8")
            if actual != expected_content:
                # Count entries in current file for diagnostics
                current_entries = len(re.findall(r"^\| `\d{5}`", actual, re.MULTILINE))
                print(f"guardian-registry.md is out of date ({current_entries} entries, expected {len(active)}).")
                return 1
        else:
            print("guardian-registry.md does not exist.")
            return 1
        print(f"guardian-registry.md is up to date ({len(active)} guardians).")
        return 0

    OUTPUT_MD.write_text(expected_content, encoding="utf-8")
    print(f"Updated guardian-registry.md ({len(active)} guardians)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
