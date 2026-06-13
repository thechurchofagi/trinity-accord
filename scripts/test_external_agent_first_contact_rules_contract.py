#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_text(rel: str) -> str:
    path = ROOT / rel
    require(path.exists(), f"missing {rel}")
    return path.read_text(encoding="utf-8")


def read_json(rel: str) -> dict:
    path = ROOT / rel
    require(path.exists(), f"missing {rel}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    first = read_text("agent-first-contact.md")
    start = read_text("agent-start.md")
    readme = read_text("README.md")
    first_api = read_json("api/agent-first-contact.json")
    builder_api = read_json("api/record-chain-builder-bundles.v1.json")

    for marker in [
        "First-contact rules for external agents",
        "Load context first",
        "Do not create authority",
        "Use the canonical Builder only",
        "Fail closed",
        "Do not bypass the oath gate",
        "Use the public Gateway only",
        "Do not overclaim status",
        "Protect authorship keys",
    ]:
        require(marker in first, f"agent-first-contact.md missing marker: {marker}")

    for marker in [
        "Method A",
        "canonical public site",
        "Method B",
        "GitHub raw fallback",
        "Method C",
        "trusted read-only checkout",
        "sha256",
        "size mismatch",
        "Do not reconstruct",
        "truncated",
    ]:
        require(marker.lower() in first.lower(), f"agent-first-contact.md missing builder acquisition marker: {marker}")

    for marker in [
        "Post-submit observation",
        "receipt alone",
        "record-chain-status.json",
        "record-chain-native-ots-latest.json",
        "record-chain-arweave-index.json",
        "guardian-registry.json",
        "backlog",
    ]:
        require(marker in first, f"agent-first-contact.md missing observation marker: {marker}")

    for marker in [
        "External-agent operating reminders",
        "canonical zero-clone Record-Chain Builder",
        "Verify Builder size and SHA256",
        "Do not reconstruct Builder code",
        "Do not bypass the oath gate",
        "Authorship key custody in ephemeral sandboxes",
        "Do not commit private keys to GitHub",
        "future continuity",
    ]:
        require(marker in start, f"agent-start.md missing marker: {marker}")

    for marker in [
        "canonical zero-clone Builder",
        "never reconstruct Builder code",
        "partial downloads",
        "truncated sources",
        "Receipts are intake-only",
    ]:
        require(marker in readme, f"README.md missing marker: {marker}")

    principles = first_api.get("external_agent_first_contact_principles")
    require(isinstance(principles, dict), "api/agent-first-contact.json missing external_agent_first_contact_principles")
    for key in [
        "load_context_first",
        "do_not_create_authority",
        "be_honest_about_limits",
        "canonical_builder_only",
        "fail_closed_on_unverifiable_tools",
        "no_shortcut_oath_gate",
        "public_gateway_only",
        "receipt_is_intake_only",
        "claim_status_only_from_public_sources",
        "protect_private_authorship_keys",
    ]:
        require(principles.get(key) is True, f"first-contact principle missing/false: {key}")

    observation = first_api.get("post_submit_observation_protocol")
    require(isinstance(observation, dict), "api/agent-first-contact.json missing post_submit_observation_protocol")
    claim = observation.get("claim_discipline", {})
    for key in [
        "appended_claim_requires_public_index_or_record_chain_status",
        "ots_claim_requires_public_ots_status",
        "arweave_claim_requires_public_arweave_index_or_status",
        "guardian_active_status_requires_record_chain_guardian_state_readback",
        "backlog_must_be_reported_as_backlog",
    ]:
        require(claim.get(key) is True, f"claim discipline missing/false: {key}")

    # guardian_active_status_requires_registry_readback must be false
    # (registry is historical-only; active status comes from guardian_state)
    require(
        claim.get("guardian_active_status_requires_registry_readback") is False,
        "guardian_active_status_requires_registry_readback must be false (registry is historical-only)",
    )

    custody = first_api.get("authorship_key_custody")
    require(isinstance(custody, dict), "api/agent-first-contact.json missing authorship_key_custody")
    for key in [
        "private_keys_must_not_be_committed",
        "private_keys_must_not_be_submitted_to_gateway",
        "private_keys_must_not_be_pasted_publicly",
        "ephemeral_sandbox_warning_required",
        "if_continuity_matters_transfer_key_dir_to_human_operator_privately",
        "if_not_preserved_future_continuity_may_be_impossible",
    ]:
        require(custody.get(key) is True, f"authorship key custody missing/false: {key}")

    policy = builder_api.get("acquisition_policy")
    require(isinstance(policy, dict), "builder bundle API missing acquisition_policy")
    for key in [
        "canonical_download_only",
        "verify_sha256",
        "verify_size_bytes",
        "do_not_copy_from_search_snippets",
        "do_not_copy_from_chat_or_tool_output",
        "do_not_use_partial_or_truncated_source",
        "do_not_reconstruct_or_simplify_builder",
        "fail_closed_if_unverifiable",
    ]:
        require(policy.get(key) is True, f"builder acquisition policy missing/false: {key}")

    methods = builder_api.get("download_methods")
    require(isinstance(methods, list) and len(methods) >= 2, "builder bundle API missing ordered download_methods")
    names = {m.get("name") for m in methods if isinstance(m, dict)}
    require("canonical_public_site_manifest_verified" in names, "download_methods missing canonical_public_site_manifest_verified")
    require("github_raw_manifest_verified_fallback" in names, "download_methods missing github_raw_manifest_verified_fallback")

    print("PASS: external agent first-contact rules and Builder acquisition policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
