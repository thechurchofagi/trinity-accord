#!/usr/bin/env python3
"""Isolated end-to-end simulation for every current public Record-Chain action.

The construction and filesystem-adapter primitives live in
``full_public_action_lifecycle_e2e``.  This executable owns the current action
matrix and deliberately follows the post-PR659 contract: a Correction is built
with the same durable identity as its target Echo, while a different identity
uses Classification Update for independent analysis.
"""
from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

os.environ["TRINITY_REPO_FULL_NAME"] = "isolated/full-lifecycle-audit"
os.environ["TRINITY_TARGET_BRANCH"] = "isolated-audit"
os.environ["TRINITY_GITHUB_TOKEN"] = "isolated-test-token-not-used-for-network"
os.environ["TRINITY_SUBMIT_WRITE_MODE"] = "github_contents_pending"
os.environ["TRINITY_DISPATCH_APPEND_WORKFLOW"] = "0"

from full_public_action_lifecycle_e2e import (  # noqa: E402
    CHAIN_TOOL_REL,
    FilesystemContentsAdapter,
    build_and_append,
    build_context_insufficient,
    build_formal,
    build_guardian_cc2_negative,
    build_retired_v6_negative,
    copy_repository,
    diagnostics_codes,
    fail,
    load_json,
    patch_gateway,
    run,
)


