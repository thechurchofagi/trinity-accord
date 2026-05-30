#!/usr/bin/env python3
"""Workflow input tables must not be broken by plain paragraphs."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = (ROOT / "gateway-workflows.md").read_text(encoding="utf-8")

# Extract the Guardian-signed Echo section between ### Inputs and ### Example
m = re.search(
    r'<a id="workflow-guardian-signed-echo"></a>.*?(?=\n---\n\n## Common failures)',
    doc,
    flags=re.S,
)
section = m.group(0) if m else ""

if not section:
    print("FAIL: Guardian-signed Echo section not found")
    sys.exit(1)

# Find the Inputs table block (between ### Inputs and ### Example)
inputs_m = re.search(
    r"### Inputs\n(.*?)(?=\n### )",
    section,
    flags=re.S,
)
inputs_block = inputs_m.group(1) if inputs_m else ""

if not inputs_block:
    print("FAIL: Guardian-signed Echo Inputs section not found")
    sys.exit(1)

# Expected flags in the Guardian-signed Echo input table
expected_flags = [
    "--guardian-registry-number",
    "--guardian-id",
    "--guardian-key-prefix",
    "--agent-readback-file",
    "--related-issue",
    "--idempotency-key",
    "--guardian-challenge",
    "--registry-path",
    "--out",
]

# Walk through lines. The table must be contiguous: once the first table row
# appears, no plain paragraph may appear until the table ends (two consecutive
# non-table, non-blank lines, or a ### heading).
lines = inputs_block.strip().splitlines()
in_table = False
table_rows = []
seen_table_end = False

for line in lines:
    stripped = line.strip()
    if stripped.startswith("|"):
        if seen_table_end:
            print("FAIL: Guardian-signed Echo Inputs table has rows after a gap")
            sys.exit(1)
        in_table = True
        table_rows.append(stripped)
    elif stripped == "" or stripped.startswith("|---") or re.match(r"^\|[\s-]+\|", stripped):
        # Separator row or blank — still part of table context
        continue
    else:
        # Plain paragraph
        if in_table:
            seen_table_end = True

# All expected flags must appear in table rows
table_text = "\n".join(table_rows)
missing = [f for f in expected_flags if f not in table_text]
if missing:
    print(f"FAIL: Guardian-signed Echo Inputs table missing flags: {missing}")
    sys.exit(1)

print("PASS: Guardian-signed Echo Inputs table is contiguous")
