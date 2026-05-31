#!/usr/bin/env python3
"""Verify that api/echo-index.json matches echoes/records/**/*.json — including metadata."""
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


def get_index_item_by_path(records):
    out = {}
    for item in records:
        if isinstance(item, str):
            out[item] = {"path": item}
        elif isinstance(item, dict):
            out[item.get("path")] = item
    return out


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

    ok &= check(data.get("record_count") == len(actual_paths), "record_count matches filesystem",
                f"{data.get('record_count')} vs {len(actual_paths)}")
    ok &= check(indexed_paths == actual_paths, "echo-index paths exactly match filesystem",
                f"missing={sorted(actual_paths - indexed_paths)} extra={sorted(indexed_paths - actual_paths)}")
    ok &= check("records_by_archive_status" in data, "records_by_archive_status present")
    ok &= check("records_by_independence_class" in data, "records_by_independence_class present")
    ok &= check("records_by_verification_status" in data, "records_by_verification_status present")

    # Deep metadata comparison
    indexed_by_path = get_index_item_by_path(records)

    for actual_file in actual_files:
        rel = "/" + actual_file.relative_to(ROOT).as_posix()
        src = json.loads(actual_file.read_text(encoding="utf-8"))
        idx = indexed_by_path.get(rel)

        ok &= check(idx is not None, f"{rel} indexed")
        if not idx:
            continue

        for field in [
            "archive_status",
            "verification_status",
            "do_not_count_as_attestation",
            "independence_class",
            # echo_type removed — deprecated; Echo is a unified type
            "record_kind",
        ]:
            if field == "do_not_count_as_attestation":
                # Match build_echo_index.py derivation logic:
                # explicit field > derived from independence_class > counts_as_independent_attestation
                src_val = src.get(field)
                if src_val is None:
                    src_val = src.get("independence_class") == "human_solicited_agent_response"
                if src.get("counts_as_independent_attestation") is False:
                    src_val = True
                expected = src_val
                actual = idx.get(field, False)
            else:
                expected = src.get(field, "unknown")
                actual = idx.get(field, "unknown")
            ok &= check(
                actual == expected,
                f"{rel} index {field} matches source",
                f"index={actual!r} source={expected!r}"
            )

        # OpenClaw-specific: content-based detection
        record_text = json.dumps(src, ensure_ascii=False).lower()
        is_openclaw = "openclaw" in record_text

        if is_openclaw and src.get("verification_status") == "invalidated":
            ok &= check(idx.get("verification_status") == "invalidated",
                        f"{rel} invalidated OpenClaw index status")
            ok &= check(idx.get("do_not_count_as_attestation") is True,
                        f"{rel} invalidated OpenClaw do_not_count")

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — echo index completeness verified.")
        return 0
    print("FINAL: FAIL — echo index completeness failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
