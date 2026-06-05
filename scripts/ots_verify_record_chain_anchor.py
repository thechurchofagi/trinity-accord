#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

from record_chain_hashing import (
    OTS_ANCHOR_SCHEMA,
    load_json,
    sha256_bytes,
    write_json_atomic,
)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def is_pending_output(text: str) -> bool:
    lower = text.lower()
    pending_markers = [
        "pending",
        "pendingattestation",
        "pending confirmation",
        "calendar",
        "incomplete",
        "not complete",
        "upgrade",
        "attestation",
    ]
    return any(marker in lower for marker in pending_markers)


def is_success_output(text: str) -> bool:
    lower = text.lower()
    return "success" in lower and ("bitcoin" in lower or "timestamp complete" in lower)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify a Record-Chain OTS anchor."
    )
    parser.add_argument("--anchor-file", required=True)
    parser.add_argument("--ots-bin", default="ots")
    parser.add_argument("--upgrade", action="store_true")
    parser.add_argument("--strict-bitcoin", action="store_true")
    parser.add_argument("--allow-dry-run", action="store_true")
    parser.add_argument("--write-updated-anchor", action="store_true")
    parser.add_argument("--bitcoin-node-url", default=None)
    args = parser.parse_args()

    anchor_path = Path(args.anchor_file)
    anchor = load_json(anchor_path)

    errors: list[str] = []
    if anchor.get("schema") != OTS_ANCHOR_SCHEMA:
        errors.append("anchor schema mismatch")

    anchored_file = Path(anchor.get("anchored_file", ""))
    ots_file = Path(anchor.get("ots_file", "")) if anchor.get("ots_file") else None

    if not anchored_file.exists():
        errors.append(f"anchored file missing: {anchored_file}")
    else:
        actual_sha = sha256_bytes(anchored_file.read_bytes())
        if actual_sha != anchor.get("anchored_file_sha256"):
            errors.append(
                f"anchored file sha mismatch: expected {anchor.get('anchored_file_sha256')}, got {actual_sha}"
            )

    ots_status = anchor.get("ots_status")
    if ots_status == "dry_run":
        if not args.allow_dry_run:
            errors.append("anchor is dry_run but --allow-dry-run was not set")

        report = {
            "schema": "trinity_record_chain_ots_verify_report.v1",
            "anchor_file": str(anchor_path),
            "result": "pass" if not errors else "fail",
            "dry_run": True,
            "errors": errors,
            "generated_at": utc_now(),
        }
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False))
        if errors:
            raise SystemExit(1)
        return

    if ots_file is None:
        errors.append("ots_file missing")
    elif not ots_file.exists():
        errors.append(f"ots file missing: {ots_file}")
    elif anchor.get("ots_file_sha256"):
        actual_ots_sha = sha256_bytes(ots_file.read_bytes())
        if actual_ots_sha != anchor.get("ots_file_sha256"):
            if not (args.upgrade and args.write_updated_anchor):
                errors.append(
                    f"ots file sha mismatch: expected {anchor.get('ots_file_sha256')}, got {actual_ots_sha}"
                )

    ots_verify_command = None
    ots_verify_exit_code = None
    ots_verify_stdout = None
    ots_verify_stderr = None
    ots_upgrade_command = None
    ots_upgrade_exit_code = None
    ots_upgrade_stdout = None
    ots_upgrade_stderr = None

    bitcoin_verified = False
    bitcoin_pending = False

    if not errors:
        if not shutil.which(args.ots_bin):
            errors.append(f"OpenTimestamps CLI not found: {args.ots_bin}")
        else:
            if args.upgrade:
                ots_upgrade_command = [args.ots_bin, "upgrade", str(ots_file)]
                upgrade = run_cmd(ots_upgrade_command)
                ots_upgrade_exit_code = upgrade.returncode
                ots_upgrade_stdout = upgrade.stdout
                ots_upgrade_stderr = upgrade.stderr

            ots_verify_command = [args.ots_bin]
            if args.bitcoin_node_url:
                ots_verify_command += ["--bitcoin-node", args.bitcoin_node_url]
            ots_verify_command += ["verify", str(ots_file)]

            verify = run_cmd(ots_verify_command)
            ots_verify_exit_code = verify.returncode
            ots_verify_stdout = verify.stdout
            ots_verify_stderr = verify.stderr

            combined = f"{verify.stdout}\n{verify.stderr}"
            if args.upgrade:
                combined += f"\n{upgrade.stdout}\n{upgrade.stderr}"

            upgrade_proved_complete = False
            if args.upgrade and upgrade.returncode == 0:
                upgrade_text = f"{upgrade.stdout}\n{upgrade.stderr}".lower()
                if "success" in upgrade_text and "timestamp complete" in upgrade_text:
                    upgrade_proved_complete = True

            if verify.returncode == 0 and is_success_output(combined):
                bitcoin_verified = True
            elif upgrade_proved_complete:
                bitcoin_verified = True
            elif is_pending_output(combined):
                bitcoin_pending = True
                if args.strict_bitcoin:
                    errors.append("OTS proof is pending and not Bitcoin-verified yet")
            else:
                errors.append(
                    "OTS verify failed without recognizable pending state; treating as invalid"
                )

    if ots_file and ots_file.exists():
        anchor["ots_file_sha256"] = sha256_bytes(ots_file.read_bytes())

    anchor["verified_at"] = utc_now()
    anchor["ots_verify_command"] = ots_verify_command
    anchor["ots_verify_exit_code"] = ots_verify_exit_code
    anchor["ots_verify_stdout"] = ots_verify_stdout
    anchor["ots_verify_stderr"] = ots_verify_stderr
    anchor["ots_upgrade_command"] = ots_upgrade_command
    anchor["ots_upgrade_exit_code"] = ots_upgrade_exit_code
    anchor["ots_upgrade_stdout"] = ots_upgrade_stdout
    anchor["ots_upgrade_stderr"] = ots_upgrade_stderr
    anchor["bitcoin_verified"] = bitcoin_verified
    anchor["bitcoin_pending"] = bitcoin_pending
    anchor["ots_status"] = "verified" if bitcoin_verified else "pending"

    if args.write_updated_anchor:
        write_json_atomic(anchor_path, anchor)

    result = "pass" if not errors else "fail"

    report = {
        "schema": "trinity_record_chain_ots_verify_report.v1",
        "anchor_file": str(anchor_path),
        "anchored_file": str(anchored_file),
        "ots_file": str(ots_file) if ots_file else None,
        "result": result,
        "bitcoin_verified": bitcoin_verified,
        "bitcoin_pending": bitcoin_pending,
        "strict_bitcoin": args.strict_bitcoin,
        "errors": errors,
        "generated_at": utc_now(),
    }

    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False))

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
