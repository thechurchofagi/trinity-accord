#!/usr/bin/env python3
"""PUB-DIGEST-001: source_digest must not include deprecated hidden inputs."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "scripts/generate_public_home_status.py").read_text(encoding="utf-8")

m = re.search(r"def source_digest\(\).*?return h\.hexdigest\(\)\[:16\]", src, re.S)
if not m:
    print("FAIL: could not locate source_digest function")
    sys.exit(1)

block = m.group(0)

if "AGENT_DECLARED_ECHO_INDEX" in block:
    print("FAIL: source_digest still includes deprecated hidden AGENT_DECLARED_ECHO_INDEX")
    sys.exit(1)

print("PASS: source_digest has no deprecated hidden agent-declared echo input")
