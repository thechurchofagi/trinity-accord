#!/usr/bin/env python3
"""Public API metadata validator must discover /api/*.json files from sitemap."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_public_api_metadata import sitemap_api_json_files

apis = sitemap_api_json_files()

required = {
    "api/public-home-status.json",
    "api/context-load-map.json",
    "api/agent-start.v1.json",
    "api/gateway-builder-route-map.v1.json",
    "api/guardian-registry.json",
    "api/agent-declared-verification-index.json",
}

missing = sorted(required - set(apis))
if missing:
    print(f"FAIL: sitemap API discovery missing expected APIs: {missing}")
    sys.exit(1)

if len(apis) < 50:
    print(f"FAIL: sitemap API discovery unexpectedly small: {len(apis)}")
    sys.exit(1)

print("PASS: public API sitemap discovery covers main APIs")
