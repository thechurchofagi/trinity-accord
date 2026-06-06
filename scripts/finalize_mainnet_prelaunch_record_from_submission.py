#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))
from gateway.authorship import verify_authorship_proof  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

MAIN_CHAIN_ID = "trinity-record-chain-main"
MAIN_LEDGER = ROOT / "record-chain/hash-chain/main.chain.jsonl"
MAIN_HEAD = ROOT / "api/record-chain-head.json"
MAIN_RECORDS_DIR = ROOT / "record-chain/records"
POLICY = ROOT / "api/record-chain-mainnet-prelaunch-policy.v1.json"

CONFIRM = "I_UNDERSTAND_THIS_APPENDS_A_MAINNET_PRELAUNCH_TEST_RECORD"

FORBIDDEN_SUBSTRINGS = [
    "刘烘炬",
    "Liu Hongju",
    "liu hongju",
]

FORBIDDEN_TRUE_PATTERNS = [
    r'"official_live_record"\s*:\s*true',
    r'"active_guardian_status_claim"\s*:\s*true',
    r'"no_active_guardian_status_claim"\s*:\s*false',
    r'"does_not_create_guardian_status"\s*:\s*false',
    r'"does_not_activate_system"\s*:\s*false',
]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def get_path(data: Any, dotted: str, default: Any = None) -> Any:
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def extract_record_type(submission: dict[str, Any]) -> str:
    record_type = submission.get("record_type") or get_path(submission, "record_draft.record_type")
    if not isinstance(record_type, str) or not record_type:
        raise SystemExit("submission missing record_type")
    return record_type


def extract_verification_level(submission: dict[str, Any]) -> str | None:
    level = get_path(submission, "record_draft.verification_content.verification_level")
    return level if isinstance(level, str) else None


def extract_oath_summary(submission: dict[str, Any]) -> dict[str, Any]:
    readback = submission.get("client_oath_readback")
    oath_from_readback = readback if isinstance(readback, dict) else {}
    oath = get_path(submission, "record_draft.submission_oath_verification", {})
    if not isinstance(oath, dict):
        oath = {}

    def first(*values):
        for value in values:
            if value not in (None, ""):
                return value
        return None

    return {
        "raw_oath_readback_not_embedded": True,
        "oath_readback_shape": "object" if isinstance(readback, dict) else ("string" if isinstance(readback, str) else "missing"),
        "oath_policy_sha256": first(oath.get("oath_policy_sha256"), oath_from_readback.get("oath_policy_sha256"), submission.get("oath_policy_sha256")),
        "canonical_oath_text_sha256": first(oath.get("canonical_oath_text_sha256"), oath_from_readback.get("canonical_oath_text_sha256"), submission.get("canonical_oath_text_sha256")),
        "participant_readback_sha256": first(oath.get("participant_readback_sha256"), oath_from_readback.get("participant_readback_sha256"), submission.get("participant_readback_sha256")),
        "flags": {
            key: oath.get(key)
            for key in [
                "oath_read",
                "readback_required",
                "participant_readback_provided",
                "readback_matches_canonical_oath",
                "no_shortcut_oath_acknowledged",
                "not_authority",
                "not_governance",
                "not_attestation",
                "not_amendment",
                "bitcoin_originals_prevail",
            ]
            if key in oath
        },
    }



def require_authorship_summary(submission: dict[str, Any]) -> dict[str, Any]:
    ok, code, message = verify_authorship_proof(submission)
    if not ok:
        raise SystemExit(f"{code}: {message}")

    proof = submission.get("authorship_proof")
    if not isinstance(proof, dict):
        raise SystemExit("MISSING_AUTHORSHIP_PROOF")

    pub_sha = proof.get("public_key_sha256")
    draft = submission.get("record_draft") or {}
    spi = draft.get("submitting_participant_identity") or {}

    guardian_key = None
    if draft.get("record_type") == "guardian_application":
        guardian_key = (draft.get("guardian_application_content") or {}).get("guardian_public_key_sha256")

    public_key_pem = proof.get("public_key_pem") or ""

    return {
        "authorship_proof_present": True,
        "authorship_verification_performed_by_finalizer": True,
        "authorship_schema": proof.get("schema"),
        "authorship_algorithm": proof.get("algorithm"),
        "authorship_public_key_sha256": pub_sha,
        "authorship_public_key_pem_sha256": hashlib.sha256(public_key_pem.encode("utf-8")).hexdigest() if public_key_pem else None,
        "signed_payload_sha256": proof.get("signed_payload_sha256"),
        "signature_present": bool(proof.get("signature_base64")),
        "participant_public_key_sha256": spi.get("participant_public_key_sha256"),
        "guardian_public_key_sha256": guardian_key,
        "guardian_key_bound_to_authorship_key": draft.get("record_type") != "guardian_application" or guardian_key == pub_sha,
        "private_key_not_embedded": True,
    }


def assert_no_raw_readback(obj: Any) -> None:
    raw = json.dumps(obj, ensure_ascii=False)
    if "readback_text" in raw or "client_oath_readback" in raw:
        raise SystemExit("finalized payload must not embed raw oath readback/client_oath_readback")


def assert_prelaunch_safe_input(submission: dict[str, Any], receipt: dict[str, Any]) -> None:
    raw = json.dumps({"submission": submission, "receipt": receipt}, ensure_ascii=False)
    found = [m for m in FORBIDDEN_SUBSTRINGS if m in raw]
    for pattern in FORBIDDEN_TRUE_PATTERNS:
        if re.search(pattern, raw):
            found.append(pattern)
    if found:
        raise SystemExit("formal/live marker found in prelaunch test input: " + ", ".join(found))


