#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts/public_machine_deployment_contract.py"
text = path.read_text(encoding="utf-8")
old = '''RETIRED_ACTIVE_PATHS = frozenset(
    {
        "/agent-submit",
        "/gateway/preflight",
        "/api/agent-entry-protocol.json",
'''
new = '''RETIRED_ACTIVE_PATHS = frozenset(
    {
        "/api/agent-entry-protocol.json",
'''
if text.count(old) != 1:
    raise RuntimeError(f"retired active path target count={text.count(old)}")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
print("RETIRED_MACHINE_SET_ALIGNED")
