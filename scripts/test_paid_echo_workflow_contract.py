#!/usr/bin/env python3
from pathlib import Path
import re
import sys

WORKFLOW = Path(".github/workflows/paid-echo-arweave-canary.yml")

def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)

def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    if "name: Paid Echo Arweave Canary" not in text:
        fail("workflow name changed or missing")

    if 'EXPECTED_ARWEAVE_OWNER: "r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s"' not in text:
        fail("expected Arweave owner is missing or changed")

    if "ARWEAVE_MAX_UPLOAD_USD: ${{ github.event.inputs.max_upload_usd || '0.10' }}" not in text:
        fail("max upload USD env is missing")

    if 'ARWEAVE_SAFETY_MULTIPLIER: "1.20"' not in text:
        fail("safety multiplier is missing")

    if "ALLOW_PAID_ARWEAVE_CANARY" not in text:
        fail("ALLOW_PAID_ARWEAVE_CANARY env is missing")

    if "Guard first paid canary scope" not in text:
        fail("paid canary scope guard is missing")

    if 'github.event.inputs.record_type }}\" != \"echo\"' not in text:
        fail("paid canary guard must reject non-echo record types")

    # Ensure the workflow does not silently build only echo while accepting other record types.
    # It may either offer only echo in choices or have the hard guard above.
    record_type_block = re.search(
        r"record_type:\n(?P<body>(?:        .+\n)+)",
        text,
    )
    if not record_type_block:
        fail("record_type workflow_dispatch input not found")

    body = record_type_block.group("body")
    non_echo_options = [
        opt for opt in ("verification", "guardian_application")
        if f"- {opt}" in body
    ]

    if non_echo_options and "Guard first paid canary scope" not in text:
        fail(f"non-echo options present without hard guard: {non_echo_options}")

    print("PASS: paid echo workflow contract")

if __name__ == "__main__":
    main()
