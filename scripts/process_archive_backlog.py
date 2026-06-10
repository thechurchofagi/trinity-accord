#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
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
CONFIRM_PAID_UPLOAD = "I_UNDERSTAND_THIS_UPLOADS_THE_VERIFIED_OTS_PROOF_BUNDLE_TO_ARWEAVE"


def prepare_native_ots_jwk_path() -> str | None:
    configured_path = os.environ.get("ARWEAVE_JWK_PATH")
    if configured_path and Path(configured_path).exists():
        return configured_path
    raw = os.environ.get("ARKEY") or os.environ.get("ARWEAVE_JWK")
    if not raw:
        return None
    try:
        json.loads(raw)
    except json.JSONDecodeError:
        return None
    secret_dir = Path(tempfile.gettempdir()) / "trinity-arweave-secrets"
    secret_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    jwk_path = secret_dir / "wallet.jwk.json"
    jwk_path.write_text(raw, encoding="utf-8")
    jwk_path.chmod(0o600)
    os.environ["ARWEAVE_JWK_PATH"] = str(jwk_path)
    return str(jwk_path)


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
                "upgrade_due": "upgrade_native_ots_anchor",
                "upgrade_failed": "retry_native_ots_upgrade",
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


ACTIONABLE_NATIVE_STATUSES = {
    "upgrade_due",
    "upgrade_failed",
    "pending_upload",
    "upload_failed",
    "readback_failed",
    "waiting_for_key",
}

UPLOAD_NATIVE_STATUSES = {
    "pending_upload",
    "upload_failed",
    "readback_failed",
    "waiting_for_key",
}


def process_native_ots(max_items: int, enable_paid_upload: bool) -> int:
    data = read_json(OTS_BACKLOG, {"items": []})
    candidates = [
        i for i in data.get("items", [])
        if i.get("archive_status") in ACTIONABLE_NATIVE_STATUSES
    ]

    processed = 0
    for item in candidates[:max_items]:
        status = item.get("archive_status")
        jwk_path = prepare_native_ots_jwk_path() if enable_paid_upload else None

        # Upload/re-upload states need a JWK when paid upload is requested.
        # Upgrade states may still run without a JWK; they can upgrade/build/register_without_tx.
        if enable_paid_upload and not jwk_path and status in UPLOAD_NATIVE_STATUSES:
            update_item(
                OTS_BACKLOG,
                API_OTS_BACKLOG,
                "native_ots_bundle",
                item["key"],
                "waiting_for_key",
                "ARKEY/ARWEAVE_JWK JSON or ARWEAVE_JWK_PATH not configured",
            )
            processed += 1
            continue

        if not enable_paid_upload and status in UPLOAD_NATIVE_STATUSES:
            update_item(OTS_BACKLOG, API_OTS_BACKLOG, "native_ots_bundle", item["key"], "pending_upload", None)
            processed += 1
            continue

        cmd = [
            "python3", "scripts/run_native_ots_upgrade_verify.py",
            "--max-items", "1",
        ]

        anchor_file = item.get("anchor_file")
        if anchor_file:
            cmd += ["--anchor-file", anchor_file]
        else:
            cmd += ["--all-backlog"]

        if enable_paid_upload and jwk_path:
            cmd += [
                "--enable-paid-upload",
                "--confirm-paid-upload", CONFIRM_PAID_UPLOAD,
                "--jwk-path", jwk_path,
            ]

        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, env=os.environ.copy())

        # Always surface subprocess output for debugging
        if result.stdout:
            print(f"[native-ots stdout] {result.stdout.strip()[-2000:]}")
        if result.stderr:
            print(f"[native-ots stderr] {result.stderr.strip()[-2000:]}")

        if result.returncode != 0:
            err = (result.stderr or result.stdout or "native OTS repair failed").strip()[-1000:]
            lower = err.lower()
            if "readback" in lower:
                new_status = "readback_failed"
            elif "upgrade" in lower or "ots" in lower or "pending" in lower:
                new_status = "upgrade_failed"
            else:
                new_status = "upload_failed"
            update_item(OTS_BACKLOG, API_OTS_BACKLOG, "native_ots_bundle", item["key"], new_status, err)
        else:
            # Subprocess returned 0 — determine new status from anchor state.
            anchor_file = item.get("anchor_file")
            new_status = None
            if anchor_file:
                try:
                    anchor_data = read_json(ROOT / anchor_file, {})
                    ots_status = anchor_data.get("ots_status")
                    ots_upgrade_cmd = anchor_data.get("ots_upgrade_command")
                    if ots_status in {"upgraded", "verified"}:
                        if enable_paid_upload:
                            if anchor_data.get("tx_id"):
                                new_status = "archived"
                            else:
                                new_status = "pending_upload"
                        else:
                            new_status = "pending_upload"
                    elif ots_status == "pending" and ots_upgrade_cmd is None:
                        # Script returned 0 but ots upgrade was never executed.
                        # This means ots binary was not found or skip-upgrade was active.
                        # Do NOT advance status — mark as upgrade_failed so it retries.
                        err = (result.stderr or result.stdout or "ots upgrade was not executed; anchor still pending").strip()[-500:]
                        update_item(OTS_BACKLOG, API_OTS_BACKLOG, "native_ots_bundle", item["key"], "upgrade_failed", err)
                        processed += 1
                        continue
                except Exception as exc:
                    update_item(OTS_BACKLOG, API_OTS_BACKLOG, "native_ots_bundle", item["key"], "upgrade_failed", f"failed to read anchor after repair: {exc}")
                    processed += 1
                    continue
            if new_status:
                update_item(OTS_BACKLOG, API_OTS_BACKLOG, "native_ots_bundle", item["key"], new_status)

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
