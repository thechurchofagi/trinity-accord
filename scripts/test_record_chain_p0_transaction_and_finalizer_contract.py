#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    p = ROOT / path
    require(p.exists(), f"missing {path}")
    return p.read_text(encoding="utf-8")


def main() -> None:
    app = read("apps/record_chain_intake_gateway/app.py")
    workflow = read(".github/workflows/record-chain-append.yml")
    authorship = read("apps/record_chain_intake_gateway/gateway/authorship.py")
    chain = read("scripts/trinity_record_chain.py")
    finalizer = read("scripts/finalize_mainnet_prelaunch_record_from_submission.py")

    for label, text in [
        ("app.py", app),
        ("trinity_record_chain.py", chain),
        ("finalize_mainnet_prelaunch_record_from_submission.py", finalizer),
    ]:
        try:
            ast.parse(text)
        except SyntaxError as exc:
            fail(f"{label} has syntax error: {exc}")

    # P0-A: append workflow must not trigger directly on pending push.
    require(
        "record-chain/pending/**" not in workflow,
        "record-chain-append.yml must not trigger on record-chain/pending/** push",
    )

    # P0-A: Gateway must write idempotency index before pending.
    idx_idemp = app.find('f"intake: idempotency index')
    idx_pending = app.find('f"intake: pending')
    require(idx_idemp != -1, "app.py missing idempotency index write")
    require(idx_pending != -1, "app.py missing pending write")
    require(idx_idemp < idx_pending, "Gateway must write idempotency index before pending")
    require("pending LAST" in app, "app.py must document pending as LAST append-eligibility marker")

    # P0-A: append must require durable binding before authorship verification.
    idx_binding = chain.find("require_gateway_pending_durable_intake_binding(path)")
    idx_verify = chain.find("verify_pending_record_authorship(signed_scope_draft)")
    require(idx_binding != -1, "trinity_record_chain.py must call require_gateway_pending_durable_intake_binding(path)")
    require(idx_verify != -1, "trinity_record_chain.py must verify pending authorship")
    require(idx_binding < idx_verify, "durable intake binding must be checked before authorship verification/append")
    for needle in [
        "_GATEWAY_PENDING_RE",
        "by-submission-sha256",
        "idempotency index pending_file_path mismatch",
    ]:
        require(needle in chain, f"trinity_record_chain.py missing durable binding contract text: {needle}")

    # P0-B: server_append_metadata must be unsigned for authorship verification.
    require('"server_append_metadata"' in authorship, "authorship.UNSIGNED_PROJECTION_FIELDS must include server_append_metadata")

    # P0-B: append must extract metadata before stripping and merge after verification.
    require("def extract_server_append_metadata" in chain, "trinity_record_chain.py missing extract_server_append_metadata")
    idx_extract = chain.find("server_append_metadata = extract_server_append_metadata(raw_draft)")
    idx_sanitize = chain.find("signed_scope_draft = sanitize_pending_record_for_append(raw_draft)")
    idx_merge = chain.find('draft["server_normalization"]["server_append_metadata"] = server_append_metadata')
    require(idx_extract != -1, "append must extract server_append_metadata from raw_draft")
    require(idx_sanitize != -1, "append must sanitize pending record before verification")
    require(idx_merge != -1, "append must merge server_append_metadata into final server_normalization")
    require(idx_extract < idx_sanitize < idx_merge, "server_append_metadata must be extracted before sanitize and merged after verification")

    # P0-B: finalizer must not write finalizer metadata directly onto signed draft.
    forbidden_direct_assignments = [
        'draft["network_phase"]',
        'draft["record_scope"]',
        'draft["live_test"]',
        'draft["operational_test"]',
        'draft["test_record"]',
        'draft["prelaunch_test"]',
        'draft["official_live_record"]',
        'draft["does_not_create_guardian_status"]',
        'draft["does_not_activate_system"]',
        'draft["source_receipt_semantics"]',
        'draft["receipt_id"]',
        'draft["source_artifacts"]',
        'draft["source_run_id"]',
        'draft["source_summary"]',
        'draft["finalization"]',
    ]
    for needle in forbidden_direct_assignments:
        require(needle not in finalizer, f"finalizer must not directly mutate signed draft with {needle}")

    require('draft["server_append_metadata"]' in finalizer, "finalizer must attach server_append_metadata to pending draft")
    require('"trinityaccord.server-append-metadata.v1"' in finalizer, "finalizer metadata must declare schema")
    require(
        'server_append_metadata.get("network_phase")' in finalizer,
        "finalizer post-append assertions must read metadata from server_append_metadata",
    )
    require(
        'native_record.get("network_phase")' not in finalizer,
        "finalizer must not expect network_phase at final record top level",
    )

    print("PASS: P0 transaction/finalizer contract is enforced.")


if __name__ == "__main__":
    main()
