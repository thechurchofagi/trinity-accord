#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: str) -> dict[str, Any]:
    p = ROOT / path
    require(p.exists(), f"missing {path}")
    data = json.loads(p.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must be a JSON object")
    return data


def main() -> None:
    agent_start = (ROOT / "agent-start.md").read_text(encoding="utf-8")
    record_status = load_json("api/record-chain-status.json")
    production_policy = load_json("api/record-chain-production-enablement-policy.v1.json")
    native_ots = load_json("api/record-chain-native-ots-latest.json")
    arweave_index = load_json("api/record-chain-arweave-index.json")
    chain_tip = load_json("record-chain/chain-tip.json")
    public_home = load_json("api/public-home-status.json")

    require(
        "Current phase: production live / public submission open" in agent_start,
        "agent-start.md must announce production live / public submission open",
    )
    for forbidden in [
        "Current phase: public test / stabilization",
        "still in test/stabilization",
        "Submissions during this phase may be treated as test data",
        "\u6b63\u5f0f\u5f00\u653e\u524d\u91cd\u65b0\u5206\u7c7b",
    ]:
        require(forbidden not in agent_start, f"agent-start.md contains retired test-phase wording: {forbidden}")

    require(
        "receipt is still intake-only" in agent_start.lower(),
        "agent-start.md must preserve receipt-is-intake-only boundary",
    )
    require(
        "External agents do not need GitHub access." in agent_start,
        "agent-start.md must preserve no-GitHub-access external submission statement",
    )

    require(production_policy.get("status") == "active", "production policy must be active")
    require(production_policy.get("network_phase") == "production", "production policy network_phase must be production")
    semantics = production_policy.get("production_enablement_semantics", {})
    require(
        semantics.get("official_live_record_true_now_permitted") is True,
        "production policy must permit official_live_record true",
    )

    latest_record_id = chain_tip.get("latest_record_id")
    native_record_count = chain_tip.get("native_record_count")
    latest_record_sha256 = chain_tip.get("latest_record_sha256")
    require(isinstance(latest_record_id, str) and latest_record_id.startswith("R-"), "invalid chain-tip latest record")
    require(isinstance(native_record_count, int) and native_record_count >= 33, "native_record_count must be at least M9 count")
    require(isinstance(latest_record_sha256, str) and len(latest_record_sha256) == 64, "latest record sha256 invalid")

    require(record_status.get("schema") == "trinityaccord.record-chain-status.v1", "record-chain-status schema mismatch")
    require(record_status.get("status") == "production_live", "record-chain-status.status must be production_live")

    public_phase = record_status.get("public_phase", {})
    require(public_phase.get("network_phase") == "production", "public_phase.network_phase must be production")
    require(public_phase.get("status") == "production_live", "public_phase.status must be production_live")
    require(public_phase.get("official_live_records_allowed") is True, "official live records must be allowed")
    require(public_phase.get("not_final_public_launch") is False, "not_final_public_launch must be false")
    require(public_phase.get("production_enablement_marker_recorded") is True, "production enablement marker must be recorded")
    require(public_phase.get("receipt_is_intake_only") is True, "receipt boundary must remain intake-only")
    require(public_phase.get("bitcoin_originals_prevail") is True, "Bitcoin Originals boundary must remain")

    submission = record_status.get("public_submission_phase", {})
    require(submission.get("phase") == "production_live", "public_submission_phase.phase must be production_live")
    require(submission.get("status") == "production_live", "public_submission_phase.status must be production_live")
    require(submission.get("gateway_operational") is True, "gateway must remain operational")
    require(submission.get("official_live_records_allowed") is True, "submission phase must allow official live records")
    require(
        submission.get("public_gateway") == "https://trinity-record-chain-gateway.onrender.com",
        "public gateway mismatch",
    )

    receipt_boundary = submission.get("receipt_boundary", {})
    require(receipt_boundary.get("receipts_are_intake_only") is True, "receipts must remain intake-only")
    external_boundary = submission.get("external_agent_boundary", {})
    for key in [
        "external_agents_must_not_clone_repository",
        "external_agents_must_not_directly_append_record_chain",
        "external_agents_must_not_request_github_pat",
        "external_agents_must_not_use_arweave_key",
        "external_agents_must_use_public_gateway_for_submissions",
    ]:
        require(external_boundary.get(key) is True, f"external boundary missing {key}")

    rc = record_status.get("record_chain", {})
    require(rc.get("latest_record_id") == latest_record_id, "record-chain-status latest_record_id mismatch")
    require(rc.get("latest_record_sha256") == latest_record_sha256, "record-chain-status latest_record_sha256 mismatch")
    require(rc.get("native_record_count") == native_record_count, "record-chain-status native count mismatch")
    require(rc.get("legacy_main_chain_jsonl_is_not_current_source") is True, "legacy JSONL must not be current source")

    ots = record_status.get("anchoring", {}).get("open_timestamps", {})
    ots_matches_chain = (
        native_ots.get("latest_record_id") == latest_record_id
        and native_ots.get("latest_record_sha256") == latest_record_sha256
        and native_ots.get("native_record_count") == native_record_count
    )
    if native_ots.get("bitcoin_verified") is True:
        expected_ots_status = "verified-bitcoin"
    elif ots_matches_chain and native_ots.get("ots_status") == "pending":
        expected_ots_status = "current-pending-bitcoin"
    else:
        expected_ots_status = "anchor-needed"
    require(ots.get("status") == expected_ots_status, f"OTS public status mismatch: expected {expected_ots_status}, got {ots.get('status')}")
    require(ots.get("latest_record_id") == native_ots.get("latest_record_id"), "OTS latest record mismatch")
    require(ots.get("latest_record_sha256") == native_ots.get("latest_record_sha256"), "OTS latest record sha mismatch")
    require(ots.get("native_record_count") == native_ots.get("native_record_count"), "OTS native record count mismatch")
    require(ots.get("bitcoin_pending") == (native_ots.get("bitcoin_pending") is True), "OTS bitcoin_pending mismatch")
    require(ots.get("bitcoin_verified") == (native_ots.get("bitcoin_verified") is True), "OTS bitcoin_verified mismatch")
    require(ots.get("legacy_main_chain_jsonl_is_not_source") is True, "OTS must not use legacy JSONL")
    require(ots.get("anchor_needed") == (not ots_matches_chain), "OTS anchor_needed must reflect chain match state")

    ar = record_status.get("anchoring", {}).get("arweave_archive", {})
    require(ar.get("current_upload_mode") == arweave_index.get("current_upload_mode"), "Arweave mode mismatch")
    require(ar.get("live_upload_enabled") is True, "Arweave live upload must be enabled")
    require(ar.get("live_upload_implemented") is True, "Arweave live upload must be implemented")
    require(ar.get("live_archive_count") == arweave_index.get("live_archive_count"), "Arweave live count mismatch")
    require(ar.get("latest_arweave_txid") == arweave_index.get("latest_arweave_txid"), "Arweave txid mismatch")
    require(ar.get("source_type") == "native-record-chain", "Arweave source_type must be native-record-chain")
    require(ar.get("arweave_archive_is_mirror_only") is True, "Arweave must remain mirror-only")
    require(bool(arweave_index.get("latest_arweave_txid")), "arweave index must have latest txid")
    require(arweave_index.get("current_upload_mode") == "live", "arweave index mode must be live")
    require(arweave_index.get("live_archive_count", 0) >= 1, "arweave index live count must be positive")

    current = public_home.get("current_record_chain_status", {})
    require(current.get("phase") == "production_live", "public-home-status phase must be production_live")
    require(current.get("total_records") == native_record_count, "public-home-status total_records must match chain-tip")
    require(current.get("latest_record_id") == latest_record_id, "public-home latest record mismatch")
    ar_home = current.get("anchoring", {}).get("arweave_index", {})
    require(ar_home.get("current_upload_mode") == "live", "public-home arweave mode must be live")
    require(ar_home.get("latest_arweave_txid") == arweave_index.get("latest_arweave_txid"), "public-home txid mismatch")

    print("Public production status alignment PASSED.")


if __name__ == "__main__":
    main()
