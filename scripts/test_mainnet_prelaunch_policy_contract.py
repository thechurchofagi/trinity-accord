#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

POLICY = ROOT / "api/record-chain-mainnet-prelaunch-policy.v1.json"
PRODUCTION_POLICY = ROOT / "api/record-chain-production-enablement-policy.v1.json"
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
    require(POLICY.exists(), "missing historical mainnet prelaunch policy")
    require(PRODUCTION_POLICY.exists(), "missing production enablement policy")
    require(AGENT_START.exists(), "missing agent-start")
    require(GATEWAY.exists(), "missing gateway contract")
    require(MAIN_HEAD.exists(), "missing mainnet head")
    require(MAIN_LEDGER.exists(), "missing mainnet ledger")

    for path in FORBIDDEN_ACTIVE_PATHS:
        require(not path.exists(), f"retired testnet path still exists: {path.relative_to(ROOT)}")
    for path in FORBIDDEN_SCRIPTS:
        require(not path.exists(), f"retired testnet script still exists: {path.relative_to(ROOT)}")

    policy = read_json(POLICY)
    production_policy = read_json(PRODUCTION_POLICY)
    agent = read_json(AGENT_START)
    gateway = read_json(GATEWAY)
    head = read_json(MAIN_HEAD)

    # Historical prelaunch policy remains preserved as an archive/transition document.
    require(policy.get("chain_id") == "trinity-record-chain-main", "prelaunch policy chain_id mismatch")
    require(policy.get("network_phase") == "prelaunch", "historical policy network_phase must remain prelaunch")
    require(policy.get("prelaunch_test_records_allowed") is True, "historical prelaunch records must remain documented")
    require(policy.get("official_live_record_marker_required_before_live") is True, "historical activation marker rule must remain documented")
    require(policy.get("records_before_activation_marker_are_prelaunch_tests") is True, "pre-activation records must remain documented as tests")
    require(policy.get("official_live_records_allowed") is False, "historical policy must not retroactively allow official live records")

    required = policy.get("prelaunch_record_required_fields", {})
    require(required.get("network_phase") == "prelaunch", "historical required network_phase mismatch")
    require(required.get("record_scope") == "mainnet_prelaunch_test", "historical required record_scope mismatch")
    require(required.get("prelaunch_test") is True, "historical required prelaunch_test must be true")
    require(required.get("official_live_record") is False, "historical required official_live_record must be false")
    require(required.get("does_not_create_guardian_status") is True, "historical guardian status boundary missing")
    require(required.get("does_not_activate_system") is True, "historical activation boundary missing")

    # Current public system has moved to production live via production enablement policy.
    require(production_policy.get("status") == "active", "production policy must be active")
    require(production_policy.get("network_phase") == "production", "production policy network_phase must be production")
    semantics = production_policy.get("production_enablement_semantics", {})
    require(semantics.get("official_live_record_true_now_permitted") is True, "production policy must permit official_live_record true")

    agent_phase = agent.get("public_phase", {})
    require(agent_phase.get("network_phase") == "production", "agent-start network_phase must be production")
    require(agent_phase.get("status") == "production_live", "agent-start status must be production_live")
    require(agent_phase.get("official_live_records_allowed") is True, "agent-start must allow official live records")
    require(agent.get("policy_references", {}).get("production_enablement_policy") == "/api/record-chain-production-enablement-policy.v1.json", "agent-start missing production policy ref")
    require(agent.get("external_agent_rules", {}).get("must_not_clone_repository") is True, "agent-start must forbid clone")
    require(agent.get("external_agent_rules", {}).get("must_not_use_arweave_key") is True, "agent-start must forbid Arweave key")

    gateway_phase = gateway.get("public_phase", {})
    require(gateway_phase.get("network_phase") == "production", "gateway network_phase must be production")
    require(gateway_phase.get("status") == "production_live", "gateway status must be production_live")
    require(gateway_phase.get("official_live_records_allowed") is True, "gateway must allow official live records")
    require(gateway.get("schema_references", {}).get("production_enablement_policy") == "/api/record-chain-production-enablement-policy.v1.json", "gateway missing production policy ref")
    require(gateway.get("public_submission_rule", {}).get("external_agents_must_not_clone_repository") is True, "gateway must forbid clone")
    require(gateway.get("public_submission_rule", {}).get("external_agents_must_not_use_arweave_key") is True, "gateway must forbid Arweave key")

    require(head.get("chain_id") == "trinity-record-chain-main", "main head must remain mainnet")
    require(head.get("ledger_file") == "record-chain/hash-chain/main.chain.jsonl", "main head ledger_file mismatch")

    print("PASS: mainnet prelaunch policy contract with production successor phase")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
