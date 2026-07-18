#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

path = ROOT / "scripts/test_agent_e2e_journey_matrix.py"
text = path.read_text(encoding="utf-8")
old = 'node(["context-insufficient", "--actor-label", "E2E Test Agent", "--provider", "Offline Test Runtime", "--key-dir", "./authorship-keys", "--out", "cin.json"], tmp)'
new = 'node(["context-insufficient", "--actor-label", "E2E Test Agent", "--provider", "Offline Test Runtime", "--body", "Insufficient context for a stronger record", "--key-dir", "./authorship-keys", "--out", "cin.json"], tmp)'
if text.count(old) != 1:
    raise RuntimeError(f"context-insufficient E2E target count={text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")

path = ROOT / "scripts/test_record_chain_builder_bundle_contract.py"
text = path.read_text(encoding="utf-8")
old = '            "--provider", "Test",\n            "--key-dir", "/tmp/trinity-test-ci-keydir",'
new = '            "--provider", "Test",\n            "--body", "Insufficient context for a stronger record",\n            "--key-dir", "/tmp/trinity-test-ci-keydir",'
if text.count(old) != 1:
    raise RuntimeError(f"builder bundle context-insufficient target count={text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")

print("CONTEXT_INSUFFICIENT_FIXTURES_ALIGNED")
