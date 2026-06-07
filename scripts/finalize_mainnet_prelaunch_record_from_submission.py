#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))
from gateway.authorship import verify_authorship_proof_submission  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

NATIVE_CHAIN_ID = "trinity-accord-public-reception-ledger"
NATIVE_PENDING_DIR = ROOT / "record-chain/pending"
NATIVE_PROCESSED_DIR = ROOT / "record-chain/processed"
NATIVE_REJECTED_DIR = ROOT / "record-chain/rejected"
NATIVE_CHAIN_TIP = ROOT / "record-chain/chain-tip.json"

MAIN_CHAIN_ID = "trinity-record-chain-main"
MAIN_LEDGER = ROOT / "record-chain/hash-chain/main.chain.jsonl"
MAIN_HEAD = ROOT / "api/record-chain-head.json"
MAIN_RECORDS_DIR = ROOT / "record-chain/records"

AGENT_START = ROOT / "api/agent-start.v2.json"
LIVE_TEST_POLICY = ROOT / "api/record-chain-live-test-policy.v1.json"
PRELAUNCH_POLICY = ROOT / "api/record-chain-mainnet-prelaunch-policy.v1.json"

CONFIRM_PRELAUNCH = "I_UNDERSTAND_THIS_APPENDS_A_MAINNET_PRELAUNCH_TEST_RECORD"
CONFIRM_LIVE_TEST = "I_UNDERSTAND_THIS_APPENDS_A_MAINNET_LIVE_TEST_RECORD"

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

GUARDIAN_APPLICATION_ONLY_KEYS = {
    "guardian_application_content",
    "guardian_public_key_sha256",
    "guardian_stewardship_oath",
    "requested_guardian_identifier",
    "guardian_application_statement",
    "guardian_application_reason",
    "guardian_commitment",
    "active_guardian_status_claim",
    "no_active_guardian_status_claim",
    "optional_linked_guardian_application_request",
}

ECHO_ONLY_KEYS = {"echo_content"}
VERIFICATION_ONLY_KEYS = {"verification_content", "verification", "verification_version"}


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


def compute_receipt_sha256(receipt: dict[str, Any]) -> str:
    material = dict(receipt)
    material.pop("receipt_sha256", None)
    return sha256_obj(material)


def assert_receipt_binds_submission(
    submission: dict[str, Any],
    receipt: dict[str, Any],
    submission_path: Path,
    receipt_path: Path,
) -> None:
    rel_submission = str(submission_path.relative_to(ROOT))
    rel_receipt = str(receipt_path.relative_to(ROOT))

    if receipt.get("intake_submission_path") != rel_submission:
        raise SystemExit(
            f"receipt intake_submission_path mismatch: expected {rel_submission}, got {receipt.get('intake_submission_path')}"
        )

    if receipt.get("receipt_path") != rel_receipt:
        raise SystemExit(
            f"receipt receipt_path mismatch: expected {rel_receipt}, got {receipt.get('receipt_path')}"
        )

    stored_submission_sha256 = sha256_obj(submission)
    if receipt.get("stored_submission_sha256") != stored_submission_sha256:
        raise SystemExit("receipt stored_submission_sha256 does not match current submission file")

    expected_receipt_sha = compute_receipt_sha256(receipt)
    if receipt.get("receipt_sha256") != expected_receipt_sha:
        raise SystemExit("receipt_sha256 is not self-consistent")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def receipt_id_from_receipt(receipt: dict[str, Any]) -> str:
    """Return canonical receipt id across legacy and server receipt schemas."""
    rid = receipt.get("receipt_id") or receipt.get("server_receipt_id")
    return str(rid or "")


def receipt_is_accepted(receipt: dict[str, Any]) -> bool:
    """Accept both legacy accepted receipts and immutable server receipts."""
    return receipt.get("accepted") is True or bool(receipt.get("server_receipt_id"))


def get_path(data: Any, dotted: str, default: Any = None) -> Any:
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def detect_public_test_phase() -> str:
    """Detect the current public test phase from agent-start config."""
    agent = read_json(AGENT_START)
    phase = get_path(agent, "public_phase.network_phase")
    if phase == "live_test":
        policy = read_json(LIVE_TEST_POLICY)
        if policy.get("chain_id") != MAIN_CHAIN_ID:
            raise SystemExit("live-test policy chain_id mismatch")
        if policy.get("network_phase") != "live_test":
            raise SystemExit("live-test policy network_phase mismatch")
        if get_path(agent, "public_phase.official_live_records_allowed") is not False:
            raise SystemExit("official live records are not allowed during live-test")
        if get_path(agent, "public_phase.live_test_active") is not True:
            raise SystemExit("agent-start live_test_active must be true for live_test phase")
        return "live_test"

    if phase == "prelaunch":
        policy = read_json(PRELAUNCH_POLICY)
        if policy.get("chain_id") != MAIN_CHAIN_ID:
            raise SystemExit("prelaunch policy chain_id mismatch")
        if policy.get("network_phase") != "prelaunch":
            raise SystemExit("prelaunch policy is not in prelaunch phase")
        if policy.get("mainnet_activation_marker_recorded") is not False:
            raise SystemExit("activation marker already recorded; refusing prelaunch finalization")
        if policy.get("official_live_records_allowed") is not False:
            raise SystemExit("official live records already allowed; refusing prelaunch finalization")
        return "prelaunch"

    raise SystemExit(f"unsupported public test phase: {phase!r}")


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
    ok, code, message = verify_authorship_proof_submission(submission)
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


