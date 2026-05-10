#!/usr/bin/env python3
"""Test stale-copy correction endpoint references (TA-REDTEAM-2026-012).

Verifies that llms.txt, ai.txt, api/links.json, and sitemap.xml
all reference the corrections-index endpoint.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    passed = 0
    failed = 0

    # 1. llms.txt contains correction_revocation_index
    llms_path = ROOT / "llms.txt"
    if not llms_path.exists():
        print("  FAIL: llms.txt does not exist")
        failed += 1
    else:
        content = llms_path.read_text(encoding="utf-8")
        if "correction_revocation_index" in content:
            print("  PASS: llms.txt contains correction_revocation_index")
            passed += 1
        else:
            print("  FAIL: llms.txt missing correction_revocation_index")
            failed += 1

    # 2. ai.txt contains correction_revocation_index
    ai_path = ROOT / "ai.txt"
    if not ai_path.exists():
        print("  FAIL: ai.txt does not exist")
        failed += 1
    else:
        content = ai_path.read_text(encoding="utf-8")
        if "correction_revocation_index" in content:
            print("  PASS: ai.txt contains correction_revocation_index")
            passed += 1
        else:
            print("  FAIL: ai.txt missing correction_revocation_index")
            failed += 1

    # 3. api/links.json contains /api/corrections-index.json
    links_path = ROOT / "api" / "links.json"
    if not links_path.exists():
        print("  FAIL: api/links.json does not exist")
        failed += 1
    else:
        data = json.loads(links_path.read_text(encoding="utf-8"))
        machine = data.get("machine", [])
        if "/api/corrections-index.json" in machine:
            print("  PASS: api/links.json contains /api/corrections-index.json")
            passed += 1
        else:
            print("  FAIL: api/links.json missing /api/corrections-index.json")
            failed += 1

    # 4. sitemap.xml contains /api/corrections-index.json
    sitemap_path = ROOT / "sitemap.xml"
    if not sitemap_path.exists():
        print("  FAIL: sitemap.xml does not exist")
        failed += 1
    else:
        content = sitemap_path.read_text(encoding="utf-8")
        if "/api/corrections-index.json" in content:
            print("  PASS: sitemap.xml contains /api/corrections-index.json")
            passed += 1
        else:
            print("  FAIL: sitemap.xml missing /api/corrections-index.json")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"test_stale_copy_correction_endpoint: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
