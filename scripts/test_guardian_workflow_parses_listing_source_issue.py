#!/usr/bin/env python3
"""Verify guardian workflow parses listing_source_issue."""
from pathlib import Path
import sys

p = Path(".github/workflows/guardian-registry-auto-list.yml")
text = p.read_text(encoding="utf-8")

if "listing_source_issue" not in text:
    print("FAIL: guardian workflow does not parse listing_source_issue")
    sys.exit(1)

print("PASS: guardian workflow parses listing_source_issue")
