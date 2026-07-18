#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement target, found {count}")
    write(path, text.replace(old, new, 1))


APP = "apps/record_chain_intake_gateway/app.py"
ATOMIC = "apps/record_chain_intake_gateway/gateway/github_atomic.py"
MODELS = "apps/record_chain_intake_gateway/gateway/models.py"
RECEIPT_TEST = "apps/record_chain_intake_gateway/tests/test_receipt.py"

# 1. Strictly parse repository artifacts and reject non-object JSON.
replace_once(
    APP,
    '''async def _load_json_text_or_none(path_text: str) -> dict[str, Any] | None:
    text = await get_file_text(path_text)
    if text is None:
        return None
    return json.loads(text)
''',
    '''async def _load_json_text_or_none(path_text: str) -> dict[str, Any] | None:
    text = await get_file_text(path_text)
    if text is None:
        return None
    data = parse_json_strict(text)
    if not isinstance(data, dict):
        raise RuntimeError(f"Repository JSON artifact is not an object: {path_text}")
    return data
''',
)
replace_once(
    APP,
    '''    data = json.loads(text)
    if data.get("submission_sha256") != submission_sha256:
''',
    '''    data = parse_json_strict(text)
    if not isinstance(data, dict):
        raise RuntimeError(f"Idempotency index is not a JSON object at {path}")
    if data.get("submission_sha256") != submission_sha256:
''',
)
replace_once(APP, "    receipt_data_raw = json.loads(receipt_text)\n", "    receipt_data_raw = parse_json_strict(receipt_text)\n")

# 2. Same-day/legacy receipt fallback must verify the immutable receipt and all path bindings.
replace_once(
    APP,
    '''def _existing_receipt_matches_current(
    *,
    existing_receipt: dict[str, Any],
    submission_sha256: str,
    stored_submission_sha256: str,
    receipt_path: str,
) -> bool:
    return (
        existing_receipt.get("submission_sha256") == submission_sha256
        and existing_receipt.get("stored_submission_sha256") == stored_submission_sha256
        and existing_receipt.get("receipt_path") == receipt_path
        and isinstance(existing_receipt.get("intake_submission_path"), str)
    )
''',
    '''def _existing_receipt_matches_current(
    *,
    existing_receipt: dict[str, Any],
    submission_sha256: str,
    stored_submission_sha256: str,
    receipt_path: str,
) -> bool:
    receipt_ok, _ = verify_receipt_sha256(existing_receipt)
    filename = receipt_path.rsplit("/", 1)[-1]
    suffix = ".receipt.json"
    if not receipt_ok or not filename.endswith(suffix):
        return False
    receipt_id = filename[:-len(suffix)]
    record_type = existing_receipt.get("record_type")
    if not isinstance(record_type, str) or not record_type:
        return False
    expected_intake_path = receipt_path.replace(
        "/intake/receipts/", "/intake/submissions/", 1
    ).replace(suffix, ".submission.json")
    expected_pending_path = f"record-chain/pending/{receipt_id}.{record_type}.pending.json"
    return (
        (existing_receipt.get("server_receipt_id") or existing_receipt.get("receipt_id")) == receipt_id
        and existing_receipt.get("submission_sha256") == submission_sha256
        and existing_receipt.get("original_submission_sha256", submission_sha256) == submission_sha256
        and existing_receipt.get("stored_submission_sha256") == stored_submission_sha256
        and existing_receipt.get("receipt_path") == receipt_path
        and existing_receipt.get("intake_submission_path") == expected_intake_path
        and existing_receipt.get("pending_file_path") == expected_pending_path
    )
''',
)

# 3. Add an explicit discriminator so public submit-response oneOf is unambiguous.
replace_once(
    MODELS,
    '''    accepted: bool
    submitted: bool = False
    receipt_id: str = ""
''',
    '''    accepted: bool
    submitted: bool = False
    duplicate: bool = False
    receipt_id: str = ""
''',
)
replace_once(
    APP,
    '''    return SubmitResponse(
        accepted=True,
        submitted=True,
        receipt_id=receipt_id,
''',
    '''    return SubmitResponse(
        accepted=True,
        submitted=True,
        duplicate=True,
        receipt_id=receipt_id,
''',
)
replace_once(
    APP,
    '''                return SubmitResponse(
                    accepted=True,
                    submitted=True,
                    receipt_id=existing_receipt.get("server_receipt_id") or existing_receipt.get("receipt_id") or receipt_id,
''',
    '''                return SubmitResponse(
                    accepted=True,
                    submitted=True,
                    duplicate=True,
                    receipt_id=existing_receipt.get("server_receipt_id") or existing_receipt.get("receipt_id") or receipt_id,
''',
)

