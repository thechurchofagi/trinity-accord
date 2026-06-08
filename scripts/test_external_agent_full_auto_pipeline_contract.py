#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    p = ROOT / path
    require(p.exists(), f"missing {path}")
    return p.read_text(encoding="utf-8")


def main() -> None:
    gateway = read("apps/record_chain_intake_gateway/app.py")
    append_wf = read(".github/workflows/record-chain-append.yml")
    ots_wf = read(".github/workflows/record-chain-head-ots-anchor.yml")
    arweave_wf = read(".github/workflows/record-chain-arweave-archive.yml")
    guard = read("scripts/check_record_chain_write_path_guard.py")

    require(
        'TRINITY_APPEND_WORKFLOW_FILE", "record-chain-append.yml"' in gateway,
        "Gateway default append workflow must remain record-chain-append.yml unless this contract is updated",
    )
    require("dispatch_workflow(" in gateway, "Gateway must dispatch append workflow after durable intake writes")
    require('"receipt_id": receipt_id' in gateway, "Gateway append dispatch must pass receipt_id")
    require('"pending_file_path": pending_file_path' in gateway, "Gateway append dispatch must pass pending_file_path")

    require("name: Append Record Chain Entries" in append_wf, "append workflow name must be stable")
    require("workflow_dispatch:" in append_wf, "append workflow must support Gateway dispatch")
    require("record-chain/pending/**" in append_wf, "append workflow must also react to pending pushes")
    require('cron: "*/15 * * * *"' in append_wf, "append workflow must keep scheduled fallback")
    require("trinity_record_chain.py append --all" in append_wf, "append workflow must append pending records")
    require("trinity_record_chain.py verify" in append_wf, "append workflow must verify after append")
    require("Append record-chain entries from Render intake" in append_wf, "append workflow commit message must be stable")

    require("workflow_run:" in ots_wf, "OTS workflow must be triggered by workflow_run")
    require("Record Chain Auto Finalize" in ots_wf, "OTS workflow must keep Auto Finalize compatibility")
    require("Append Record Chain Entries" in ots_wf, "OTS workflow must listen to real Gateway append workflow")
    require("ots_anchor_native_record_chain_head.py" in ots_wf, "OTS workflow must use native OTS script")
    require("record-chain/records/**" not in ots_wf, "OTS must not accept arbitrary records push trigger")
    # Verify push trigger does not include dangerous path globs
    on_section = ""
    in_on = False
    for line in ots_wf.splitlines():
        stripped = line.strip()
        if stripped.startswith("on:"):
            in_on = True
            continue
        if in_on:
            if stripped and not stripped.startswith("#") and not line.startswith(" ") and not line.startswith("\t"):
                break
            on_section += line + "\n"
    require("record-chain/chain-tip.json" not in on_section, "OTS push trigger must not include chain-tip.json")

    require('workflows: ["Record Chain Head OTS Anchor"]' in arweave_wf, "Arweave workflow must listen to OTS workflow")
    require("Check if latest live Arweave archive already matches native head" in arweave_wf, "Arweave workflow must check for already archived head")
    require("No new Arweave archive needed" in arweave_wf, "Arweave workflow must explicitly no-op when already archived")
    require("archive_check.outputs.matched != 'true'" in arweave_wf, "Arweave build/upload steps must be skipped when already archived")
    require("Resolve Arweave upload mode" in arweave_wf, "Arweave workflow must explicitly resolve upload mode")
    require("ARWEAVE_UPLOAD_MODE=live" in arweave_wf, "Arweave workflow_run from OTS must use live mode")
    require("workflow_run from OTS" in arweave_wf, "Arweave live mode must be tied to workflow_run from OTS")
    require("ARWEAVE_UPLOAD_TIMEOUT_SECONDS" in arweave_wf, "Arweave workflow must keep extended upload timeout")
    require("verify_record_chain_arweave_archive.py" in arweave_wf, "Arweave workflow must verify metadata")
    require("trinity_record_chain.py verify" in arweave_wf, "Arweave workflow must verify record chain")
    require("archive: update native record-chain Arweave archive metadata" in arweave_wf, "Arweave commit message must be stable")

    require("APPROVED_APPEND_MESSAGE" in guard, "write-path guard must define append workflow message")
    require("Append record-chain entries from Render intake" in guard, "write-path guard must allow append workflow message")
    require("append workflow commit" in guard, "write-path guard must label append workflow approval")
    require("public_generated" in guard, "write-path guard must account for append/generated public files")

    print("External-agent full-auto pipeline contract PASSED.")


if __name__ == "__main__":
    main()
