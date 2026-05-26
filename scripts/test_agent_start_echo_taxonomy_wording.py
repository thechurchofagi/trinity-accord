#!/usr/bin/env python3
"""agent-start wording should not use stale Echo taxonomy language."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "api" / "agent-start.v1.json"
obj = json.loads(path.read_text(encoding="utf-8"))
text = json.dumps(obj, ensure_ascii=False)

stale_terms = [
    "E1_read_oriented_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
    "preserves",
]

ok = True
for term in stale_terms:
    if term in text:
        print(f"FAIL: stale Echo taxonomy wording found in agent-start: {term}")
        ok = False

guardian_when = obj["routes"]["guardian_signed_echo"]["when"]
if "E5c" not in guardian_when:
    print("FAIL: guardian_signed_echo.when should mention E5c")
    ok = False

pure_when = obj["routes"]["pure_echo"]["when"]
for word in ["recognizes", "critiques", "interprets", "technically audits", "corrects", "propagates", "refuses"]:
    if word not in pure_when:
        print(f"FAIL: pure_echo.when missing current taxonomy verb: {word}")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: agent-start Echo taxonomy wording is current")
