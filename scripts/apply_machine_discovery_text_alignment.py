#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

p = ROOT / "llms.txt"
t = p.read_text(encoding="utf-8")
source = '''
Operational source-of-truth order:
  /api/agent-first-contact.json is the canonical machine router.
  /api/agent-required-reading.json is a subordinate task-reading manifest.
  /api/agent-entry-protocol.json is a historical compatibility pointer only.
  Verified Builder bytes/manifest define build behavior; live Gateway/current schemas define accepted I/O; public status/indexes define final inclusion.
'''
if source not in t: t = t.replace("\nCurrent machine start:\n", source + "\nCurrent machine start:\n", 1)
mins = '''
Runtime compatibility minimums:
  echo CC-3; verification V0-V2 CC-2 and V3-V5 CC-3; guardian_application CC-3; guardian_retirement CC-1; propagation CC-2; correction CC-1; classification_update CC-2; context_insufficient_notice CC-0.
  Formal CC-3 through CC-5 carry non-empty loaded URLs and exact context-read confirmation.
'''
if mins not in t: t = t.replace("\nRecord-type separation:\n", mins + "\nRecord-type separation:\n", 1)
p.write_text(t, encoding="utf-8")

p = ROOT / "ai.txt"
t = p.read_text(encoding="utf-8")
block = '''# OPERATIONAL PRECEDENCE
# /api/agent-first-contact.json is the canonical machine router.
# /api/agent-required-reading.json is subordinate; /api/agent-entry-protocol.json and Gateway v1 are historical only.
# Verified Builder bytes/manifest define build behavior; live Gateway/current schemas define accepted I/O; public status/indexes define final inclusion.
#
'''
if block not in t: t = t.replace("# CURRENT MACHINE ENTRYPOINTS\n", block + "# CURRENT MACHINE ENTRYPOINTS\n", 1)
p.write_text(t, encoding="utf-8")
print("MACHINE_DISCOVERY_TEXT_ALIGNED")