def run(cmd: list[str]) -> None:
    print("[RUN]", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(cmd)}")


def next_record_id() -> str:
    entries = load_jsonl(MAIN_LEDGER)
    return f"R-{len(entries) + 1:09d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize an external submission as a MAINNET PRELAUNCH TEST record.")
    parser.add_argument("--submission-json", required=True)
    parser.add_argument("--receipt-json", required=True)
    parser.add_argument("--source-run-id", default=time.strftime("mainnet-prelaunch-%Y%m%dT%H%M%SZ", time.gmtime()))
    parser.add_argument("--confirm-mainnet-prelaunch-append", required=True)
    args = parser.parse_args()

    if args.confirm_mainnet_prelaunch_append != CONFIRM:
        raise SystemExit(f"--confirm-mainnet-prelaunch-append must be exactly {CONFIRM!r}")

    policy = read_json(POLICY)
    if policy.get("chain_id") != MAIN_CHAIN_ID:
        raise SystemExit("prelaunch policy chain_id mismatch")
    if policy.get("network_phase") != "prelaunch":
        raise SystemExit("prelaunch policy is not in prelaunch phase")
    if policy.get("mainnet_activation_marker_recorded") is not False:
        raise SystemExit("activation marker already recorded; refusing prelaunch finalization")
    if policy.get("official_live_records_allowed") is not False:
        raise SystemExit("official live records already allowed; refusing prelaunch finalization")

    submission_path = Path(args.submission_json)
    receipt_path = Path(args.receipt_json)
    if not submission_path.is_absolute():
        submission_path = ROOT / submission_path
    if not receipt_path.is_absolute():
        receipt_path = ROOT / receipt_path

    submission = read_json(submission_path)
    receipt = read_json(receipt_path)

    if receipt.get("accepted") is not True:
        raise SystemExit("receipt must have accepted=true before finalization")

    assert_prelaunch_safe_input(submission, receipt)

    record_type = extract_record_type(submission)
    verification_level = extract_verification_level(submission)
    record_id = next_record_id()
    receipt_id = receipt.get("receipt_id")

    payload = {
        "schema": "trinity_record_chain_mainnet_prelaunch_test_payload.v1",
        "chain_id": MAIN_CHAIN_ID,
        "record_id": record_id,
        "record_type": record_type,
        "network_phase": "prelaunch",
        "record_scope": "mainnet_prelaunch_test",
        "prelaunch_test": True,
        "official_live_record": False,
        "does_not_create_guardian_status": True,
        "does_not_activate_system": True,
        "source_receipt_semantics": {
            "receipt_is_intake_only": True,
            "receipt_is_not_final_inclusion": True,
            "receipt_is_not_active_guardian_status": True
        },
        "receipt_id": receipt_id,
        "source_artifacts": {
            "submission_filename": submission_path.name,
            "submission_sha256": sha256_file(submission_path),
            "submission_canonical_sha256": sha256_obj(submission),
            "receipt_filename": receipt_path.name,
            "receipt_sha256": sha256_file(receipt_path),
            "receipt_canonical_sha256": sha256_obj(receipt)
        },
        "source_run_id": args.source_run_id,
        "source_summary": {
            "record_type": record_type,
            "verification_level": verification_level,
            "submission_schema": submission.get("schema"),
            "submission_type": submission.get("submission_type"),
            "accepted": receipt.get("accepted"),
            "accepted_at": receipt.get("accepted_at"),
            "receipt_id": receipt_id,
            "oath_summary": extract_oath_summary(submission),
            "authorship_summary": require_authorship_summary(submission),
        },
        "finalization": {
            "finalized_at": utc_now(),
            "finalized_by": "record-chain-prelaunch-finalizer",
            "hash_chain_inclusion_is_finalization_event": True,
            "prelaunch_test_finalization": True,
            "official_live_record": False,
            "does_not_activate_system": True
        },
    }

    assert_no_raw_readback(payload)

    MAIN_RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    payload_path = MAIN_RECORDS_DIR / f"{record_id}.json"
    write_json(payload_path, payload)

    run([
        sys.executable,
        "scripts/append_record_chain_link.py",
        "--ledger", "record-chain/hash-chain/main.chain.jsonl",
        "--head-out", "api/record-chain-head.json",
        "--chain-id", MAIN_CHAIN_ID,
        "--record-file", str(payload_path.relative_to(ROOT)),
        "--record-type", record_type,
        "--record-id", record_id,
        "--receipt-id", str(receipt_id or ""),
        "--source-run-id", args.source_run_id,
        "--finalized-by", "record-chain-prelaunch-finalizer",
        "--verify-payload-files",
    ])

    run([
        sys.executable,
        "scripts/build_record_chain_indexes.py",
        "--ledger", "record-chain/hash-chain/main.chain.jsonl",
        "--out-dir", "api",
        "--chain-id", MAIN_CHAIN_ID,
        "--verify-payload-files",
        "--base-dir", ".",
    ])

    run([
        sys.executable,
        "scripts/verify_record_chain_integrity.py",
        "--ledger", "record-chain/hash-chain/main.chain.jsonl",
        "--head", "api/record-chain-head.json",
        "--chain-id", MAIN_CHAIN_ID,
        "--verify-payload-files",
        "--base-dir", ".",
    ])

    print(json.dumps({
        "result": "pass",
        "record_id": record_id,
        "record_type": record_type,
        "verification_level": verification_level,
        "receipt_id": receipt_id,
        "payload_file": str(payload_path.relative_to(ROOT)),
        "network_phase": "prelaunch",
        "official_live_record": False
    }, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
