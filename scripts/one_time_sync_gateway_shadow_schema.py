#!/usr/bin/env python3
from pathlib import Path

public = Path("api/record-chain-submission-schema.v1.json")
shadow = Path("apps/record_chain_intake_gateway/schemas/record_chain_submission.schema.json")
raw = public.read_bytes()
shadow.write_bytes(raw)
if shadow.read_bytes() != raw:
    raise SystemExit("shadow schema byte synchronization failed")
print("Gateway shadow schema synchronized byte-for-byte.")
