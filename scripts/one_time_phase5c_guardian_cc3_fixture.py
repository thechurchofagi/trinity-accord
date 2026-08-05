#!/usr/bin/env python3
from pathlib import Path

path = Path("scripts/test_phase_5c_hotfix.py")
text = path.read_text(encoding="utf-8")
old = '''            "--context-level",
            "CC-2",
            "--context-sufficient-for-selected-action",
'''
new = '''            "--context-level",
            "CC-3",
            "--context-read-confirmed",
            "true",
            "--context-sufficient-for-selected-action",
'''
if text.count(old) != 1:
    raise SystemExit(f"expected one Guardian CC-2 fixture block, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Updated Phase 5C Guardian Application fixture to current CC-3 contract.")
