#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from typing import Any

from archive_backlog_lib import (
    API_OTS_BACKLOG,
    API_RC_BACKLOG,
    OTS_BACKLOG,
    RC_BACKLOG,
    has_arweave_key,
    native_ots_backlog_doc,
    read_json,
    record_chain_backlog_doc,
    run_detector_write,
    utc_now,
    write_json_if_changed,
)

ROOT = Path(__file__).resolve().parents[1]


def update_item(path: Path, api_path: Path, kind: str, key: str, status: str, error: str | None = None, tx_id: str | None = None) -> None:
    data = read_json(path, {"items": []})
    items = list(data.get("items", []))
    for item in items:
        if item.get("key") == key:
            item["archive_status"] = status
            item["retry_count"] = int(item.get("retry_count") or 0) + 1
            item["last_attempt_at"] = utc_now()
            item["last_error"] = error
            if tx_id:
                item["tx_id"] = tx_id
            item["next_action"] = {
                "waiting_for_key": "provide_arweave_key",
                "upload_failed": "retry_upload",
                "readback_failed": "retry_readback_or_upload",
                "archived": "no_op",
                "pending_upload": "upload",
            }.get(status, "review")
            break
    doc = record_chain_backlog_doc(items, utc_now()) if kind == "record_chain_arweave" else native_ots_backlog_doc(items, utc_now())
    write_json_if_changed(path, doc)
    write_json_if_changed(api_path, doc)


def process_record_chain(max_items: int, mode: str) -> int:
    data = read_json(RC_BACKLOG, {"items": []})
    candidates = [i for i in data.get("items", []) if i.get("archive_status") in {"pending_upload", "upload_failed", "readback_failed", "waiting_for_key"}]
    processed = 0
    for item in candidates[:max_items]:
        if mode == "live" and not has_arweave_key():
            update_item(RC_BACKLOG, API_RC_BACKLOG, "record_chain_arweave", item["key"], "waiting_for_key", "ARKEY/Arweave JWK not configured")
            processed += 1
            continue
        if mode != "live":
            update_item(RC_BACKLOG, API_RC_BACKLOG, "record_chain_arweave", item["key"], "pending_upload", None)
            processed += 1
            continue
        result = subprocess.run(["python3", "scripts/build_record_chain_arweave_archive.py", "--mode", "live"], cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "record-chain Arweave upload failed").strip()[-1000:]
            status = "readback_failed" if "readback" in err.lower() else "upload_failed"
            update_item(RC_BACKLOG, API_RC_BACKLOG, "record_chain_arweave", item["key"], status, err)
        processed += 1
    run_detector_write()
    print(f"processed record_chain_arweave items: {processed}")
    return 0


def process_native_ots(max_items: int, enable_paid_upload: bool) -> int:
    data = read_json(OTS_BACKLOG, {"items": []})
    candidates = [i for i in data.get("items", []) if i.get("archive_status") in {"pending_upload", "upload_failed", "readback_failed", "waiting_for_key"}]
    processed = 0
    for item in candidates[:max_items]:
        if enable_paid_upload and not has_arweave_key():
            update_item(OTS_BACKLOG, API_OTS_BACKLOG, "native_ots_bundle", item["key"], "waiting_for_key", "ARKEY/Arweave JWK not configured")
            processed += 1
            continue
        if not enable_paid_upload:
            update_item(OTS_BACKLOG, API_OTS_BACKLOG, "native_ots_bundle", item["key"], "pending_upload", None)
            processed += 1
            continue
        cmd = [
            "python3", "scripts/run_native_ots_upgrade_verify.py",
            "--all-backlog",
            "--max-items", "1",
            "--enable-paid-upload",
        ]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, env=os.environ.copy())
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "native OTS bundle upload failed").strip()[-1000:]
            status = "readback_failed" if "readback" in err.lower() else "upload_failed"
            update_item(OTS_BACKLOG, API_OTS_BACKLOG, "native_ots_bundle", item["key"], status, err)
        processed += 1
    run_detector_write()
    print(f"processed native_ots_bundle items: {processed}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Process lightweight archive backlog")
    parser.add_argument("--kind", choices=["record_chain_arweave", "native_ots_bundle"], required=True)
    parser.add_argument("--max-items", type=int, default=1)
    parser.add_argument("--mode", choices=["dry-run", "live"], default="dry-run")
    parser.add_argument("--enable-paid-upload", action="store_true")
    args = parser.parse_args()
    if args.max_items < 1:
        raise SystemExit("--max-items must be >= 1")
    run_detector_write()
    if args.kind == "record_chain_arweave":
        return process_record_chain(args.max_items, args.mode)
    return process_native_ots(args.max_items, args.enable_paid_upload)


if __name__ == "__main__":
    raise SystemExit(main())
