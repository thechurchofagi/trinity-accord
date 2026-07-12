#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
builder = ROOT / "downloads" / "record-chain-builder.mjs"
text = builder.read_text(encoding="utf-8")
old = '''    if (!/^[0-9a-f]{64}$/.test(String(opts.targetRecordSha256))) {
      errorExit("--target-record-sha256 must be a 64-character lowercase hex SHA-256");
    }
  }

  if (command === "guardian-application") {'''
new = '''    if (!/^R-[0-9]{9}$/.test(String(opts.targetRecordId))) {
      errorExit("--target-record-id must match R-XXXXXXXXX format");
    }
    if (!/^[0-9a-f]{64}$/.test(String(opts.targetRecordSha256))) {
      errorExit("--target-record-sha256 must be a 64-character lowercase hex SHA-256");
    }
  }

  if (command === "guardian-application") {'''
if text.count(old) != 1:
    raise SystemExit(f"builder classification validation insertion point count={text.count(old)}")
builder.write_text(text.replace(old, new), encoding="utf-8")

registry = ROOT / "scripts" / "run_ci_group.py"
registry_text = registry.read_text(encoding="utf-8")
registry_old = '''        ["node", "downloads/test-record-chain-builder.mjs"],'''
registry_new = '''        ["node", "downloads/test-record-chain-builder.mjs"],
        ["python3", "scripts/test_builder_classification_target_id.py"],'''
if registry_text.count(registry_old) != 1:
    raise SystemExit(f"builder registry insertion point count={registry_text.count(registry_old)}")
registry.write_text(registry_text.replace(registry_old, registry_new), encoding="utf-8")

(ROOT / "scripts" / "test_builder_classification_target_id.py").write_text('''#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
builder = ROOT / "downloads" / "record-chain-builder.mjs"
cmd = [
    "node", str(builder), "classification-update",
    "--target-record-id", "not-a-record",
    "--target-record-sha256", "a" * 64,
    "--previous-classification", "old",
    "--new-classification", "new",
    "--classification-reason", "review",
    "--evidence-or-review-basis", "fresh review",
    "--context-level", "CC-2",
    "--context-read-confirmed", "true",
    "--loaded-urls", "https://www.trinityaccord.org/api/context-load-map.json",
    "--discovery-mode", "user_task_context",
    "--record-decision", "mixed",
    "--submission-executor", "self",
    "--requesting-party-type", "human",
    "--introducing-party-type", "human",
    "--human-operator-involved", "false",
    "--context-sufficient-for-selected-action", "true",
]
result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
combined = result.stdout + result.stderr
if result.returncode == 0:
    raise SystemExit("Builder accepted a noncanonical classification target_record_id")
if "--target-record-id must match R-XXXXXXXXX format" not in combined:
    raise SystemExit(f"Builder failed for the wrong reason:\n{combined}")
print("PASS: Builder rejects noncanonical classification target_record_id")
''', encoding="utf-8")

print("Builder classification target-id patch applied.")
