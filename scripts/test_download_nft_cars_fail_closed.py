#!/usr/bin/env python3
"""VR-003: Verify download-nft-cars.mjs fails closed on download/upload failures."""
from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "download-nft-cars.mjs"
text = path.read_text(encoding="utf-8")

errors = []

if "if (fail > 0)" not in text and "fail > 0" not in text:
    errors.append("download-nft-cars.mjs must fail closed when downloads fail")

if "refusing to package" not in text.lower() and "downloads failed" not in text.lower():
    errors.append("download failure must explicitly refuse packaging/upload")

if "uploadFail" not in text:
    errors.append("upload failures must be counted")

if not re.search(r"if\s*\(\s*uploadFail\s*>\s*0\s*\)", text):
    errors.append("uploadFail > 0 must cause failure")

if "throw new Error" not in text:
    errors.append("fail-closed branches must throw errors")

if errors:
    print("DOWNLOAD_NFT_CARS_FAIL_CLOSED_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("DOWNLOAD_NFT_CARS_FAIL_CLOSED_OK")
