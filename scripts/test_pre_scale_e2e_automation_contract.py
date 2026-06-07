#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(cond, msg):
    if not cond:
        raise SystemExit(msg)

def main():
    required = [
        "scripts/auto_finalize_accepted_submissions.py",
        ".github/workflows/record-chain-auto-finalize.yml",
        ".github/workflows/record-chain-head-ots-anchor.yml",
        ".github/workflows/pre-scale-e2e-orchestrator-v2.yml",
        ".github/workflows/record-chain-data-arweave-archive.yml",
    ]
    for rel in required:
        require((ROOT / rel).exists(), f"missing {rel}")

    auto = (ROOT / "scripts/auto_finalize_accepted_submissions.py").read_text(encoding="utf-8")
    require("finalize_mainnet_prelaunch_record_from_submission.py" in auto, "auto finalizer must call finalizer")
    require("verify_record_chain_integrity.py" in auto, "auto finalizer must verify hash chain")
    require("trinity_record_chain.py" in auto, "auto finalizer must verify native chain")
    require("already finalized" in auto, "auto finalizer must be idempotent by receipt_id")

    head_ots = (ROOT / ".github/workflows/record-chain-head-ots-anchor.yml").read_text(encoding="utf-8")
    require("ots_anchor_record_chain_head.py" in head_ots, "head OTS workflow must stamp current head")
    require("workflow_run" in head_ots, "head OTS workflow must be chainable after auto finalize")

    orchestrator = (ROOT / ".github/workflows/pre-scale-e2e-orchestrator-v2.yml").read_text(encoding="utf-8")
    require("auto_finalize_accepted_submissions.py" in orchestrator, "orchestrator must run auto finalize")
    require("build_record_chain_data_arweave_bundle.py" in orchestrator, "orchestrator must build data bundle")
    require("run_phase5_ots_arweave_paid_upload.py" in orchestrator, "orchestrator must run Phase 5 OTS upload")
    require("I_UNDERSTAND_THIS_RUNS_PRE_SCALE_E2E_AUTOMATION" in orchestrator, "live orchestrator must have confirm guard")
    require("secrets.ARKEY" in orchestrator, "orchestrator must use GitHub Secret ARKEY")
    require("verify_ots_arweave_registry.py" in orchestrator, "orchestrator must verify OTS registry")
    require("run_current_system_tests.py" in orchestrator, "orchestrator must run current tests")

    # Paid upload guard: --enable-paid-upload must be passed to Phase 5
    require("--enable-paid-upload" in orchestrator, "orchestrator must pass --enable-paid-upload to Phase 5 script")

    # Duplicate upload prevention: latest_by_head registry check
    require("latest_by_head" in orchestrator, "orchestrator must check latest_by_head in OTS registry to skip duplicate uploads")

    print("PASS: pre-scale e2e automation contract")

if __name__ == "__main__":
    main()
