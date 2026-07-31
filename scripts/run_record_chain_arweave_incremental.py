#!/usr/bin/env python3
"""Run the crash-safe Record-Chain Arweave workflow with delta payloads."""
from __future__ import annotations

import json
import sys

import build_record_chain_arweave_archive as builder
import run_record_chain_arweave_archive as runner
from arweave_daily_spend_guard import evaluate_daily_spend
from record_chain_arweave_incremental import build_incremental_payload_json

# Both modules hold the same imported builder object in normal script execution,
# but assign through both names explicitly to keep the contract obvious in tests.
builder.build_payload_json = build_incremental_payload_json
runner.builder.build_payload_json = build_incremental_payload_json


def _requested_mode(argv: list[str]) -> str:
    for index, value in enumerate(argv):
        if value == "--mode" and index + 1 < len(argv):
            return argv[index + 1]
        if value.startswith("--mode="):
            return value.split("=", 1)[1]
    return "dry-run"


def main() -> int:
    if _requested_mode(sys.argv[1:]) == "live":
        # A posted transaction whose readback is incomplete is resumed by the
        # crash-safe runner without creating a second transaction. Daily spend
        # limits must block only a new paid post, never this no-cost recovery.
        readback_resume = runner._find_incomplete_current_archive() is not None
        if not readback_resume:
            decision = evaluate_daily_spend("record_chain_arweave_archive")
            if not decision.allowed:
                print(
                    json.dumps(
                        {
                            "result": "not_uploaded",
                            "reason": decision.reason,
                            "kind": decision.kind,
                            "utc_date": decision.utc_date,
                            "paid_count": decision.paid_count,
                            "daily_limit": decision.daily_limit,
                        },
                        sort_keys=True,
                    )
                )
                # Distinct non-zero result: callers must preserve existing metadata
                # and must never reinterpret this as permission to post another tx.
                return 75
        else:
            print("Daily spend gate bypassed for readback-only resume of an existing Arweave transaction.")
    return runner.main()


if __name__ == "__main__":
    raise SystemExit(main())
