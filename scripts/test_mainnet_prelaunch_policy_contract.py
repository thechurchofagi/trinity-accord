#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

POLICY = ROOT / "api/record-chain-mainnet-prelaunch-policy.v1.json"
AGENT_START = ROOT / "api/agent-start.v2.json"
GATEWAY = ROOT / "api/record-chain-intake-gateway.v1.json"
MAIN_HEAD = ROOT / "api/record-chain-head.json"
MAIN_LEDGER = ROOT / "record-chain/hash-chain/main.chain.jsonl"

FORBIDDEN_ACTIVE_PATHS = [
    ROOT / "api/record-chain-testnet",
    ROOT / "record-chain/testnet",
]

FORBIDDEN_SCRIPTS = [
    ROOT / "scripts/init_record_chain_testnet.py",
    ROOT / "scripts/finalize_testnet_record_from_submission.py",
    ROOT / "scripts/run_testnet_ots_archive.py",
    ROOT / "scripts/test_record_chain_testnet_contract.py",
    ROOT / "scripts/summarize_external_agent_real_test_results.py",
    ROOT / "scripts/verify_phase7b_real_testnet_outputs.py",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    require(POLICY.exists(), "missing mainnet prelaunch policy")
    require(AGENT_START.exists(), "missing agent-start")
    require(GATEWAY.exists(), "missing gateway contract")
    require(MAIN_HEAD.exists(), "missing mainnet head")
    require(MAIN_LEDGER.exists(), "missing mainnet ledger")

    for path in FORBIDDEN_ACTIVE_PATHS:
        require(not path.exists(), f"retired testnet path still exists: {path.relative_to(ROOT)}")
    for path in FORBIDDEN_SCRIPTS:
        require(not path.exists(), f"retired testnet script still exists: {path.relative_to(ROOT)}")

    policy = read_json(POLICY)
    agent = read_json(AGENT_START)
    gateway = read_json(GATEWAY)
    head = read_json(MAIN_HEAD)

    require(policy.get("chain_id") == "trinity-record-chain-main", "policy chain_id mismatch")
    require(policy.get("network_phase") == "prelaunch", "policy network_phase must be prelaunch")
    require(policy.get("prelaunch_test_records_allowed") is True, "prelaunch records must be allowed")
    require(policy.get("official_live_record_marker_required_before_live") is True, "activation marker must be required")
    require(policy.get("records_before_activation_marker_are_prelaunch_tests") is True, "pre-activation records must be tests")
    require(policy.get("mainnet_activation_marker_recorded") is False, "activation marker must not be recorded yet")
    require(policy.get("official_live_records_allowed") is False, "official live records must not be allowed yet")
    require(policy.get("formal_liu_hongju_guardian_application_still_deferred") is True, "formal guardian application must remain deferred")

    required = policy.get("prelaunch_record_required_fields", {})
    require(required.get("network_phase") == "prelaunch", "required network_phase mismatch")
    require(required.get("record_scope") == "mainnet_prelaunch_test", "required record_scope mismatch")
    require(required.get("prelaunch_test") is True, "required prelaunch_test must be true")
    require(required.get("official_live_record") is False, "required official_live_record must be false")
    require(required.get("does_not_create_guardian_status") is True, "required guardian status boundary missing")
    require(required.get("does_not_activate_system") is True, "required activation boundary missing")

    require(agent.get("public_phase", {}).get("network_phase") == "prelaunch", "agent-start must expose prelaunch")
    require(agent.get("policy_references", {}).get("mainnet_prelaunch_policy") == "/api/record-chain-mainnet-prelaunch-policy.v1.json", "agent-start missing prelaunch policy ref")
    require(agent.get("external_agent_rules", {}).get("must_not_clone_repository") is True, "agent-start must forbid clone")
    require(agent.get("external_agent_rules", {}).get("must_not_use_arweave_key") is True, "agent-start must forbid Arweave key")

    require(gateway.get("public_phase", {}).get("network_phase") == "prelaunch", "gateway must expose prelaunch")
    require(gateway.get("schema_references", {}).get("mainnet_prelaunch_policy") == "/api/record-chain-mainnet-prelaunch-policy.v1.json", "gateway missing prelaunch policy ref")
    require(gateway.get("public_submission_rule", {}).get("external_agents_must_not_clone_repository") is True, "gateway must forbid clone")
    require(gateway.get("public_submission_rule", {}).get("external_agents_must_not_use_arweave_key") is True, "gateway must forbid Arweave key")

    require(head.get("chain_id") == "trinity-record-chain-main", "main head must remain mainnet")
    require(head.get("ledger_file") == "record-chain/hash-chain/main.chain.jsonl", "main head ledger_file mismatch")

    print("PASS: mainnet prelaunch policy contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