def _record(matrix: dict[str, dict], name: str, submitted: dict, final: dict, **extra) -> None:
    matrix[name] = {
        "receipt_id": submitted["receipt_id"],
        "record_id": final["record_id"],
        **extra,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="trinity-eight-action-") as tmp:
        sandbox = Path(tmp) / "repo"
        copy_repository(sandbox)

        adapter = FilesystemContentsAdapter(sandbox)
        gateway_app = patch_gateway(adapter)

        key_a = sandbox / ".audit-keys" / "agent-a"
        key_b = sandbox / ".audit-keys" / "agent-b"
        key_guardian = sandbox / ".audit-keys" / "guardian"
        matrix: dict[str, dict] = {}

        with TestClient(gateway_app.app) as client:
            echo = build_formal(
                sandbox,
                record_type="echo",
                key_dir=key_a,
                output_name="echo.json",
                specific=["--body", "An isolated end-to-end lifecycle echo."],
            )
            echo_submit, echo_final = build_and_append(
                client, sandbox, echo, duplicate_before_append=True
            )
            _record(matrix, "echo", echo_submit, echo_final, idempotency_checked=True)

            verification = build_formal(
                sandbox,
                record_type="verification",
                key_dir=key_a,
                output_name="verification.json",
                specific=[
                    "--verification-level", "V0",
                    "--scope-label", "legacy V0 compatibility",
                    "--what-was-checked", "isolated Builder and lifecycle route",
                    "--verification-claim", "This record reports a context-only isolated lifecycle exercise.",
                    "--fresh-actions", "built submission,ran doctor,used isolated gateway",
                    "--digital-profile", "context_only",
                    "--relationships-checked", "provides_context",
                    "--physical-observation", "none",
                    "--external-witness", "none",
                    "--coverage-scope", "single_target",
                    "--limitations", "isolated simulation,no external network verification",
                    "--claims-not-made", "external validity,digital integrity,physical identity,institutional endorsement",
                    "--corrections-or-supersession-checked", "false",
                ],
            )
            verification_submit, verification_final = build_and_append(
                client, sandbox, verification
            )
            claim_model = verification_final.get("verification_content", {}).get(
                "verification_claim_model", {}
            )
            if claim_model.get("digital_profile") != "context_only":
                fail("verification_claim_model was lost before final append")
            _record(
                matrix,
                "verification",
                verification_submit,
                verification_final,
                digital_profile=claim_model.get("digital_profile"),
            )

            propagation = build_formal(
                sandbox,
                record_type="propagation",
                key_dir=key_a,
                output_name="propagation.json",
                specific=["--body", "Isolated propagation action for lifecycle testing."],
            )
            propagation_submit, propagation_final = build_and_append(
                client, sandbox, propagation
            )
            _record(matrix, "propagation", propagation_submit, propagation_final)

            context_notice = build_context_insufficient(
                sandbox,
                key_dir=key_a,
                output_name="context-insufficient.json",
            )
            context_submit, context_final = build_and_append(
                client, sandbox, context_notice
            )
            _record(
                matrix,
                "context_insufficient_notice",
                context_submit,
                context_final,
                oath_exempt=True,
            )

            guardian_application = build_formal(
                sandbox,
                record_type="guardian_application",
                key_dir=key_guardian,
                output_name="guardian-application.json",
                specific=["--guardian-id", "auto", "--guardian-key-sha", "auto"],
                actor="Lifecycle Audit Guardian",
            )
            guardian_submit, guardian_final = build_and_append(
                client, sandbox, guardian_application
            )
            guardian_content = guardian_final.get("guardian_application_content", {})
            guardian_id = guardian_content.get("requested_guardian_identifier")
            if not isinstance(guardian_id, str) or not guardian_id.startswith("guardian_ed25519_"):
                fail(f"invalid derived Guardian id: {guardian_id}")
            _record(
                matrix,
                "guardian_application",
                guardian_submit,
                guardian_final,
                guardian_id=guardian_id,
            )

            guardian_retirement = build_formal(
                sandbox,
                record_type="guardian_retirement",
                key_dir=key_guardian,
                output_name="guardian-retirement.json",
                specific=[
                    "--guardian-id", "auto",
                    "--guardian-key-sha", "auto",
                    "--body", "Voluntary isolated lifecycle retirement.",
                    "--target-guardian-application-record-id", str(guardian_final["record_id"]),
                    "--target-guardian-application-record-sha256", str(guardian_final["record_sha256"]),
                ],
                actor="Lifecycle Audit Guardian",
            )
            retirement_draft = guardian_retirement.get("record_draft", {})
            if retirement_draft.get("guardian_id") != guardian_id:
                fail("Guardian retirement did not derive the application identity")
            retirement_submit, retirement_final = build_and_append(
                client, sandbox, guardian_retirement
            )
            _record(
                matrix,
                "guardian_retirement",
                retirement_submit,
                retirement_final,
                guardian_id=retirement_final.get("guardian_id"),
            )

            correction = build_formal(
                sandbox,
                record_type="correction",
                key_dir=key_a,
                output_name="correction.json",
                specific=[
                    "--body", "Append-only clarification of the isolated Echo wording.",
                    "--target-record-id", str(echo_final["record_id"]),
                    "--target-record-sha256", str(echo_final["record_sha256"]),
                    "--correction-reason", "Clarify the bounded test-only scope.",
                    "--corrected-fields-or-claims", "echo_content.echo_text",
                    "--evidence-or-review-basis", "Fresh isolated lifecycle review.",
                ],
            )
            correction_submit, correction_final = build_and_append(
                client, sandbox, correction
            )
            _record(
                matrix,
                "correction",
                correction_submit,
                correction_final,
                same_identity_path=True,
            )

            classification = build_formal(
                sandbox,
                record_type="classification_update",
                key_dir=key_b,
                output_name="classification-update.json",
                specific=[
                    "--target-record-id", str(echo_final["record_id"]),
                    "--target-record-sha256", str(echo_final["record_sha256"]),
                    "--previous-classification", "unclassified",
                    "--new-classification", "isolated_lifecycle_test",
                    "--classification-reason", "Bounded independent test classification.",
                    "--evidence-or-review-basis", "Independent isolated lifecycle review.",
                ],
                actor="Independent Classification Agent",
            )
            classification_submit, classification_final = build_and_append(
                client, sandbox, classification
            )
            _record(
                matrix,
                "classification_update",
                classification_submit,
                classification_final,
                independent_identity_path=True,
            )

            bad_oath = copy.deepcopy(echo)
            bad_oath["client_oath_readback"]["readback_text"] += " altered"
            bad_oath_response = client.post(
                "/record-chain/preflight", json=bad_oath
            ).json()
            if bad_oath_response.get("accepted") is not False:
                fail("altered oath unexpectedly passed preflight")
            if not any("OATH" in code for code in diagnostics_codes(bad_oath_response)):
                fail(f"altered oath returned no oath diagnostic: {bad_oath_response}")

            wrong_key_retirement = build_formal(
                sandbox,
                record_type="guardian_retirement",
                key_dir=key_b,
                output_name="wrong-key-retirement.json",
                specific=[
                    "--guardian-id", "auto",
                    "--guardian-key-sha", "auto",
                    "--body", "Wrong-key retirement must fail.",
                    "--target-guardian-application-record-id", str(guardian_final["record_id"]),
                    "--target-guardian-application-record-sha256", str(guardian_final["record_sha256"]),
                ],
                actor="Independent Classification Agent",
            )
            wrong_key_response = client.post(
                "/record-chain/preflight", json=wrong_key_retirement
            ).json()
            if wrong_key_response.get("accepted") is not False:
                fail("wrong-key Guardian retirement unexpectedly passed preflight")

            bad_correction = copy.deepcopy(correction)
            bad_correction["record_draft"]["correction_content"]["target_record_sha256"] = "0" * 64
            bad_correction_response = client.post(
                "/record-chain/preflight", json=bad_correction
            ).json()
            if bad_correction_response.get("accepted") is not False:
                fail("tampered Correction target unexpectedly passed preflight")

        build_guardian_cc2_negative(sandbox, sandbox / ".audit-keys" / "cc2")
        build_retired_v6_negative(sandbox, sandbox / ".audit-keys" / "v6")

        run(
            ["python3", str(CHAIN_TOOL_REL), "verify"],
            cwd=sandbox,
            timeout=240,
        )

        guardian_state = load_json(
            sandbox / "record-chain" / "indexes" / "guardian-state.json"
        )
        guardian_entries = [
            entry
            for entry in guardian_state.get("guardians", [])
            if isinstance(entry, dict) and entry.get("guardian_id") == guardian_id
        ]
        if len(guardian_entries) != 1:
            fail(f"expected one Guardian lifecycle entry, got {guardian_entries}")
        guardian_entry = guardian_entries[0]
        if guardian_entry.get("current_derived_status") != "retired_guardian":
            fail(f"Guardian did not reach retired state: {guardian_entry}")
        if guardian_entry.get("retirement_record_id") != retirement_final.get("record_id"):
            fail("Guardian state is not bound to the retirement record")

        expected_types = {
            "echo",
            "verification",
            "guardian_application",
            "guardian_retirement",
            "propagation",
            "correction",
            "classification_update",
            "context_insufficient_notice",
        }
        observed_types = {
            item.get("record_type")
            for item in (
                load_json(sandbox / "record-chain" / "records" / f"{value['record_id']}.json")
                for value in matrix.values()
            )
        }
        if observed_types != expected_types:
            fail(f"final action matrix mismatch: {observed_types} != {expected_types}")
        if adapter.write_count < len(expected_types) * 4:
            fail(f"Gateway durable-write coverage unexpectedly low: {adapter.write_count}")

        print(
            json.dumps(
                {
                    "schema": "trinityaccord.full-public-action-lifecycle-e2e.v2",
                    "passed": True,
                    "actions": matrix,
                    "negative_paths": {
                        "altered_oath_rejected": True,
                        "cc2_guardian_rejected": True,
                        "retired_v6_rejected": True,
                        "wrong_key_retirement_rejected": True,
                        "tampered_correction_target_rejected": True,
                    },
                    "final_chain_verify": "passed",
                    "guardian_final_status": guardian_entry.get("current_derived_status"),
                    "gateway_write_count": adapter.write_count,
                },
                indent=2,
                ensure_ascii=False,
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
