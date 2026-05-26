#!/usr/bin/env python3
"""scripts/run_all.sh must not swallow required test failures."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "run_all.sh"
text = path.read_text(encoding="utf-8")

bad_patterns = [
    r'python3 "\$t" 2>&1 \|\| echo "  FAIL: \$t"',
    r'\|\| echo "  \(index gen may need GitHub API',
    r'\|\| echo "  \(status gen may need GitHub API',
]

ok = True
for pat in bad_patterns:
    if re.search(pat, text):
        print(f"FAIL: run_all.sh still swallows failures via pattern: {pat}")
        ok = False

required_fragments = [
    "failures=0",
    "run_required()",
    "exit 1",
    "PASS: all required steps completed",
]

for frag in required_fragments:
    if frag not in text:
        print(f"FAIL: run_all.sh missing fail-closed fragment: {frag}")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: run_all.sh is fail-closed for required steps")
