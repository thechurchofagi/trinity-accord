#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = ROOT / "scripts/check_record_chain_write_path_guard.py"

spec = importlib.util.spec_from_file_location("record_chain_write_path_guard", GUARD_PATH)
if spec is None or spec.loader is None:
    raise SystemExit("FAIL: unable to load write-path guard module")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

files = [
    "record-chain/intake/by-submission-sha256/4ff02e.json",
    "record-chain/intake/receipts/2026/07/rcg-test.receipt.json",
    "record-chain/intake/submissions/2026/07/rcg-test.submission.json",
    "record-chain/pending/rcg-test.context_insufficient_notice.pending.json",
]
message = "intake: materialize rcg-test (context_insufficient_notice)"

ok, reason = module.allowed_for_push(
    files,
    message,
    ["single-commit"],
    "single-commit",
    "thechurchofagi",
    {"thechurchofagi"},
)
assert ok, reason
assert reason == "gateway intake commit"

ok, reason = module.allowed_for_push(
    files,
    message,
    ["single-commit"],
    "single-commit",
    "untrusted-user",
    {"thechurchofagi"},
)
assert not ok
assert "gateway intake actor not allowed" in reason

ok, reason = module.allowed_for_push(
    [*files, "record-chain/records/R-999999999.json"],
    message,
    ["single-commit"],
    "single-commit",
    "thechurchofagi",
    {"thechurchofagi"},
)
assert not ok
assert "unauthorized push write categories" in reason

print("PASS: materialize commits are allowed only for configured Gateway actors and intake/pending paths")
