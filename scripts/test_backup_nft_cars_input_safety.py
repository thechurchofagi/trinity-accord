#!/usr/bin/env python3
"""VR-008: Verify backup-nft-cars workflow validates CONCURRENCY input."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

workflow = (ROOT / ".github" / "workflows" / "backup-nft-cars.yml").read_text(encoding="utf-8")
script = (ROOT / "scripts" / "download-nft-cars.mjs").read_text(encoding="utf-8")

errors = []

if "Validate inputs" not in workflow:
    errors.append("backup-nft-cars.yml should validate workflow inputs before running node script")

if "CONCURRENCY" not in workflow or "-le 25" not in workflow:
    errors.append("backup-nft-cars.yml should enforce concurrency range 1-25")

if "parsePositiveIntEnv" not in script:
    errors.append("download-nft-cars.mjs should parse bounded integer env values")

if "Invalid" not in script or "CONCURRENCY" not in script:
    errors.append("download-nft-cars.mjs should reject invalid CONCURRENCY")

if errors:
    print("BACKUP_NFT_CARS_INPUT_SAFETY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("BACKUP_NFT_CARS_INPUT_SAFETY_OK")
