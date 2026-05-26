#!/usr/bin/env python3
"""DEEP-IDX-002: agent-declared-echo-index is not used as a stale live input."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "scripts/generate_public_home_status.py"
text = p.read_text(encoding="utf-8")

if "AGENT_DECLARED_ECHO_INDEX.exists()" in text:
    print("FAIL: public status still reads agent-declared-echo-index as a live input")
    sys.exit(1)

if "ad_echo_index" in text and "load_json(AGENT_DECLARED_ECHO_INDEX)" in text:
    print("FAIL: public status still loads agent-declared-echo-index")
    sys.exit(1)

print("PASS: agent-declared-echo-index is not used as a stale live input")
