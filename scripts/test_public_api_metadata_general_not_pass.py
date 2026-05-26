#!/usr/bin/env python3
"""General public API metadata branch must not silently pass everything."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts" / "validate_public_api_metadata.py").read_text(encoding="utf-8")

bad = """else:
            # General public API: parse and identify.
            # Schema identity is recommended but not enforced for legacy files.
            pass"""

if bad in text:
    print("FAIL: validate_public_api_metadata.py still silently passes general public APIs")
    sys.exit(1)

if "public API missing schema/$schema identity" not in text:
    print("FAIL: validator does not enforce schema identity for general public APIs")
    sys.exit(1)

print("PASS: general public API metadata branch is enforced")