# 4. Dry-run must not claim a created pending artifact or expose a non-durable receipt through cache.
replace_once(
    APP,
    '''    # Track all created pending file paths
    created_pending_records: list[str] = [pending_file_path]
''',
    '''    # Track only pending files that actually became durable.
    created_pending_records: list[str] = []
''',
)
replace_once(
    APP,
    '''            commit_sha = atomic_result.get("commit", {}).get("sha")
            logger.info("Atomically materialized intake transaction %s", receipt_id)
''',
    '''            commit_sha = atomic_result.get("commit", {}).get("sha")
            created_pending_records = [pending_file_path]
            logger.info("Atomically materialized intake transaction %s", receipt_id)
''',
)
replace_once(
    APP,
    '''    # --- store receipt in memory (NOT mutated — same bytes as persisted) ---
    _receipt_store[receipt_id] = receipt_data
''',
    '''    # Cache only receipts that became durable. A dry-run receipt is returned
    # in the immediate response but must not masquerade as retrievable intake.
    if _WRITE_MODE == "github_contents_pending":
        _receipt_store[receipt_id] = receipt_data
''',
)

# 5. Atomic conflict recovery must not leak an unhandled index-read exception.
replace_once(
    APP,
    '''            existing_index = await _read_idempotency_index(original_submission_sha256)
            if existing_index is not None:
''',
    '''            try:
                existing_index = await _read_idempotency_index(original_submission_sha256)
            except Exception as lookup_exc:
                logger.error(
                    "Atomic conflict idempotency lookup failed for %s: %s",
                    original_submission_sha256[:16],
                    lookup_exc,
                )
                return SubmitResponse(
                    accepted=False,
                    submitted=False,
                    record_type=record_type,
                    submission_sha256=original_submission_sha256,
                    received_raw_body_sha256=received_raw_body_sha256,
                    diagnostics=[Diagnostic(
                        code="INTAKE_ATOMIC_CONFLICT_LOOKUP_FAILED",
                        severity="error",
                        field="record-chain/intake/by-submission-sha256",
                        message=f"Atomic path conflict occurred and the winning idempotency state could not be read: {lookup_exc}",
                        meaning="The gateway failed closed instead of guessing whether the concurrent intake succeeded.",
                        suggested_fix="Retry the exact same submission later without rebuilding or re-signing it.",
                        retry_allowed=True,
                    )],
                    boundary=_build_submit_boundary(body),
                )
            if existing_index is not None:
''',
)

# 6. Verify receipt-status paths canonically and independently recompute final record hashes.
marker = '''async def _read_receipt_final_status(receipt_id: str) -> dict[str, Any] | None:
'''
helper = '''def _record_chain_record_sha256(record: dict[str, Any]) -> str:
    """Recompute the canonical Record-Chain record hash (newline included)."""
    material = dict(record)
    material.pop("record_sha256", None)
    canonical_with_newline = canonical_dumps(material) + "\\n"
    return hashlib.sha256(canonical_with_newline.encode("utf-8")).hexdigest()


'''
text = read(APP)
if text.count(marker) != 1 or helper in text:
    raise RuntimeError("app.py: receipt-status helper insertion target invalid")
