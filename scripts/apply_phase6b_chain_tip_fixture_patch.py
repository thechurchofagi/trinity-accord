#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "scripts" / "test_phase6b_hotfix.py"
text = path.read_text(encoding="utf-8")
old = '''    mod.CHAIN_TIP.write_text(json.dumps({
        "schema": "trinityaccord.chain-tip.v1",
        "native_record_count": 0,'''
new = '''    mod.CHAIN_TIP.write_text(json.dumps({
        "schema": "trinityaccord.chain-tip.v1",
        "chain_id": mod.CHAIN_ID,
        "native_record_count": 0,'''
if text.count(old) != 1:
    raise SystemExit(f"expected one Phase 6B chain-tip fixture, found {text.count(old)}")
path.write_text(text.replace(old, new), encoding="utf-8")
print("Phase 6B chain-tip fixture patched.")
