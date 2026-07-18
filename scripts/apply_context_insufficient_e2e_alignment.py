#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts/test_agent_e2e_journey_matrix.py"
text = path.read_text(encoding="utf-8")
old = 'node(["context-insufficient", "--actor-label", "E2E Test Agent", "--provider", "Offline Test Runtime", "--key-dir", "./authorship-keys", "--out", "cin.json"], tmp)'
new = 'node(["context-insufficient", "--actor-label", "E2E Test Agent", "--provider", "Offline Test Runtime", "--body", "Insufficient context for a stronger record", "--key-dir", "./authorship-keys", "--out", "cin.json"], tmp)'
if text.count(old) != 1:
    raise RuntimeError(f"context-insufficient E2E target count={text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("CONTEXT_INSUFFICIENT_E2E_ALIGNED")
