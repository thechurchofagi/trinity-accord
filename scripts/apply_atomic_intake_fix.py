#!/usr/bin/env python3
"""Apply the atomic Record-Chain intake migration to the current branch.

This script is intentionally temporary: it lets CI apply one deterministic,
reviewable transformation to the large Gateway application, after which the
script is removed from the final pull request.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def patch_app() -> None:
    path = ROOT / "apps/record_chain_intake_gateway/app.py"
    text = path.read_text(encoding="utf-8")

    old_import = (
        "from apps.record_chain_intake_gateway.gateway.github_adapter import "
        "delete_file, dispatch_workflow, get_file_sha, get_file_text, put_file"
    )
    new_import = (
        "from apps.record_chain_intake_gateway.gateway.github_atomic import "
        "AtomicCreateConflict, create_files_atomic\n"
        "from apps.record_chain_intake_gateway.gateway.github_adapter import "
        "dispatch_workflow, get_file_sha, get_file_text"
    )
    text = replace_once(text, old_import, new_import, "Gateway imports")

    helper_start = text.index("async def put_file_confirmed(")
    helper_end_marker = (
        "# ---------------------------------------------------------------------------\n"
        "# BLOCKER 1 helpers: Idempotency index fail-closed"
    )
    helper_end = text.index(helper_end_marker, helper_start)
    text = text[:helper_start] + text[helper_end:]

    transaction_anchor = text.index("    # --- persist to GitHub ---")
    transaction_start = text.index(
        '    if _WRITE_MODE == "github_contents_pending":',
        transaction_anchor,
    )
    transaction_end = text.index(
        "    # --- store receipt in memory",
        transaction_start,
    )

    atomic_transaction = '''    if _WRITE_MODE == "github_contents_pending":
        # Read-only duplicate/legacy checks are safe before the atomic commit.
        # No intake artifact is exposed by these checks.
        try:
            existing_match = await _find_existing_matching_receipt(
                candidate_receipt_paths=[receipt_path, legacy_receipt_path],
                submission_sha256=submission_sha256,
                stored_submission_sha256=stored_submission_sha256,
            )
            if existing_match is not None:
                existing_receipt_path, existing_receipt = existing_match
                return SubmitResponse(
                    accepted=True,
                    submitted=True,
                    receipt_id=existing_receipt.get("server_receipt_id") or existing_receipt.get("receipt_id") or receipt_id,
                    record_type=record_type,
                    submission_sha256=submission_sha256,
                    received_raw_body_sha256=received_raw_body_sha256,
                    pending_file_path=existing_receipt.get("pending_file_path", pending_file_path),
                    intake_submission_path=existing_receipt.get("intake_submission_path", intake_submission_path),
                    receipt_path=existing_receipt.get("receipt_path", existing_receipt_path),
                    server_created_at=existing_receipt.get("accepted_at", ""),
                    append_status="duplicate_existing_receipt_returned",
                    receipt_commit_sha=None,
                    receipt=existing_receipt,
                    diagnostics=[],
                    warnings=["Duplicate submission: existing immutable receipt returned; no files were updated."],
                    boundary=_build_submit_boundary(body),
                    created_pending_records=[
                        value
                        for value in [existing_receipt.get("pending_file_path", "")]
                        if isinstance(value, str) and value
                    ],
                )

            legacy_sub_sha = await get_file_sha(legacy_intake_submission_path)
            legacy_pending_sha = await get_file_sha(legacy_pending_file_path)
            if legacy_sub_sha is not None or legacy_pending_sha is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "LEGACY_INTAKE_ARTIFACT_PATH_CONFLICT",
                        "message": "Legacy 12-hex submission or pending path exists without a matching immutable receipt. Refusing to create duplicate 24-hex artifact.",
                        "legacy_submission_path_exists": legacy_sub_sha is not None,
                        "legacy_pending_path_exists": legacy_pending_sha is not None,
                        "legacy_submission_path": legacy_intake_submission_path,
                        "legacy_pending_file_path": legacy_pending_file_path,
                    },
                )
        except HTTPException:
            raise
        except Exception as lookup_exc:
            logger.error("Pre-commit duplicate check failed for %s: %s", receipt_id, lookup_exc)
            return SubmitResponse(
                accepted=False,
                submitted=False,
                record_type=record_type,
                submission_sha256=original_submission_sha256,
                received_raw_body_sha256=received_raw_body_sha256,
                diagnostics=[Diagnostic(
                    code="INTAKE_PRECOMMIT_LOOKUP_FAILED",
                    severity="error",
                    field="record-chain/intake",
                    message=f"Pre-commit duplicate-state lookup failed: {lookup_exc}",
                    meaning="The Gateway failed closed before creating any intake artifact.",
                    suggested_fix="Retry the exact same submission later.",
                    retry_allowed=True,
                )],
                boundary=_build_submit_boundary(body),
            )

        # Submission, receipt, finalized idempotency index, and pending marker
        # become visible in one branch-ref update. The strict verifier can no
        # longer observe an idempotency index before its pending transaction is
        # fully materialized.
        idempotency_path = _idempotency_index_path(original_submission_sha256)
        pending_committed_at = now.isoformat().replace("+00:00", "Z")
        idempotency_index_data = _build_idempotency_index_data(
            submission_sha256=original_submission_sha256,
            stored_submission_sha256=stored_submission_sha256,
            receipt_id=receipt_id,
            receipt_path=receipt_path,
            pending_file_path=pending_file_path,
            intake_submission_path=intake_submission_path,
            record_type=record_type,
            now=now,
            pending_written=True,
            pending_committed_at=pending_committed_at,
        )
        atomic_files = {
            intake_submission_path: submission_content,
            receipt_path: receipt_content,
            idempotency_path: canonical_dumps(idempotency_index_data),
            pending_file_path: pending_content,
        }

        try:
            atomic_result = await create_files_atomic(
                atomic_files,
                f"intake: materialize {receipt_id} ({record_type})",
            )
            commit_sha = atomic_result.get("commit", {}).get("sha")
            logger.info("Atomically materialized intake transaction %s", receipt_id)
        except AtomicCreateConflict as exc:
            logger.warning("Atomic intake conflict for %s: %s", receipt_id, exc)
            existing_index = await _read_idempotency_index(original_submission_sha256)
            if existing_index is not None:
                try:
                    return await _submit_response_from_idempotency_index(
                        index=existing_index,
                        record_type=record_type,
                        submission_sha256=original_submission_sha256,
                        received_raw_body_sha256=received_raw_body_sha256,
                        body=body,
                    )
                except HTTPException:
                    raise
                except Exception as response_exc:
                    logger.error(
                        "Concurrent atomic intake could not be resolved for %s: %s",
                        original_submission_sha256[:16],
                        response_exc,
                    )
            return SubmitResponse(
                accepted=False,
                submitted=False,
                record_type=record_type,
                submission_sha256=original_submission_sha256,
                received_raw_body_sha256=received_raw_body_sha256,
                diagnostics=[Diagnostic(
                    code="INTAKE_ATOMIC_PATH_CONFLICT",
                    severity="error",
                    field="record-chain/intake",
                    message=f"Atomic intake paths conflict with existing repository state: {exc}",
                    meaning="The Gateway refused to expose or overwrite a partial intake transaction.",
                    suggested_fix="Retry the exact same submission later or ask an operator to inspect the durable intake paths.",
                    retry_allowed=True,
                )],
                boundary=_build_submit_boundary(body),
            )
        except Exception as exc:
            logger.error("Atomic persistence failed for %s: %s", receipt_id, exc)
            return SubmitResponse(
                accepted=False,
                submitted=False,
                record_type=record_type,
                submission_sha256=original_submission_sha256,
                received_raw_body_sha256=received_raw_body_sha256,
                diagnostics=[Diagnostic(
                    code="PERSIST_FAILED",
                    severity="error",
                    message=f"Atomic persist failed: {exc}",
                    meaning="No intake artifact is accepted unless submission, receipt, finalized idempotency index, and pending marker become visible together.",
                    suggested_fix="Retry the exact same submission later.",
                    retry_allowed=True,
                )],
                boundary=_build_submit_boundary(body),
            )

        if _DISPATCH_APPEND_WORKFLOW:
            try:
                await dispatch_workflow(
                    _APPEND_WORKFLOW,
                    inputs={
                        "receipt_id": receipt_id,
                        "pending_file_path": pending_file_path,
                    },
                )
                append_status = "queued"
                logger.info("Dispatched append workflow %s for %s", _APPEND_WORKFLOW, receipt_id)
            except Exception as dispatch_exc:
                append_status = "pending_dispatch_failed"
                warning = (
                    f"Append workflow dispatch failed after durable atomic intake: {dispatch_exc}. "
                    "The record remains pending and can be picked up by push/scheduled/manual append."
                )
                warnings.append(warning)
                logger.warning("Append dispatch failed for %s: %s", receipt_id, dispatch_exc)
    else:
        logger.info("Dry-run mode — skipping persist for %s", receipt_id)
        append_status = "dry_run"

'''
    text = text[:transaction_start] + atomic_transaction + text[transaction_end:]
    compile(text, str(path), "exec")
    path.write_text(text, encoding="utf-8")


def patch_readback_policy() -> None:
    path = ROOT / "scripts/test_readback_hash_policy.py"
    text = path.read_text(encoding="utf-8")
    old = '''    for relative in ["index.md", "agent-start.md", "llms.txt", "external-agent-quickstart.md"]:
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        require("handwrite" in text and ("submission" in text or "payload" in text),
                f"{relative} must warn against handwritten submissions")
        require("agent_readback_sha256" not in text, f"{relative} contains retired agent_readback_sha256")
'''
    new = '''    for relative in ["agent-start.md", "llms.txt", "external-agent-quickstart.md"]:
        text = (ROOT / relative).read_text(encoding="utf-8").lower()
        require("handwrite" in text and ("submission" in text or "payload" in text),
                f"{relative} must warn against handwritten submissions")
        require("agent_readback_sha256" not in text, f"{relative} contains retired agent_readback_sha256")

    homepage = (ROOT / "index.md").read_text(encoding="utf-8").lower()
    require("homepage-only context remains" in homepage and "payload construction" in homepage,
            "index.md must fail closed for homepage-only payload construction")
    require("/agent-first-contact/" in homepage,
            "index.md must route operating agents to Agent First Contact")
    require("agent_readback_sha256" not in homepage,
            "index.md contains retired agent_readback_sha256")
'''
    text = replace_once(text, old, new, "readback policy")
    compile(text, str(path), "exec")
    path.write_text(text, encoding="utf-8")


def patch_deep_audit_contract() -> None:
    path = ROOT / "apps/record_chain_intake_gateway/tests/test_deep_audit_round2.py"
    text = path.read_text(encoding="utf-8")
    old = '''    app_source = (ROOT / "apps/record_chain_intake_gateway/app.py").read_text(encoding="utf-8")
    assert "put_file_confirmed" in app_source
    assert "pending_written (non-fatal)" not in app_source
'''
    new = '''    app_source = (ROOT / "apps/record_chain_intake_gateway/app.py").read_text(encoding="utf-8")
    atomic_source = (ROOT / "apps/record_chain_intake_gateway/gateway/github_atomic.py").read_text(encoding="utf-8")
    assert "create_files_atomic" in app_source
    assert "pending_written=True" in app_source
    assert "intake: materialize" in app_source
    assert "Write 1: intake submission" not in app_source
    assert "/git/trees" in atomic_source
    assert "/git/commits" in atomic_source
    assert '"force": False' in atomic_source
    assert "pending_written (non-fatal)" not in app_source
'''
    text = replace_once(text, old, new, "deep-audit source contract")
    compile(text, str(path), "exec")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    patch_app()
    patch_readback_policy()
    patch_deep_audit_contract()
    print("ATOMIC_INTAKE_FIX_APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
