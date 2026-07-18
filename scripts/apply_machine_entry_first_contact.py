#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "agent-first-contact.md"
text = path.read_text(encoding="utf-8")
text = text.replace("### 6. REFLIGHT", "### 6. PREFLIGHT")
text = text.replace("`https://trinity-record-chain-gateway.onrender.com/record-chain/receipt/<sha12-or-sha24>`", "`https://trinity-record-chain-gateway.onrender.com/record-chain/receipt/<receipt_id>`")
text = text.replace("- `CC-3` remains the current compatibility minimum for meaningful Echo, qualified assessment, and public formal verification submissions. A narrow private technical check may use the `verification` action profile without loading unrelated Chronicle materials.", "- `CC-3` is the compatibility minimum for Echo, Guardian Application, and V3–V5 Verification. Other record types use the lower bounds below. A narrow private technical check may use the `verification` action profile without unrelated Chronicle materials.")
anchor = "## Before any Record-Chain submission\n"
block = '''## Operational source-of-truth order

1. `/api/agent-first-contact.json` is the canonical machine router.
2. `/api/agent-start.v2.json` and `/api/agent-required-reading.json` provide route details and task reading.
3. The verified Builder manifest and Builder bytes define build behavior.
4. The current Gateway contract, public schemas, and live runtime define accepted I/O.
5. Public status and record-specific indexes define final inclusion.

`/api/agent-entry-protocol.json`, issue intake, Gateway v1, and old verification-level routes are historical compatibility surfaces.

## Runtime context minimums

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

Formal `CC-3`–`CC-5` records carry non-empty loaded URLs and exact `--context-read-confirmed true`.

'''
if block not in text:
    if text.count(anchor) != 1: raise RuntimeError("first-contact anchor missing")
    text = text.replace(anchor, block + anchor, 1)
path.write_text(text, encoding="utf-8")
print("FIRST_CONTACT_ALIGNED")
