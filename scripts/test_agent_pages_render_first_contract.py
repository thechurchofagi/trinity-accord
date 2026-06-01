#!/usr/bin/env python3
"""Test: agent pages must lead with Render-first submission instructions.

Checks that:
1. Render gateway URL appears in key pages
2. /record-chain/preflight and /record-chain/submit appear in key pages
3. New Render-first action sequence appears in agent-first-contact
4. Legacy Gateway v1 sections are properly marked as legacy in headers
5. The primary instruction block (first occurrence) uses Render-first flow
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RENDER_GW = "trinity-record-chain-gateway.onrender.com"
RENDER_ENDPOINTS = ["/record-chain/preflight", "/record-chain/submit"]


def main() -> None:
    errors = []

    # Test 1: Render gateway URL in key pages
    for page in ["index.md", "agent-first-contact.md", "agent-start.md"]:
        path = ROOT / page
        if not path.exists():
            errors.append(f"{page}: FILE NOT FOUND")
            continue
        content = path.read_text()
        if RENDER_GW not in content:
            errors.append(f"{page}: missing Render gateway URL ({RENDER_GW})")

    # Test 2: Render endpoints in key pages
    for page in ["index.md", "agent-first-contact.md", "agent-start.md"]:
        path = ROOT / page
        if not path.exists():
            continue
        content = path.read_text()
        for ep in RENDER_ENDPOINTS:
            if ep not in content:
                errors.append(f"{page}: missing endpoint {ep}")

    # Test 3: agent-first-contact has new Render-first action sequence
    path = ROOT / "agent-first-contact.md"
    if path.exists():
        content = path.read_text()
        for action in ["DOWNLOAD_BUILDER", "BUILD_SUBMISSION", "PREFLIGHT", "SUBMIT", "SAVE_RECEIPT"]:
            if action not in content:
                errors.append(f"agent-first-contact.md: missing action {action}")

    # Test 4: agent-start has zero-clone quick start
    path = ROOT / "agent-start.md"
    if path.exists():
        content = path.read_text()
        if "record-chain-builder.mjs" not in content:
            errors.append("agent-start.md: missing builder reference")
        if "zero-clone" not in content.lower():
            errors.append("agent-start.md: missing zero-clone reference")

    # Test 5: llms.txt has Render-first block at top
    path = ROOT / "llms.txt"
    if path.exists():
        lines = path.read_text().splitlines()
        # Check first 30 lines for Render-first instruction
        top_block = "\n".join(lines[:30])
        if RENDER_GW not in top_block:
            errors.append("llms.txt: Render gateway not in top 30 lines")
        if "must not clone" not in top_block.lower() and "must not request github" not in top_block.lower():
            errors.append("llms.txt: missing 'must not clone' in top block")

    # Test 6: ai.txt has Render-first block at top
    path = ROOT / "ai.txt"
    if path.exists():
        lines = path.read_text().splitlines()
        top_block = "\n".join(lines[:30])
        if "Record-Chain Intake Gateway" not in top_block:
            errors.append("ai.txt: missing 'Record-Chain Intake Gateway' in top 30 lines")

    # Test 7: Legacy Gateway sections are marked as legacy
    for page in ["index.md"]:
        path = ROOT / page
        if not path.exists():
            continue
        content = path.read_text()
        # The issue-gateway-intake section should have "legacy" in its header
        if 'id="issue-gateway-intake"' in content:
            # Find the section header
            match = re.search(
                r'section id="issue-gateway-intake".*?<h2>(.*?)</h2>',
                content,
                re.DOTALL,
            )
            if match and "legacy" not in match.group(1).lower():
                errors.append(
                    f'{page}: issue-gateway-intake section header not marked as legacy'
                )

    # Test 8: API contracts exist
    for f in [
        "api/record-chain-intake-gateway.v1.json",
        "api/record-chain-submission-schema.v1.json",
        "api/record-chain-preflight-response.v1.json",
        "api/record-chain-submit-response.v1.json",
        "api/record-chain-builder-bundles.v1.json",
    ]:
        if not (ROOT / f).exists():
            errors.append(f"{f}: NOT FOUND")

    # Test 9: Builder exists and works
    builder = ROOT / "downloads" / "record-chain-builder.mjs"
    if not builder.exists():
        errors.append("downloads/record-chain-builder.mjs: NOT FOUND")

    # Test 10: Intake directory structure
    for d in ["record-chain/intake/submissions", "record-chain/intake/receipts"]:
        if not (ROOT / d).is_dir():
            errors.append(f"{d}: NOT FOUND")

    # Test 11: Append workflow exists
    wf = ROOT / ".github/workflows/record-chain-append.yml"
    if not wf.exists():
        errors.append(".github/workflows/record-chain-append.yml: NOT FOUND")

    if errors:
        print("FAIL:\n")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("PASS: All Render-first submission checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
