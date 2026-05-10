#!/usr/bin/env python3
"""Test claim registry public links (TA-REDTEAM-2026-017).

Checks that public surfaces (links, sitemap, llms, ai, recovery, corrections) reference the claim registry.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []

    # 1. api/links.json references api/claim-registry.json
    links_path = ROOT / "api" / "links.json"
    links = json.loads(links_path.read_text())
    machine = links.get("machine", [])
    if not any("claim-registry" in m for m in machine):
        errors.append("api/links.json machine array does not reference claim-registry")

    # 2. sitemap.xml references /api/claim-registry.json
    sitemap = (ROOT / "sitemap.xml").read_text()
    if "claim-registry.json" not in sitemap:
        errors.append("sitemap.xml does not reference claim-registry.json")

    # 3. llms.txt references claim registry
    llms = (ROOT / "llms.txt").read_text()
    if "claim" not in llms.lower() or "registry" not in llms.lower():
        errors.append("llms.txt does not reference claim registry")

    # 4. ai.txt references claim registry
    ai = (ROOT / "ai.txt").read_text()
    if "claim" not in ai.lower() or "registry" not in ai.lower():
        errors.append("ai.txt does not reference claim registry")

    # 5. RECOVERY.md references claim registry or claim traceability
    recovery = (ROOT / "RECOVERY.md").read_text()
    if "claim" not in recovery.lower() or "registry" not in recovery.lower():
        errors.append("RECOVERY.md does not reference claim registry")

    # 6. CORRECTION-REVOCATION-POLICY.md references claim correction path or claim registry
    corrections = (ROOT / "CORRECTION-REVOCATION-POLICY.md").read_text()
    if "claim" not in corrections.lower() or "registry" not in corrections.lower():
        errors.append("CORRECTION-REVOCATION-POLICY.md does not reference claim registry")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("CLAIM_REGISTRY_PUBLIC_LINKS_OK")


if __name__ == "__main__":
    main()
