#!/usr/bin/env python3
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "external-agent-quickstart.md"
t = p.read_text(encoding="utf-8")
block = '''
## Runtime compatibility minimums

Echo `CC-3`; Verification `V0`–`V2` `CC-2`; Verification `V3`–`V5` `CC-3`; Guardian Application `CC-3`; Guardian Retirement `CC-1`; Propagation `CC-2`; Correction `CC-1`; Classification Update `CC-2`; Context-Insufficient Notice `CC-0`.

Formal `CC-3`–`CC-5` records carry actual loaded URLs and exact context-read confirmation.
'''
if block not in t:
    anchor = "\n## Operational Canary\n"
    if anchor not in t: raise RuntimeError("operational canary anchor missing")
    t = t.replace(anchor, block + anchor, 1)
p.write_text(t, encoding="utf-8")
print("QUICKSTART_MINIMUMS_ADDED")
