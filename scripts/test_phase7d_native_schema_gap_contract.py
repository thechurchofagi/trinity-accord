#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGET_IDS = [
    "R-000000011",
    "R-000000012",
    "R-000000013",
    "R-000000014",
    "R-000000015",
    "R-000000016",
]

BOUNDARY_KEYS = [
    "not_authority",
    "not_governance",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str):
    if not cond:
        raise SystemExit(msg)


def run(cmd):
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"command failed: {' '.join(cmd)}")
    return result


def is_hex64(v):
    return isinstance(v, str) and re.fullmatch(r"[a-f0-9]{64}", v) is not None


def main():
    previous = None
    public_keys = set()

    for rid in TARGET_IDS:
        path = ROOT / "record-chain/records" / f"{rid}.json"
        require(path.exists(), f"missing {path}")
        rec = read_json(path)

        require(rec.get("record_id") == rid, f"{rid}: record_id mismatch")
        require(isinstance(rec.get("record_index"), int), f"{rid}: missing record_index")
        require(is_hex64(rec.get("content_sha256")), f"{rid}: content_sha256 invalid")
        require(is_hex64(rec.get("record_sha256")), f"{rid}: record_sha256 invalid")
        require(rec.get("previous_record_sha256") == previous, f"{rid}: previous_record_sha256 mismatch")

        boundary = rec.get("boundary_acknowledgement") or rec.get("boundary") or {}
        for key in BOUNDARY_KEYS:
            require(boundary.get(key) is True, f"{rid}: boundary missing/false {key}")

        proof = rec.get("authorship_proof")
        require(isinstance(proof, dict), f"{rid}: missing authorship_proof")
        pub = proof.get("public_key_sha256")
        require(is_hex64(pub), f"{rid}: bad authorship public key")
        public_keys.add(pub)

        avs = rec.get("authorship_verification_status")
        require(isinstance(avs, dict), f"{rid}: missing authorship_verification_status")
        require(avs.get("signed_payload_scope") == "pre_append_record_draft", f"{rid}: bad signed_payload_scope")
        require(avs.get("verified_by_gateway_before_pending") is True, f"{rid}: gateway verification flag missing")
        require(avs.get("final_record_contains_append_assigned_fields_not_in_signed_payload") is True, f"{rid}: append assignment flag missing")

        require(rec.get("prelaunch_test") is True, f"{rid}: prelaunch_test must be true")
        require(rec.get("official_live_record") is False, f"{rid}: official_live_record must be false")
        require(rec.get("does_not_create_guardian_status") is True, f"{rid}: guardian status boundary missing")
        require(rec.get("does_not_activate_system") is True, f"{rid}: activation boundary missing")

        raw = json.dumps(rec, ensure_ascii=False)
        require("BEGIN PRIVATE KEY" not in raw, f"{rid}: private key leak")
        require("authorship-private.pem" not in raw, f"{rid}: private key filename leak")
        require("client_oath_readback" not in raw, f"{rid}: raw oath readback leaked")
        require("readback_text" not in raw, f"{rid}: readback_text leaked")
        require('"official_live_record": true' not in raw, f"{rid}: official live marker leak")

        previous = rec["record_sha256"]

    require(len(public_keys) == 1, f"expected one shared public key, got {sorted(public_keys)}")

    # Both verifiers must pass.
    run([sys.executable, "scripts/trinity_record_chain.py", "verify"])
    run([
        sys.executable,
        "scripts/verify_record_chain_integrity.py",
        "--ledger", "record-chain/hash-chain/main.chain.jsonl",
        "--head", "api/record-chain-head.json",
        "--chain-id", "trinity-record-chain-main",
        "--verify-payload-files",
        "--base-dir", ".",
    ])

    print("PASS: phase7d native schema gap contract")


if __name__ == "__main__":
    main()
