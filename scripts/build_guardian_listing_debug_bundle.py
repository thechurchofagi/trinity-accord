#!/usr/bin/env python3
"""Build a debug bundle for Guardian Stage 2 signed payload mismatch investigation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from agent_authorship_common import (
    authorship_canonical_contract,
    authorship_debug_fingerprint,
    canonical_payload_without_authorship,
)


def run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=90)
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    path = Path(args.payload)
    payload = json.loads(path.read_text(encoding="utf-8"))

    bundle = {
        "schema": "trinity.guardian-listing-debug-bundle.v1",
        "payload_file": str(path),
        "fingerprint": authorship_debug_fingerprint(payload, str(path)),
        "authorship_canonical_contract": authorship_canonical_contract(),
        "canonical_payload_without_authorship": canonical_payload_without_authorship(payload),
        "build_agent_authorship_message_print_digest": run([
            "python3",
            "scripts/build_agent_authorship_message.py",
            str(path),
            "--print-digest",
        ]),
        "build_agent_authorship_message_print_message": run([
            "python3",
            "scripts/build_agent_authorship_message.py",
            str(path),
            "--print-message",
        ]),
        "validate_gateway_payload": run([
            "python3",
            "scripts/validate_gateway_payload.py",
            str(path),
        ]),
        "archive_readiness_gate": run([
            "python3",
            "scripts/archive_readiness_gate.py",
            "--gateway-payload",
            str(path),
            "--json",
        ]),
    }

    out_path = Path(args.out) if args.out else path.with_suffix(path.suffix + ".debug-bundle.json")
    out_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "
", encoding="utf-8")
    print(f"Wrote debug bundle to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
