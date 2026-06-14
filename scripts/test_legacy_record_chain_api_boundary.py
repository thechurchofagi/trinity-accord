#!/usr/bin/env python3
"""Part D: Test that legacy record-chain public APIs are fail-closed."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def load_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


_REQUIRED_FLAGS = {
    "historical_archive_only": True,
    "legacy_hash_chain_view": True,
}


def check_fail_closed(data: dict, path: str, is_head: bool = False) -> None:
    """Verify fail-closed flags and replacement pointers."""
    for key, expected in _REQUIRED_FLAGS.items():
        if data.get(key) != expected:
            fail(f"{path}: {key} must be {expected}, got {data.get(key)}")

    if is_head:
        if data.get("not_current_native_record_chain_head") is not True:
            fail(f"{path}: not_current_native_record_chain_head must be true")
    else:
        if data.get("not_current_native_record_chain_index") is not True:
            fail(f"{path}: not_current_native_record_chain_index must be true")

    for field in ("replacement_current_status_api", "replacement_native_record_index", "replacement_native_chain_tip"):
        if not data.get(field):
            fail(f"{path}: missing {field}")

    ok(f"{path} is fail-closed")


def main() -> int:
    api_dir = ROOT / "api"

    # Check head
    head_path = api_dir / "record-chain-head.json"
    if head_path.exists():
        check_fail_closed(load_json(head_path), str(head_path), is_head=True)

    # Check type indexes
    for index_file in sorted(api_dir.glob("record-chain-index.*.json")):
        if index_file.name == "record-chain-index.manifest.json":
            continue
        data = load_json(index_file)
        check_fail_closed(data, str(index_file))

    # Check manifest
    manifest_path = api_dir / "record-chain-index.manifest.json"
    if manifest_path.exists():
        data = load_json(manifest_path)
        check_fail_closed(data, str(manifest_path))

    print("PASS: all legacy record-chain APIs are fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