write(APP, text.replace(marker, helper + marker, 1))
replace_once(APP, "    status = json.loads(text)\n", "    status = parse_json_strict(text)\n")
replace_once(
    APP,
    '''    pending_path = status.get("pending_file_path")
    if not isinstance(pending_path, str) or not pending_path.startswith("record-chain/pending/"):
        raise RuntimeError(f"receipt-status pending_file_path invalid at {path}")
''',
    '''    pending_path = status.get("pending_file_path")
    pending_pattern = rf"record-chain/pending/{re.escape(receipt_id)}\\.[a-z_]+\\.pending\\.json"
    if not isinstance(pending_path, str) or not re.fullmatch(pending_pattern, pending_path):
        raise RuntimeError(f"receipt-status pending_file_path invalid or receipt-mismatched at {path}")
''',
)
replace_once(
    APP,
    '''        final_record = json.loads(final_text)
        if final_record.get("record_id") != final_id or final_record.get("record_sha256") != final_sha:
            raise RuntimeError(f"receipt-status final record binding mismatch at {path}")
''',
    '''        final_record = parse_json_strict(final_text)
        if not isinstance(final_record, dict):
            raise RuntimeError(f"receipt-status final record is not an object at {expected_path}")
        if final_record.get("record_id") != final_id or final_record.get("record_sha256") != final_sha:
            raise RuntimeError(f"receipt-status final record binding mismatch at {path}")
        if _record_chain_record_sha256(final_record) != final_sha:
            raise RuntimeError(f"receipt-status final record hash recomputation failed at {path}")
''',
)
replace_once(
    APP,
    '''        rejection_path = status.get("rejection_path")
        if not isinstance(rejection_path, str) or not rejection_path.startswith("record-chain/rejected/"):
            raise RuntimeError(f"receipt-status rejection_path invalid at {path}")
        rejection_text = await get_file_text(rejection_path)
''',
    '''        rejection_path = status.get("rejection_path")
        pending_name = pending_path.rsplit("/", 1)[-1]
        expected_rejection_path = f"record-chain/rejected/{pending_name[:-5]}.rejection.json"
        if rejection_path != expected_rejection_path:
            raise RuntimeError(f"receipt-status rejection_path invalid or pending-mismatched at {path}")
        rejection_text = await get_file_text(rejection_path)
''',
)
replace_once(
    APP,
    '''        rejection = json.loads(rejection_text)
        if rejection.get("source_pending") != pending_path.rsplit("/", 1)[-1]:
''',
    '''        rejection = parse_json_strict(rejection_text)
        if not isinstance(rejection, dict):
            raise RuntimeError(f"receipt-status rejection metadata is not an object at {rejection_path}")
        if rejection.get("source_pending") != pending_path.rsplit("/", 1)[-1]:
''',
)
replace_once(APP, "            receipt = json.loads(text)\n", "            receipt = parse_json_strict(text)\n")

# 7. Receipt warning objects and 404 response must match the published schema.
replace_once(
    APP,
    '''        envelope_warnings = [{
            "code": "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE",
            "receipt_path": receipt_path,
            "retryable": True,
        }]
''',
    '''        envelope_warnings = [{
            "code": "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE",
            "message": "Durable receipt storage could not be read; a hash-verified in-memory cache entry was returned.",
            "receipt_path": receipt_path,
            "retryable": True,
        }]
''',
)
replace_once(
    APP,
    '''    raise HTTPException(
        status_code=404,
        detail={
            "code": "RECEIPT_NOT_FOUND",
            "message": f"Receipt '{receipt_id}' not found",
            "receipt_id": receipt_id,
            "receipt_path": receipt_path,
            "retryable": False,
        },
    )
''',
    '''    return JSONResponse(
        status_code=404,
        content={
            "found": False,
            "diagnostics": [{
                "code": "RECEIPT_NOT_FOUND",
                "severity": "error",
                "message": f"Receipt '{receipt_id}' not found",
                "receipt_id": receipt_id,
                "receipt_path": receipt_path,
                "retry_allowed": False,
            }],
        },
    )
''',
)

# 8. Reconciliation must never expose an orphan attempted commit as the durable commit.
insert = '''def _authoritative_reconciled_commit_sha(
    reconciliation: str,
    observed_head: str,
    new_commit_sha: str,
) -> str:
    if reconciliation == "commit_reachable":
        return new_commit_sha
    if reconciliation == "equivalent_tree":
        return observed_head
    raise ValueError(f"Unknown atomic reconciliation mode: {reconciliation}")


'''
marker = '''async def create_files_atomic(
'''
text = read(ATOMIC)
if text.count(marker) != 1 or insert in text:
    raise RuntimeError("github_atomic.py: authoritative commit helper insertion target invalid")
