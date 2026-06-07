#!/usr/bin/env python3
"""Test --require-new-records guard with date-partitioned intake layout."""
from __future__ import annotations
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_date_partitioned_with_server_receipt_id():
    test_dir = ROOT / ".test-require-new-records"
    sub_dir = test_dir / "intake" / "submissions" / "2026" / "06"
    rec_dir = test_dir / "intake" / "receipts" / "2026" / "06"
    try:
        shutil.rmtree(test_dir, ignore_errors=True)
        sub_dir.mkdir(parents=True)
        rec_dir.mkdir(parents=True)

        (sub_dir / "test-001.submission.json").write_text(json.dumps({
            "record_type": "echo", "record_id": "test-001",
            "echo_content": {"echo_text": "test", "echo_intent": "verification"},
        }), encoding="utf-8")
        (rec_dir / "test-001.receipt.json").write_text(json.dumps({
            "server_receipt_id": "rcg-20260607-test-001", "accepted": True,
        }), encoding="utf-8")

        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "auto_finalize_accepted_submissions.py"),
             "--submissions-dir", str(test_dir / "intake" / "submissions"),
             "--receipts-dir", str(test_dir / "intake" / "receipts"),
             "--mode", "dry-run", "--require-new-records"],
            cwd=ROOT, text=True, capture_output=True,
        )
        out = json.loads(r.stdout)
        assert r.returncode == 0, f"exit {r.returncode}: {r.stderr}"
        assert out["result"] == "pass"
        assert out["finalized_count"] > 0
        assert out["finalized"][0]["receipt_id"] == "rcg-20260607-test-001"
        print("PASS: date-partitioned + server_receipt_id + --require-new-records")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_noop_fails_with_flag():
    test_dir = ROOT / ".test-empty-guard"
    try:
        shutil.rmtree(test_dir, ignore_errors=True)
        (test_dir / "intake" / "submissions").mkdir(parents=True)
        (test_dir / "intake" / "receipts").mkdir(parents=True)

        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "auto_finalize_accepted_submissions.py"),
             "--submissions-dir", str(test_dir / "intake" / "submissions"),
             "--receipts-dir", str(test_dir / "intake" / "receipts"),
             "--mode", "dry-run", "--require-new-records"],
            cwd=ROOT, text=True, capture_output=True,
        )
        out = json.loads(r.stdout)
        assert r.returncode == 1, f"Expected exit 1, got {r.returncode}"
        assert out["result"] == "fail"
        assert out["finalized_count"] == 0
        print("PASS: empty dirs + --require-new-records → exit 1")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    test_date_partitioned_with_server_receipt_id()
    test_noop_fails_with_flag()
    print("\nAll tests passed.")
