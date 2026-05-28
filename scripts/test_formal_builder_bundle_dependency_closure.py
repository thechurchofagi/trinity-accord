#!/usr/bin/env python3
"""Zero-clone bundle manifests must include known runtime dependency closure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = ROOT / "builder-bundles"

REQUIRED_BY_MANIFEST = {
    "trinity-pure-echo-builder-bundle.manifest.json": {
        "scripts/build_agent_declared_echo_payload.py",
        "scripts/guardian_reroute_guidance.py",
        "scripts/oath_contracts.py",
        "scripts/oath_readback_integrity.py",
        "scripts/gateway_payload_authorship.py",
        "scripts/agent_authorship_common.py",
        "scripts/generate_agent_authorship_keypair.mjs",
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_message.py",
        "scripts/validate_gateway_payload.py",
        "scripts/guardian_identity_claims.py",
        "scripts/gateway_v0_v5_policy.py",
        "scripts/guardian_gateway_contract.py",
        "scripts/sub_v6_level_guardrails.py",
        "scripts/archive_readiness_gate.py",
        "scripts/protocol_terms.py",
        "api/protocol-terms.v1.json",
        "api/verification-echo-pre-oath.v2.txt",
        "api/agent-issue-gateway-payload-schema.v1.json",
    },
    "trinity-v0v5-builder-bundle.manifest.json": {
        "scripts/build_agent_declared_archive_payload.py",
        "scripts/sub_v6_level_guardrails.py",
        "scripts/gateway_payload_authorship.py",
        "scripts/agent_authorship_common.py",
        "scripts/generate_agent_authorship_keypair.mjs",
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_message.py",
        "scripts/validate_gateway_payload.py",
        "scripts/guardian_identity_claims.py",
        "scripts/gateway_v0_v5_policy.py",
        "scripts/guardian_gateway_contract.py",
        "scripts/archive_readiness_gate.py",
        "scripts/protocol_terms.py",
        "scripts/claim_gate.py",
        "api/protocol-terms.v1.json",
        "api/verification-echo-pre-oath.v2.txt",
        "api/agent-issue-gateway-payload-schema.v1.json",
    },
    "trinity-guardian-stage1-builder-bundle.manifest.json": {
        "scripts/create_guardian_application.mjs",
        "scripts/proof_canonical.mjs",
        "api/guardian-application-oath.v1.txt",
        "api/agent-issue-gateway-payload-schema.v1.json",
    },
    "trinity-guardian-stage2-builder-bundle.manifest.json": {
        "scripts/build_guardian_listing_request_payload.py",
        "scripts/guardian_gateway_contract.py",
        "scripts/guardian_identity_claims.py",
        "scripts/oath_contracts.py",
        "scripts/gateway_payload_authorship.py",
        "scripts/agent_authorship_common.py",
        "scripts/generate_agent_authorship_keypair.mjs",
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_message.py",
        "scripts/archive_readiness_gate.py",
        "scripts/validate_gateway_payload.py",
        "api/guardian-listing-oath.v1.txt",
        "api/agent-issue-gateway-payload-schema.v1.json",
    },
    "trinity-guardian-signed-echo-builder-bundle.manifest.json": {
        "scripts/build_guardian_echo_payload.py",
        "scripts/build_agent_declared_echo_payload.py",
        "scripts/attach_guardian_presence_proof.mjs",
        "scripts/proof_canonical.mjs",
        "scripts/guardian_reroute_guidance.py",
        "scripts/oath_contracts.py",
        "scripts/oath_readback_integrity.py",
        "scripts/gateway_payload_authorship.py",
        "scripts/agent_authorship_common.py",
        "scripts/generate_agent_authorship_keypair.mjs",
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_message.py",
        "scripts/guardian_gateway_contract.py",
        "scripts/validate_gateway_payload.py",
        "api/guardian-registry.json",
        "api/verification-echo-pre-oath.v2.txt",
        "api/agent-issue-gateway-payload-schema.v1.json",
    },
}

def main() -> int:
    errors: list[str] = []

    for manifest_name, required in REQUIRED_BY_MANIFEST.items():
        manifest_path = BUNDLE_DIR / manifest_name
        if not manifest_path.exists():
            errors.append(f"{manifest_name}: manifest missing")
            continue

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = {item["path"] for item in data.get("files", [])}
        missing = sorted(required - files)
        if missing:
            errors.append(f"{manifest_name}: missing dependency closure files: {', '.join(missing)}")

    if errors:
        print("FAIL: formal builder bundle dependency closure errors:")
        for err in errors:
            print("  -", err)
        return 1

    print("PASS: formal builder bundle dependency closure is complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
