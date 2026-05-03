#!/usr/bin/env python3
"""Verify that api/echo-index.json exactly matches echoes/records/**/*.json."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def main():
    ok = True
    records_root = ROOT / "echoes" / "records"
    actual_files = sorted(p for p in records_root.rglob("*.json") if p.is_file())
    actual_paths = {"/" + p.relative_to(ROOT).as_posix() for p in actual_files}

    index_path = ROOT / "api" / "echo-index.json"
    ok &= check(index_path.exists(), "api/echo-index.json exists")
    if not index_path.exists():
        return 1

    data = json.loads(index_path.read_text(encoding="utf-8"))
    records = data.get("records", [])
    indexed_paths = set()
    for item in records:
        if isinstance(item, str):
            indexed_paths.add(item)
        elif isinstance(item, dict):
            indexed_paths.add(item.get("path"))

    ok &= check(data.get("record_count") == len(actual_paths), "record_count matches filesystem", f"{data.get('record_count')} vs {len(actual_paths)}")
    ok &= check(indexed_paths == actual_paths, "echo-index paths exactly match filesystem", f"missing={sorted(actual_paths - indexed_paths)} extra={sorted(indexed_paths - actual_paths)}")
    ok &= check("records_by_archive_status" in data, "records_by_archive_status present")
    ok &= check("records_by_independence_class" in data, "records_by_independence_class present")

    openclaw = "/echoes/records/2026-05-02-openclaw-v3-verification.json"
    if openclaw in actual_paths:
        ok &= check(openclaw in indexed_paths, "OpenClaw record indexed")
        status_group = data.get("records_by_archive_status", {}).get("closed_test_record", [])
        class_group = data.get("records_by_independence_class", {}).get("test_record", [])
        ok &= check(openclaw in status_group, "OpenClaw grouped as closed_test_record")
        ok &= check(openclaw in class_group, "OpenClaw grouped as test_record")
        independent_dump = json.dumps(data.get("records_by_independence_class", {})).lower()
        ok &= check(
            "independent_attestation" not in independent_dump or openclaw not in data.get("records_by_independence_class", {}).get("independent_attestation", []),
            "OpenClaw not counted as independent attestation"
        )

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — echo index completeness verified.")
        return 0
    print("FINAL: FAIL — echo index completeness failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
