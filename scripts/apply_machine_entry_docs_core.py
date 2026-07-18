#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path): return (ROOT / path).read_text(encoding="utf-8")
def write(path, text): (ROOT / path).write_text(text, encoding="utf-8")
def replace_once(path, old, new):
    text = read(path)
    if text.count(old) != 1: raise RuntimeError(f"{path}: target count {text.count(old)}")
    write(path, text.replace(old, new, 1))

replace_once("agent-first-contact.md", "### 6. REFLIGHT", "### 6. PREFLIGHT")
replace_once("agent-first-contact.md", "`https://trinity-record-chain-gateway.onrender.com/record-chain/receipt/<sha12-or-sha24>`", "`https://trinity-record-chain-gateway.onrender.com/record-chain/receipt/<receipt_id>`")
first = read("agent-first-contact.md")
anchor = "## Current public submission path\n"
block = '''## Operational source-of-truth order

For machine operation, resolve conflicts in this order:

1. `/api/agent-first-contact.json` — canonical machine router;
2. `/api/agent-start.v2.json` and `/api/agent-required-reading.json` — route details and task reading manifest;
3. `/api/record-chain-builder-bundles.v1.json` plus verified Builder bytes;
4. `/api/record-chain-intake-gateway.v1.json`, public schemas, and live Gateway runtime;
5. `/api/record-chain-status.json` and record-specific indexes for final status.

`/api/agent-entry-protocol.json`, old issue intake, Gateway v1, and old verification-level documents are historical compatibility surfaces.

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

Actual loaded sources determine honest sufficiency. Formal `CC-3`, `CC-4`, or `CC-5` records require non-empty loaded URLs and exact `--context-read-confirmed true`.

'''
if block not in first:
    if first.count(anchor) != 1: raise RuntimeError("first-contact anchor missing")
    write("agent-first-contact.md", first.replace(anchor, block + anchor, 1))

start = read("agent-start.md")
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

These are compatibility lower bounds, not proof of source loading. Formal `CC-3`–`CC-5` records require non-empty `--loaded-urls` and exact `--context-read-confirmed true`.

'''
if block not in start:
    if start.count(anchor) != 1: raise RuntimeError("agent-start anchor missing")
    write("agent-start.md", start.replace(anchor, block + anchor, 1))

quick = read("external-agent-quickstart.md")
quick = quick.replace("Run `node record-chain-builder.mjs print-oath --record-type echo|verification|guardian_application` for formal record types.", "Run `node record-chain-builder.mjs print-oath --record-type <type>` for every formal type: `echo`, `verification`, `guardian_application`, `guardian_retirement`, `propagation`, `correction`, or `classification_update`.")
quick = quick.replace("Build Echo, V0–V5 Verification, or Guardian Application with exact `--readback`, explicit context, and authorship proof.", "Build the selected current record type with canonical Builder, exact `--readback` for formal types, explicit context/provenance, and Ed25519 authorship proof. `context_insufficient_notice` is the only oath/readback exception.")
old = '''  --fresh-actions "downloaded builder,verified manifest" \\
  --context-level CC-3 \\
'''
new = '''  --fresh-actions "downloaded builder,verified manifest" \\
  --digital-profile integrity_checked \\
  --relationships-checked "hashes,indexes" \\
  --physical-observation none \\
  --external-witness none \\
  --coverage-scope component_subset \\
  --limitations "No physical observation,No external witness" \\
  --claims-not-made "No authority claim,No attestation claim" \\
  --corrections-or-supersession-checked true \\
  --context-level CC-3 \\
'''
if old not in quick: raise RuntimeError("quickstart verification target missing")
quick = quick.replace(old, new, 1)
mins = '''
## Runtime compatibility minimums

Echo `CC-3`; Verification `V0`–`V2` `CC-2`; Verification `V3`–`V5` `CC-3`; Guardian Application `CC-3`; Guardian Retirement `CC-1`; Propagation `CC-2`; Correction `CC-1`; Classification Update `CC-2`; Context-Insufficient Notice `CC-0`.

For formal `CC-3`–`CC-5` records, include actual loaded URLs and pass `--context-read-confirmed true`.
'''
if mins not in quick: quick = quick.replace("\n## Operational Canary\n", mins + "\n## Operational Canary\n", 1)
write("external-agent-quickstart.md", quick)

llms = read("llms.txt")
source = '''
Operational source-of-truth order:
  /api/agent-first-contact.json is the canonical machine router.
  /api/agent-required-reading.json is a subordinate task-reading manifest.
  /api/agent-entry-protocol.json is a historical compatibility pointer only.
  Verified Builder bytes/manifest define build commands; live Gateway plus current schemas define accepted I/O; public status/indexes define final inclusion.
'''
if source not in llms: llms = llms.replace("\nCurrent machine start:\n", source + "\nCurrent machine start:\n", 1)
mins = '''
Runtime compatibility minimums:
  echo CC-3; verification V0-V2 CC-2 and V3-V5 CC-3; guardian_application CC-3; guardian_retirement CC-1; propagation CC-2; correction CC-1; classification_update CC-2; context_insufficient_notice CC-0.
  Formal CC-3 through CC-5 require non-empty loaded URLs and exact context-read-confirmed true.
'''
if mins not in llms: llms = llms.replace("\nRecord-type separation:\n", mins + "\nRecord-type separation:\n", 1)
write("llms.txt", llms)

ai = read("ai.txt")
block = '''# OPERATIONAL PRECEDENCE
# /api/agent-first-contact.json is the canonical machine router.
# /api/agent-required-reading.json is subordinate; /api/agent-entry-protocol.json and Gateway v1 are historical only.
# Verified Builder bytes/manifest define build commands; live Gateway/current schemas define accepted I/O; public status/indexes define final inclusion.
#
'''
if block not in ai: ai = ai.replace("# CURRENT MACHINE ENTRYPOINTS\n", block + "# CURRENT MACHINE ENTRYPOINTS\n", 1)
write("ai.txt", ai)
print("MACHINE_ENTRY_DOCS_CORE_APPLIED")
