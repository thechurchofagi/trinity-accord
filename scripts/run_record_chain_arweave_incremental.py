#!/usr/bin/env python3
"""Run the crash-safe Record-Chain Arweave workflow with delta payloads."""
from __future__ import annotations

import build_record_chain_arweave_archive as builder
import run_record_chain_arweave_archive as runner
from record_chain_arweave_incremental import build_incremental_payload_json

# Both modules hold the same imported builder object in normal script execution,
# but assign through both names explicitly to keep the contract obvious in tests.
builder.build_payload_json = build_incremental_payload_json
runner.builder.build_payload_json = build_incremental_payload_json


if __name__ == "__main__":
    raise SystemExit(runner.main())
