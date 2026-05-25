#!/usr/bin/env python3
"""FUNC-DOWNLOAD-001: Downloads page freshness check."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "downloads.md").read_text(encoding="utf-8")

required = [
    "/api/verification-materials.json",
    "/api/evidence-manifest.json",
    "/api/recovery-index.json",
    "/api/links.json",
    "/downloads/arweave-bundle-verification",
    "/downloads/gz2-notarial-certificate-github-release-backup-2026-05-14",
    "/downloads/gz2-photos-arweave-2026-05-14",
    "/downloads/redteam-audit-2026-05-08",
    "/downloads/shenzhen-notary-arweave-2026-05-06",
    "/downloads/shenzhen-notary-github-release-backup-2026-05-06",
]

missing = [x for x in required if x not in text]
if missing:
    print(f"FAIL: downloads.md missing current download/evidence links: {missing}")
    sys.exit(1)

print("PASS: downloads.md includes current download/evidence links")
