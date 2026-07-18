#!/usr/bin/env python3
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "external-agent-quickstart.md"
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
for i, line in enumerate(lines):
    if '--fresh-actions "downloaded builder,verified manifest"' not in line:
        continue
    nl = "\r\n" if line.endswith("\r\n") else "\n"
    slash = "\\" if "\\" in line else ""
    values = ["  --digital-profile integrity_checked", '  --relationships-checked "hashes,indexes"', "  --physical-observation none", "  --external-witness none", "  --coverage-scope component_subset", '  --limitations "No physical observation,No external witness"', '  --claims-not-made "No authority claim,No attestation claim"', "  --corrections-or-supersession-checked true"]
    lines[i + 1:i + 1] = [value + (" " + slash if slash else "") + nl for value in values]
    break
else:
    raise RuntimeError("verification example anchor missing")
p.write_text("".join(lines), encoding="utf-8")
print("QUICKSTART_VERIFICATION_FLAGS_FIXED")
