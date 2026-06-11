#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

from record_chain_hashing import (
    NATIVE_OTS_ANCHOR_SCHEMA,
    OTS_ANCHOR_SCHEMA,
    load_json,
    sha256_bytes,
    write_json_atomic,
)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_cmd(cmd: list[str], timeout: int = 90) -> subprocess.CompletedProcess[str]:
    import shutil as _shutil
    wrapped = list(cmd)
    if _shutil.which("timeout"):
        wrapped = ["timeout", "--signal=KILL", str(timeout)] + cmd
    try:
        result = subprocess.run(
            wrapped,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout + 5,
        )
        # timeout command returns 124 on SIGTERM/timeout
        if result.returncode == 124 or (result.returncode == -9):
            return subprocess.CompletedProcess(
                cmd, returncode=-1, stdout=result.stdout,
                stderr=result.stderr + f"\ncommand timed out after {timeout}s"
            )
        return result
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            cmd, returncode=-1, stdout="", stderr=f"command timed out after {timeout}s"
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


def has_bitcoin_block_header_attestation(text: str) -> bool:
    """Check if ots info output contains a BitcoinBlockHeaderAttestation."""
    return "bitcoinblockheaderattestation" in text.lower()


def run_ots_info(ots_bin: str, ots_file: Path, timeout: int = 90) -> subprocess.CompletedProcess[str]:
    """Run `ots info` and return the result."""
    cmd = [ots_bin, "info", str(ots_file)]
    return run_cmd(cmd, timeout=timeout)


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
    if anchor.get("schema") not in {NATIVE_OTS_ANCHOR_SCHEMA, OTS_ANCHOR_SCHEMA}:
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
    calendar_attested = False
    bitcoin_attestation_embedded = False
    strict_bitcoin_verified = False
    strict_verify_unavailable_reason = None

    ots_info_command = None
    ots_info_exit_code = None
    ots_info_stdout = None
    ots_info_stderr = None

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

                upgrade_text = f"{upgrade.stdout}\n{upgrade.stderr}".lower()
                if upgrade.returncode == 0 and "success" in upgrade_text and "timestamp complete" in upgrade_text:
                    # Calendar returned BitcoinBlockHeaderAttestation; proof upgraded.
                    # This does NOT mean strict Bitcoin verify was done.
                    calendar_attested = True
                    bitcoin_attestation_embedded = True
                    bitcoin_pending = False
                elif is_pending_output(upgrade_text):
                    bitcoin_pending = True
                    calendar_attested = True

            # Run ots info to detect BitcoinBlockHeaderAttestation
            if ots_file and ots_file.exists():
                info_result = run_ots_info(args.ots_bin, ots_file)
                ots_info_command = [args.ots_bin, "info", str(ots_file)]
                ots_info_exit_code = info_result.returncode
                ots_info_stdout = info_result.stdout
                ots_info_stderr = info_result.stderr

                info_text = f"{info_result.stdout}\n{info_result.stderr}"
                if has_bitcoin_block_header_attestation(info_text):
                    bitcoin_attestation_embedded = True
                    calendar_attested = True

            if not bitcoin_verified:
                if not args.bitcoin_node_url:
                    # No Bitcoin node available; cannot do strict verify
                    strict_verify_unavailable_reason = "no_bitcoin_node"
                    if bitcoin_attestation_embedded:
                        # ots info shows BitcoinBlockHeaderAttestation — proof is upgraded
                        bitcoin_pending = False
                    elif not bitcoin_pending:
                        # Check verify output for pending markers
                        ots_verify_command = [args.ots_bin]
                        ots_verify_command += ["verify", str(ots_file)]

                        verify = run_cmd(ots_verify_command)
                        ots_verify_exit_code = verify.returncode
                        ots_verify_stdout = verify.stdout
                        ots_verify_stderr = verify.stderr

                        combined = f"{verify.stdout}\n{verify.stderr}"
                        if args.upgrade:
                            combined += f"\n{upgrade.stdout}\n{upgrade.stderr}"

                        if is_pending_output(combined):
                            bitcoin_pending = True
                            calendar_attested = True
                else:
                    # Bitcoin node available — do strict verify
                    ots_verify_command = [args.ots_bin]
                    ots_verify_command += ["--bitcoin-node", args.bitcoin_node_url]
                    ots_verify_command += ["verify", str(ots_file)]

                    verify = run_cmd(ots_verify_command)
                    ots_verify_exit_code = verify.returncode
                    ots_verify_stdout = verify.stdout
                    ots_verify_stderr = verify.stderr

                    combined = f"{verify.stdout}\n{verify.stderr}"
                    if args.upgrade:
                        combined += f"\n{upgrade.stdout}\n{upgrade.stderr}"

                    upgrade_timed_out = args.upgrade and upgrade.returncode == -1

                    if verify.returncode == 0 and is_success_output(combined):
                        bitcoin_verified = True
                        strict_bitcoin_verified = True
                    elif is_pending_output(combined):
                        bitcoin_pending = True
                        calendar_attested = True
                        if args.strict_bitcoin:
                            errors.append("OTS proof is pending and not Bitcoin-verified yet")
                    elif upgrade_timed_out:
                        bitcoin_pending = True
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
    anchor["ots_info_command"] = ots_info_command
    anchor["ots_info_exit_code"] = ots_info_exit_code
    anchor["ots_info_stdout"] = ots_info_stdout
    anchor["ots_info_stderr"] = ots_info_stderr
    anchor["bitcoin_verified"] = bitcoin_verified
    anchor["bitcoin_pending"] = bitcoin_pending
    anchor["calendar_attested"] = calendar_attested
    anchor["bitcoin_attestation_embedded"] = bitcoin_attestation_embedded
    anchor["strict_bitcoin_verified"] = strict_bitcoin_verified
    anchor["strict_verify_unavailable_reason"] = strict_verify_unavailable_reason
    anchor["ots_status"] = "verified" if bitcoin_verified else ("upgraded" if bitcoin_attestation_embedded else "pending")

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
        "calendar_attested": calendar_attested,
        "bitcoin_attestation_embedded": bitcoin_attestation_embedded,
        "strict_bitcoin_verified": strict_bitcoin_verified,
        "strict_verify_unavailable_reason": strict_verify_unavailable_reason,
        "strict_bitcoin": args.strict_bitcoin,
        "errors": errors,
        "generated_at": utc_now(),
    }

    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False))

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