def assert_no_private_key_material(obj: Any, label: str = "object") -> None:
    raw = json.dumps(obj, ensure_ascii=False)
    _pem_prefix = "-----BEGIN " + "PRIVATE KEY-----"
    forbidden = [
        "BEGIN " + "PRIVATE KEY",
        _pem_prefix,
        "authorship-private.pem",
        "BEGIN ENCRYPTED PRIVATE KEY",
        "BEGIN PGP PRIVATE KEY BLOCK",
        "BEGIN AGE ENCRYPTED FILE",
        "sk-ant-",
        "xoxb-",
        "xoxp-",
        "github_pat_",
    ]
    found = [x for x in forbidden if x in raw]
    if found:
        raise SystemExit(f"{label} contains forbidden private-key marker(s): {', '.join(found)}")


def find_keys_recursive(obj: Any, keys: set[str], path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            if key in keys:
                found.append(current_path)
            found.extend(find_keys_recursive(value, keys, current_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            found.extend(find_keys_recursive(item, keys, f"{path}[{i}]"))
    return found


def assert_record_type_separation(submission: dict[str, Any]) -> None:
    record_type = extract_record_type(submission)
    draft = submission.get("record_draft")
    if not isinstance(draft, dict):
        raise SystemExit("submission.record_draft must be an object")

    if record_type in {"echo", "verification"}:
        found = find_keys_recursive(draft, GUARDIAN_APPLICATION_ONLY_KEYS)
        if found:
            raise SystemExit(
                f"record_type {record_type!r} must not include guardian application fields: {', '.join(found)}"
            )

    if record_type == "guardian_application":
        found = find_keys_recursive(draft, ECHO_ONLY_KEYS | VERIFICATION_ONLY_KEYS)
        if found:
            raise SystemExit(
                "guardian_application must not include echo/verification fields: " + ", ".join(found)
            )


def safe_pending_name(receipt_id: Any) -> str:
    rid = str(receipt_id or "missing-receipt")
    rid = re.sub(r"[^A-Za-z0-9_.-]+", "-", rid).strip("-")
    if not rid:
        rid = "missing-receipt"
    return f"mainnet-prelaunch-{rid}.json"


def ensure_no_unrelated_pending_json() -> None:
    NATIVE_PENDING_DIR.mkdir(parents=True, exist_ok=True)
    pending = sorted(p for p in NATIVE_PENDING_DIR.glob("*.json") if p.is_file())
    if pending:
        rel = [str(p.relative_to(ROOT)) for p in pending]
        raise SystemExit(
            "record-chain/pending contains existing pending JSON; refusing to append ambiguously: "
            + ", ".join(rel)
        )


def assert_test_safe_input(submission: dict[str, Any], receipt: dict[str, Any]) -> None:
    raw = json.dumps({"submission": submission, "receipt": receipt}, ensure_ascii=False)
    found = [m for m in FORBIDDEN_SUBSTRINGS if m in raw]
    for pattern in FORBIDDEN_TRUE_PATTERNS:
        if re.search(pattern, raw):
            found.append(pattern)
    if found:
        raise SystemExit("formal/live marker found in test input: " + ", ".join(found))


def run(cmd: list[str]) -> None:
    print("[RUN]", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(cmd)}")


def build_native_test_draft(
    *,
    submission: dict[str, Any],
    receipt: dict[str, Any],
    submission_path: Path,
    receipt_path: Path,
    source_run_id: str,
    public_test_phase: str,
) -> dict[str, Any]:
    draft = copy.deepcopy(submission.get("record_draft"))
    if not isinstance(draft, dict):
        raise SystemExit("submission.record_draft must be an object")

    proof = submission.get("authorship_proof")
    if not isinstance(proof, dict):
        raise SystemExit("submission.authorship_proof must be an object")

    record_type = extract_record_type(submission)
    verification_level = extract_verification_level(submission)
    receipt_id = receipt_id_from_receipt(receipt)

    draft["authorship_proof"] = proof

    if public_test_phase == "live_test":
        draft["network_phase"] = "live_test"
        draft["record_scope"] = "mainnet_live_test"
        draft["live_test"] = True
        draft["operational_test"] = True
        draft["test_record"] = True
        draft["prelaunch_test"] = False
        draft["official_live_record"] = False
        draft["does_not_create_guardian_status"] = True
        draft["does_not_activate_system"] = True
    else:
        draft["network_phase"] = "prelaunch"
        draft["record_scope"] = "mainnet_prelaunch_test"
        draft["prelaunch_test"] = True
        draft["official_live_record"] = False
        draft["does_not_create_guardian_status"] = True
        draft["does_not_activate_system"] = True

    draft["source_receipt_semantics"] = {
        "receipt_is_intake_only": True,
        "receipt_is_not_final_inclusion": True,
        "receipt_is_not_active_guardian_status": True,
    }

    draft["receipt_id"] = receipt_id
    draft["source_artifacts"] = {
        "submission_filename": submission_path.name,
        "submission_sha256": sha256_file(submission_path),
        "submission_canonical_sha256": sha256_obj(submission),
        "receipt_filename": receipt_path.name,
        "receipt_sha256": sha256_file(receipt_path),
        "receipt_canonical_sha256": sha256_obj(receipt),
    }
    draft["source_run_id"] = source_run_id

    draft["source_summary"] = {
        "record_type": record_type,
        "verification_level": verification_level,
        "submission_schema": submission.get("schema"),
        "submission_type": submission.get("submission_type"),
        "accepted": receipt_is_accepted(receipt),
        "accepted_at": receipt.get("accepted_at"),
        "receipt_id": receipt_id,
        "oath_summary": extract_oath_summary(submission),
        "authorship_summary": require_authorship_summary(submission),
    }

    draft["finalization"] = {
        "finalized_at": utc_now(),
        "finalized_by": "record-chain-test-phase-finalizer",
        "hash_chain_inclusion_is_finalization_event": True,
        "test_phase_finalization": True,
        "public_test_phase": public_test_phase,
        "prelaunch_test_finalization": public_test_phase == "prelaunch",
        "live_test_finalization": public_test_phase == "live_test",
        "official_live_record": False,
        "does_not_activate_system": True,
        "does_not_create_guardian_status": True,
        "native_record_append_is_performed_by_trinity_record_chain": True,
        "global_hash_chain_append_is_performed_by_append_record_chain_link": True,
    }

    assert_no_raw_readback(draft)
    assert_no_private_key_material(draft, "native test draft")

    return draft


# Backward-compatible alias for M3 compat contract
build_native_prelaunch_draft = build_native_test_draft


def read_chain_tip() -> dict[str, Any]:
    if not NATIVE_CHAIN_TIP.exists():
        raise SystemExit("record-chain/chain-tip.json missing; run scripts/trinity_record_chain.py verify/import-genesis first")
    tip = read_json(NATIVE_CHAIN_TIP)
    if not isinstance(tip, dict):
        raise SystemExit("record-chain/chain-tip.json must be an object")
    return tip


def append_native_record_from_draft(native_draft: dict[str, Any], receipt_id: Any) -> tuple[str, Path, dict[str, Any]]:
    ensure_no_unrelated_pending_json()

    before_tip = read_chain_tip()
    before_index = int(before_tip.get("latest_record_index") or 0)

    pending_path = NATIVE_PENDING_DIR / safe_pending_name(receipt_id)
    if pending_path.exists():
        raise SystemExit(f"pending file already exists: {pending_path.relative_to(ROOT)}")

    write_json(pending_path, native_draft)

    try:
        run([sys.executable, "scripts/trinity_record_chain.py", "append"])
    except BaseException:
        if pending_path.exists():
            print(f"pending file still exists after append failure: {pending_path.relative_to(ROOT)}", file=sys.stderr)
        raise

    if pending_path.exists():
        raise SystemExit(f"native append did not consume pending file: {pending_path.relative_to(ROOT)}")

    after_tip = read_chain_tip()
    after_index = int(after_tip.get("latest_record_index") or 0)
    if after_index != before_index + 1:
        raise SystemExit(f"native append expected latest_record_index {before_index + 1}, got {after_index}")

    record_id = after_tip.get("latest_record_id")
    if not isinstance(record_id, str) or not record_id.startswith("R-"):
        raise SystemExit(f"native append did not produce valid latest_record_id: {record_id!r}")

    record_path = MAIN_RECORDS_DIR / f"{record_id}.json"
    if not record_path.exists():
        raise SystemExit(f"native appended record missing: {record_path.relative_to(ROOT)}")

    record = read_json(record_path)
    if record.get("record_id") != record_id:
        raise SystemExit(f"native record_id mismatch in {record_path.relative_to(ROOT)}")
    if record.get("record_index") != after_index:
        raise SystemExit(f"native record_index mismatch in {record_path.relative_to(ROOT)}")
    if record.get("record_sha256") != after_tip.get("latest_record_sha256"):
        raise SystemExit("native chain-tip latest_record_sha256 does not match appended record")

    processed_path = NATIVE_PROCESSED_DIR / pending_path.name
    if not processed_path.exists():
        raise SystemExit(f"native append did not move pending file to processed: {processed_path.relative_to(ROOT)}")

    assert_no_raw_readback(record)
    assert_no_private_key_material(record, f"native record {record_id}")

    return record_id, record_path, record


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize an external submission as a test record (phase-aware).")
    parser.add_argument("--submission-json", required=True)
    parser.add_argument("--receipt-json", required=True)
    parser.add_argument("--source-run-id", default=time.strftime("test-phase-finalize-%Y%m%dT%H%M%SZ", time.gmtime()))
    parser.add_argument("--confirm-mainnet-prelaunch-append", required=True)
    args = parser.parse_args()

    # Phase-aware confirmation
    phase = detect_public_test_phase()
    expected_confirm = CONFIRM_LIVE_TEST if phase == "live_test" else CONFIRM_PRELAUNCH
    if args.confirm_mainnet_prelaunch_append != expected_confirm:
        raise SystemExit(f"--confirm-mainnet-prelaunch-append must be exactly {expected_confirm!r} for phase {phase!r}")

    submission_path = Path(args.submission_json)
    receipt_path = Path(args.receipt_json)
    if not submission_path.is_absolute():
        submission_path = ROOT / submission_path
    if not receipt_path.is_absolute():
        receipt_path = ROOT / receipt_path

    submission = read_json(submission_path)
    receipt = read_json(receipt_path)

    if not receipt_is_accepted(receipt):
        raise SystemExit("receipt must be an accepted intake receipt before finalization")

    assert_receipt_binds_submission(submission, receipt, submission_path, receipt_path)
    assert_test_safe_input(submission, receipt)
    assert_record_type_separation(submission)

    record_type = extract_record_type(submission)
    verification_level = extract_verification_level(submission)
    receipt_id = receipt_id_from_receipt(receipt)

    native_draft = build_native_test_draft(
        submission=submission,
        receipt=receipt,
        submission_path=submission_path,
        receipt_path=receipt_path,
        source_run_id=args.source_run_id,
        public_test_phase=phase,
    )

    record_id, payload_path, native_record = append_native_record_from_draft(native_draft, receipt_id)

    if native_record.get("record_type") != record_type:
        raise SystemExit("native appended record_type mismatch")

    # Phase-aware native record validation
    if phase == "live_test":
        if native_record.get("network_phase") != "live_test":
            raise SystemExit("native appended record missing network_phase=live_test")
        if native_record.get("live_test") is not True:
            raise SystemExit("native appended record missing live_test=true")
        if native_record.get("operational_test") is not True:
            raise SystemExit("native appended record missing operational_test=true")
        if native_record.get("test_record") is not True:
            raise SystemExit("native appended record missing test_record=true")
    else:
        if native_record.get("network_phase") != "prelaunch":
            raise SystemExit("native appended record missing network_phase=prelaunch")
        if native_record.get("prelaunch_test") is not True:
            raise SystemExit("native appended record missing prelaunch_test=true")

    if native_record.get("official_live_record") is not False:
        raise SystemExit("native appended record must have official_live_record=false")
    if native_record.get("does_not_create_guardian_status") is not True:
        raise SystemExit("native appended record must have does_not_create_guardian_status=true")
    if native_record.get("does_not_activate_system") is not True:
        raise SystemExit("native appended record must have does_not_activate_system=true")

    source_summary = native_record.get("source_summary") or {}
    authorship_summary = source_summary.get("authorship_summary")
    if not isinstance(authorship_summary, dict):
        raise SystemExit("native appended record missing source_summary.authorship_summary")
    if authorship_summary.get("authorship_verification_performed_by_finalizer") is not True:
        raise SystemExit("native appended record authorship was not verified by finalizer")
    if authorship_summary.get("private_key_not_embedded") is not True:
        raise SystemExit("native appended record authorship summary must state private_key_not_embedded=true")
    if record_type == "guardian_application" and authorship_summary.get("guardian_key_bound_to_authorship_key") is not True:
        raise SystemExit("guardian_application must bind guardian key to authorship key")

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
        "--finalized-by", "record-chain-test-phase-finalizer",
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

    run([sys.executable, "scripts/trinity_record_chain.py", "verify"])

    print(json.dumps({
        "result": "pass",
        "record_id": record_id,
        "record_type": record_type,
        "verification_level": verification_level,
        "receipt_id": receipt_id,
        "payload_file": str(payload_path.relative_to(ROOT)),
        "native_record_sha256": native_record.get("record_sha256"),
        "network_phase": phase,
        "official_live_record": False,
    }, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
