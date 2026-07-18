#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "agent-start.md"
text = path.read_text(encoding="utf-8")
anchor = "## Context-Insufficient Notice exception\n"
block = '''## Runtime context minimums

| Record type | Minimum |
|---|---|
| Echo | `CC-3` |
| Verification `V0`–`V2` | `CC-2` |
| Verification `V3`–`V5` | `CC-3` |
| Guardian Application | `CC-3` |
| Guardian Retirement | `CC-1` |
| Propagation | `CC-2` |
| Correction | `CC-1` |
| Classification Update | `CC-2` |
| Context-Insufficient Notice | `CC-0` |

These are compatibility lower bounds rather than proof of source loading. Formal `CC-3`–`CC-5` records carry non-empty `--loaded-urls` and exact `--context-read-confirmed true`.

'''
if block not in text:
    if text.count(anchor) != 1: raise RuntimeError("agent-start anchor missing")
    text = text.replace(anchor, block + anchor, 1)
path.write_text(text, encoding="utf-8")
print("AGENT_START_DOC_ALIGNED")