write(ATOMIC, text.replace(marker, insert + marker, 1))
replace_once(
    ATOMIC,
    '''                    return {
                        "commit": {"sha": new_commit_sha},
                        "atomic": True,
                        "reconciled_after_error": True,
                        "reconciliation": reconciliation,
                        "observed_head_sha": observed_head,
                    }
''',
    '''                    committed_sha = _authoritative_reconciled_commit_sha(
                        reconciliation, observed_head, new_commit_sha
                    )
                    return {
                        "commit": {"sha": committed_sha},
                        "attempted_commit_sha": new_commit_sha,
                        "atomic": True,
                        "reconciled_after_error": True,
                        "reconciliation": reconciliation,
                        "observed_head_sha": observed_head,
                    }
''',
)
replace_once(
    ATOMIC,
    '''            if update_response.status_code == 200:
                updated_sha = update_response.json().get("object", {}).get("sha")
                if updated_sha and updated_sha != new_commit_sha:
                    raise RuntimeError(
                        "GitHub ref update returned a different commit SHA: "
                        f"expected {new_commit_sha}, got {updated_sha}"
                    )
                return {
                    "commit": {"sha": new_commit_sha},
                    "atomic": True,
                    "reconciled_existing": False,
                }
''',
    '''            if update_response.status_code == 200:
                updated_sha = update_response.json().get("object", {}).get("sha")
                if updated_sha == new_commit_sha:
                    return {
                        "commit": {"sha": new_commit_sha},
                        "atomic": True,
                        "reconciled_existing": False,
                    }
                try:
                    reconciliation, observed_head = await _reconcile_atomic_write(
                        client,
                        files,
                        branch,
                        ref_url,
                        new_commit_sha,
                    )
                except Exception as reconcile_exc:
                    raise RuntimeError(
                        "GitHub ref update returned 200 without the expected commit SHA "
                        "and branch reconciliation failed"
                    ) from reconcile_exc
                if reconciliation:
                    committed_sha = _authoritative_reconciled_commit_sha(
                        reconciliation, observed_head, new_commit_sha
                    )
                    return {
                        "commit": {"sha": committed_sha},
                        "attempted_commit_sha": new_commit_sha,
                        "atomic": True,
                        "reconciled_after_response": True,
                        "reconciliation": reconciliation,
                        "observed_head_sha": observed_head,
                        "response_commit_sha": updated_sha,
                    }
                raise RuntimeError(
                    "GitHub ref update returned 200 without proving the intended commit durable: "
                    f"expected {new_commit_sha}, got {updated_sha!r}"
                )
''',
)
replace_once(
    ATOMIC,
    '''            if reconciliation:
                return {
                    "commit": {"sha": new_commit_sha},
                    "atomic": True,
                    "reconciled_after_error": True,
                    "reconciliation": reconciliation,
                    "observed_head_sha": observed_head,
                }
''',
    '''            if reconciliation:
                committed_sha = _authoritative_reconciled_commit_sha(
                    reconciliation, observed_head, new_commit_sha
                )
                return {
                    "commit": {"sha": committed_sha},
                    "attempted_commit_sha": new_commit_sha,
                    "atomic": True,
                    "reconciled_after_error": True,
                    "reconciliation": reconciliation,
                    "observed_head_sha": observed_head,
                }
''',
)
replace_once(
    ATOMIC,
    '''    Existing paths are never overwritten. Branch races are retried. If the
    ref-update response is ambiguous, exact readback determines whether the
    transaction committed before an error was observed.
''',
    '''    Existing paths are never overwritten. Branch races are retried. If the
    ref-update response is ambiguous, commit ancestry is authoritative and exact
    tree parity is a fallback for an equivalent concurrent writer.
''',
)

# 9. Align public submit-response schema with the emitted discriminator.
schema_path = ROOT / "api/record-chain-submit-response.v1.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
for name, value in (("success", False), ("duplicate", True), ("failure", False)):
    definition = schema["$defs"][name]
    required = definition.setdefault("required", [])
    if "duplicate" not in required:
        insert_at = required.index("submitted") + 1 if "submitted" in required else 0
        required.insert(insert_at, "duplicate")
    definition.setdefault("properties", {})["duplicate"] = {"const": value}
schema.setdefault("properties", {})["duplicate"] = {"type": "boolean"}
schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# 10. Update existing 404 assertion for the published envelope.
replace_once(
    RECEIPT_TEST,
    '''        body = resp.json()
        assert body["detail"]["code"] == "RECEIPT_NOT_FOUND"
        assert body["detail"]["retryable"] is False
''',
    '''        body = resp.json()
        assert body["found"] is False
        assert body["diagnostics"][0]["code"] == "RECEIPT_NOT_FOUND"
        assert body["diagnostics"][0]["retry_allowed"] is False
''',
)

# Validate patched syntax and JSON before tests run.
for py_path in (APP, ATOMIC, MODELS, RECEIPT_TEST):
    ast.parse(read(py_path), filename=py_path)
json.loads((ROOT / "api/record-chain-submit-response.v1.json").read_text(encoding="utf-8"))
print("DEEP_AUDIT_ROUND3_PATCH_APPLIED")
