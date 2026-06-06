#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from native_prelaunch_finalization import (
    ROOT,
    RECORDS,
    CHAIN_TIP,
    MAIN_LEDGER,
    MAIN_HEAD,
    read_json_lenient,
    write_json_native,
    sha256_file,
    record_index_from_id,
    build_native_record_from_submission,
    ensure_genesis_manifest,
    load_existing_native_records,
    update_chain_tip_from_native_records,
    rebuild_global_hash_chain_entries_for_records,
    rebuild_all_indexes,
    verify_all,
    utc_now,
)

CONFIRM = "I_UNDERSTAND_THIS_REWRITES_PHASE7D_PRELAUNCH_RECORDS_TO_NATIVE_SCHEMA"

EXPECTED = [
    ("echo", "echo.submission.json", "echo.receipt.json"),
    ("verification", "verification-v0.submission.json", "verification-v0.receipt.json"),
    ("verification", "verification-v1.submission.json", "verification-v1.receipt.json"),
    ("verification", "verification-v2.submission.json", "verification-v2.receipt.json"),
    ("verification", "verification-v3.submission.json", "verification-v3.receipt.json"),
    ("guardian_application", "guardian-application.submission.json", "guardian-application.receipt.json"),
]


def audit_before(target_ids: list[str], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for rel in [
        "record-chain/chain-tip.json",
        "record-chain/hash-chain/main.chain.jsonl",
        "api/record-chain-head.json",
    ]:
        p = ROOT / rel
        if p.exists():
            files.append({"path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size})
    for rid in target_ids:
        p = RECORDS / f"{rid}.json"
        if p.exists():
            files.append({"path": str(p.relative_to(ROOT)), "sha256": sha256_file(p), "bytes": p.stat().st_size})
    write_json_native(out_dir / "phase7d-native-schema-gap-before-summary.json", {
        "schema": "trinityaccord.phase7d-native-schema-gap-repair-before.v1",
        "generated_at": utc_now(),
        "target_record_ids": target_ids,
        "files": files,
        "note": "SHA/size only. No raw records copied to avoid duplicating transient oath/private material.",
    })


def assert_target_records_are_safe_to_rewrite(target_ids: list[str]) -> None:
    existing = load_existing_native_records()
    indexes = sorted(record_index_from_id(rid) for rid in existing if re.fullmatch(r"R-\d{9}", rid))

    if not indexes:
        raise SystemExit("No native R-*.json records found")

    target_indexes = [record_index_from_id(rid) for rid in target_ids]
    first = min(target_indexes)
    last = max(target_indexes)

    if target_indexes != list(range(first, last + 1)):
        raise SystemExit(f"target ids must be contiguous, got {target_ids}")

    missing = [rid for rid in target_ids if rid not in existing]
    if missing:
        raise SystemExit(f"target native records missing before repair: {missing}")

    tail = [idx for idx in indexes if idx > last]
    if tail:
        raise SystemExit(
            "Refusing repair because native records exist after target range. "
            f"Tail indexes: {tail}. This script only repairs the current tail range."
        )

    for rid in target_ids:
        rec = existing[rid]
        if rec.get("prelaunch_test") is not True:
            raise SystemExit(f"{rid}: not marked prelaunch_test=true; refusing rewrite")
        if rec.get("official_live_record") is True:
            raise SystemExit(f"{rid}: official_live_record=true; refusing rewrite")
        raw = json.dumps(rec, ensure_ascii=False)
        if "Liu Hongju" in raw or "刘烘炬" in raw:
            raise SystemExit(f"{rid}: appears to contain formal Liu Hongju marker; refusing rewrite")


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair Phase 7D prelaunch records to native full-verifier schema.")
    parser.add_argument("--external-dir", required=True, help="Directory containing six submission/receipt pairs.")
    parser.add_argument("--record-ids", default="R-000000011,R-000000012,R-000000013,R-000000014,R-000000015,R-000000016")
    parser.add_argument("--source-run-id", default="phase7d-mandatory-key-prelaunch")
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args()

    if args.confirm != CONFIRM:
        raise SystemExit(f"--confirm must be exactly {CONFIRM!r}")

    external_dir = Path(args.external_dir)
    if not external_dir.is_absolute():
        external_dir = ROOT / external_dir
    if not external_dir.exists():
        raise SystemExit(f"external dir missing: {external_dir}")

    target_ids = [x.strip() for x in args.record_ids.split(",") if x.strip()]
    if len(target_ids) != len(EXPECTED):
        raise SystemExit("record-id count must match expected six records")

    ensure_genesis_manifest()
    assert_target_records_are_safe_to_rewrite(target_ids)
    audit_before(target_ids, ROOT / "record-chain/audit/phase7d-native-schema-gap")

    existing = load_existing_native_records()
    first_idx = min(record_index_from_id(rid) for rid in target_ids)

    previous_sha = None
    if first_idx > 1:
        prev_id = f"R-{first_idx - 1:09d}"
        prev = existing.get(prev_id)
        if not prev:
            raise SystemExit(f"Missing previous native record {prev_id}")
        previous_sha = prev.get("record_sha256")
        if not previous_sha:
            raise SystemExit(f"Previous native record {prev_id} missing record_sha256")

    generated = []
    public_keys = set()

    for rid, (expected_type, sub_name, rec_name) in zip(target_ids, EXPECTED):
        sub_path = external_dir / sub_name
        rec_path = external_dir / rec_name
        if not sub_path.exists():
            raise SystemExit(f"missing submission: {sub_path}")
        if not rec_path.exists():
            raise SystemExit(f"missing receipt: {rec_path}")

        submission = read_json_lenient(sub_path)
        receipt = read_json_lenient(rec_path)
        actual_type = submission.get("record_type") or (submission.get("record_draft") or {}).get("record_type")
        if actual_type != expected_type:
            raise SystemExit(f"{sub_name}: expected record_type={expected_type}, got {actual_type}")

        proof = submission.get("authorship_proof") or {}
        pub = proof.get("public_key_sha256")
        if not isinstance(pub, str):
            raise SystemExit(f"{sub_name}: missing authorship public key")
        public_keys.add(pub)

        assigned_at = (existing.get(rid) or {}).get("assigned_at") or utc_now()
        record = build_native_record_from_submission(
            submission=submission,
            receipt=receipt,
            submission_path=sub_path,
            receipt_path=rec_path,
            record_id=rid,
            previous_record_sha256=previous_sha,
            assigned_at=assigned_at,
            source_run_id=args.source_run_id,
            finalized_by="phase7d-native-schema-gap-repair",
        )

        out = RECORDS / f"{rid}.json"
        write_json_native(out, record)
        generated.append(rid)
        previous_sha = record["record_sha256"]
        print(f"[REPAIRED] {rid} {record['record_type']} {record['record_sha256']}")

    if len(public_keys) != 1:
        raise SystemExit(f"Expected one shared public key across six submissions, got {sorted(public_keys)}")

    update_chain_tip_from_native_records()
    rebuild_global_hash_chain_entries_for_records(generated)
    rebuild_all_indexes()
    verify_all()

    print(json.dumps({
        "result": "pass",
        "repaired_record_ids": generated,
        "shared_authorship_public_key_sha256": sorted(public_keys)[0],
        "hash_chain_head": read_json_lenient(MAIN_HEAD).get("head_entry_hash"),
        "native_latest_record_sha256": read_json_lenient(CHAIN_TIP).get("latest_record_sha256"),
        "ledger_file": str(MAIN_LEDGER.relative_to(ROOT)),
    }, indent=2, sort_keys=True, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
