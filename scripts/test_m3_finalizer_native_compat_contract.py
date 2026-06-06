#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINALIZER = ROOT / "scripts/finalize_mainnet_prelaunch_record_from_submission.py"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(msg)


def main() -> int:
    src = FINALIZER.read_text(encoding="utf-8")

    require("build_native_prelaunch_draft" in src, "finalizer must build native prelaunch draft")
    require("append_native_record_from_draft" in src, "finalizer must append via native helper")
    require("record-chain/pending" in src or "NATIVE_PENDING_DIR" in src, "finalizer must write native pending draft")
    require("scripts/trinity_record_chain.py" in src and '"append"' in src, "finalizer must call trinity_record_chain.py append")
    require("scripts/trinity_record_chain.py" in src and '"verify"' in src, "finalizer must call trinity_record_chain.py verify")
    require("scripts/append_record_chain_link.py" in src, "finalizer must append native record to global hash ledger")
    require("authorship_proof" in src, "finalizer must bridge top-level authorship_proof into native draft")
    require("source_summary" in src and "authorship_summary" in src, "finalizer must preserve authorship_summary")
    require("client_oath_readback" in src and "readback_text" in src, "finalizer must guard raw oath readback")
    require("ensure_no_unrelated_pending_json" in src, "finalizer must refuse ambiguous pending JSON")
    require("processed_path" in src and "NATIVE_PROCESSED_DIR" in src, "finalizer must verify native pending moved to processed")

    forbidden_fragments = [
        'payload_path = MAIN_RECORDS_DIR / f"{record_id}.json"',
        "write_json(payload_path, payload)",
        "record_id = next_record_id()",
    ]
    for frag in forbidden_fragments:
        require(frag not in src, f"legacy direct record write path remains: {frag}")

    print("PASS: m3 finalizer native compatibility contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
