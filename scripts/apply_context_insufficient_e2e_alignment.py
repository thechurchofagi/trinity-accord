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

path = ROOT / "scripts/test_mandatory_authorship_key_contract.py"
text = path.read_text(encoding="utf-8")
old = '            "--provider", "Test Runtime",\n            "--out", str(Path(td) / "out.json"),'
new = '            "--provider", "Test Runtime",\n            "--body", "Insufficient context for a stronger record",\n            "--out", str(Path(td) / "out.json"),'
if text.count(old) != 1:
    raise RuntimeError(f"mandatory-key no-keydir target count={text.count(old)}")
text = text.replace(old, new, 1)
old = '            "--provider", "Test Runtime",\n            "--key-dir", str(key_dir),\n            "--out", str(out),'
new = '            "--provider", "Test Runtime",\n            "--body", "Insufficient context for a stronger record",\n            "--key-dir", str(key_dir),\n            "--out", str(out),'
if text.count(old) != 1:
    raise RuntimeError(f"mandatory-key proof target count={text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")

path = ROOT / "scripts/test_gateway_authorship_proof_contract.py"
text = path.read_text(encoding="utf-8")
old = '             "--actor-label", "Test Agent", "--provider", "Test Runtime",\n             "--key-dir", str(key_dir), "--out", str(out)],'
new = '             "--actor-label", "Test Agent", "--provider", "Test Runtime",\n             "--body", "Insufficient context for a stronger record",\n             "--key-dir", str(key_dir), "--out", str(out)],'
if text.count(old) != 1:
    raise RuntimeError(f"gateway authorship context-insufficient target count={text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")

print("CONTEXT_INSUFFICIENT_FIXTURES_ALIGNED")
