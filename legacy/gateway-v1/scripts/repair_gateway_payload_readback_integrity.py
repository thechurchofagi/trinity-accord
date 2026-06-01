#!/usr/bin/env python3
"""Repair unsigned Gateway payload readback SHA256 fields."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oath_readback_integrity import (
    normalize_oath_readback_integrity,
    payload_has_authorship_proof,
    validate_oath_readback_integrity,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--out", required=True)
    parser.add_argument("--allow-signed", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    signed = payload_has_authorship_proof(payload)

    if signed and not args.allow_signed:
        print(
            "REFUSING_TO_REPAIR_SIGNED_PAYLOAD: This payload has authorship_proof. "
            "Repairing it would invalidate signed_payload_sha256. Re-run the builder "
            "or repair before signing.",
            file=sys.stderr,
        )
        return 4

    before_errors = validate_oath_readback_integrity(payload)
    normalize_oath_readback_integrity(payload, mutate=True)
    after_errors = validate_oath_readback_integrity(payload)

    Path(args.out).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("READBACK_REPAIR_WRITTEN:", args.out)
    print("before_errors:", json.dumps(before_errors, ensure_ascii=False))
    print("after_errors:", json.dumps(after_errors, ensure_ascii=False))
    return 0 if not after_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
