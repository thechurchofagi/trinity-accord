#!/usr/bin/env python3
from __future__ import annotations

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
        raise RuntimeError(f"{path}: expected exactly one replacement target, found {count}")
    write(path, text.replace(old, new, 1))


def replace_between(path: str, start_marker: str, end_marker: str, replacement: str) -> None:
    text = read(path)
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    write(path, text[:start] + replacement + text[end:])


# ---------------------------------------------------------------------------
# 1. Harden atomic ref-update reconciliation.
# ---------------------------------------------------------------------------
atomic_path = "apps/record_chain_intake_gateway/gateway/github_atomic.py"
replace_once(
    atomic_path,
    '''    return (
        all(state == "absent" for state in states),
        all(state == "exact" for state in states),
    )


async def create_files_atomic(
''',
    '''    return (
        all(state == "absent" for state in states),
        all(state == "exact" for state in states),
    )


async def _read_ref_head(
    client: httpx.AsyncClient,
    ref_url: str,
    branch: str,
) -> str:
    response = await client.get(ref_url, headers=_headers())
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error {response.status_code} reading branch {branch}"
        )
    head_sha = response.json().get("object", {}).get("sha")
    if not head_sha:
        raise RuntimeError(f"GitHub branch {branch} has no commit SHA")
    return str(head_sha)


async def _commit_reachable_from_head(
    client: httpx.AsyncClient,
    commit_sha: str,
    head_sha: str,
) -> bool:
    """Return whether ``commit_sha`` is the branch head or one of its ancestors."""
    if commit_sha == head_sha:
        return True
    response = await client.get(
        f"{_GITHUB_API}/repos/{_repo()}/compare/{commit_sha}...{head_sha}",
        headers=_headers(),
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API error {response.status_code} comparing {commit_sha}...{head_sha}"
        )
    return response.json().get("status") in {"ahead", "identical"}


async def _reconcile_atomic_write(
    client: httpx.AsyncClient,
    files: dict[str, str],
    branch: str,
    ref_url: str,
    new_commit_sha: str,
) -> tuple[str | None, str]:
    """Reconcile a possibly successful ref update against the current branch.

    A push-triggered append may consume the pending file immediately after the
    intake commit lands. Exact live-tree readback alone would then misclassify a
    durable transaction as failed. Commit ancestry is authoritative for our
    exact commit; exact tree state remains a safe fallback for an equivalent
    concurrent writer.
    """
    observed_head = await _read_ref_head(client, ref_url, branch)
    if await _commit_reachable_from_head(client, new_commit_sha, observed_head):
        return "commit_reachable", observed_head

    _, all_exact = await _atomic_files_state(client, files, observed_head)
    if all_exact:
        return "equivalent_tree", observed_head
    return None, observed_head


async def create_files_atomic(
''',
)
replace_once(
    atomic_path,
    '''            ref_response = await client.get(ref_url, headers=_headers())
            if ref_response.status_code != 200:
                raise RuntimeError(
                    f"GitHub API error {ref_response.status_code} reading branch {branch}"
                )
            head_sha = ref_response.json().get("object", {}).get("sha")
            if not head_sha:
                raise RuntimeError(f"GitHub branch {branch} has no commit SHA")
''',
    '''            head_sha = await _read_ref_head(client, ref_url, branch)
''',
)
replace_once(
    atomic_path,
    '''            try:
                update_response = await client.patch(
                    update_ref_url,
                    headers=_headers(),
                    json={"sha": new_commit_sha, "force": False},
                )
            except Exception:
                _, exact_after_error = await _atomic_files_state(
                    client,
                    files,
                    branch,
                )
                if exact_after_error:
                    logger.warning(
                        "Reconciled ambiguous atomic ref update for %s",
                        new_commit_sha,
                    )
                    return {
                        "commit": {"sha": new_commit_sha},
                        "atomic": True,
                        "reconciled_after_error": True,
                    }
                raise

            if update_response.status_code == 200:
                return {
                    "commit": {"sha": new_commit_sha},
                    "atomic": True,
                    "reconciled_existing": False,
                }

            if update_response.status_code in (409, 422) and attempt < max_attempts:
                logger.info(
                    "Branch moved during atomic write; retrying %d/%d",
                    attempt + 1,
                    max_attempts,
                )
                continue

            _, exact_after_response = await _atomic_files_state(
                client,
                files,
                branch,
            )
            if exact_after_response:
                return {
                    "commit": {"sha": new_commit_sha},
                    "atomic": True,
                    "reconciled_after_error": True,
                }
            raise RuntimeError(
                f"GitHub API error {update_response.status_code} advancing branch"
            )
''',
    '''            try:
                update_response = await client.patch(
                    update_ref_url,
                    headers=_headers(),
                    json={"sha": new_commit_sha, "force": False},
                )
            except Exception as update_exc:
                try:
                    reconciliation, observed_head = await _reconcile_atomic_write(
                        client,
                        files,
                        branch,
                        ref_url,
                        new_commit_sha,
                    )
                except Exception as reconcile_exc:
                    logger.warning(
                        "Could not reconcile ambiguous atomic ref update for %s: %s",
                        new_commit_sha,
                        reconcile_exc,
                    )
                    raise update_exc from reconcile_exc
                if reconciliation:
                    logger.warning(
                        "Reconciled ambiguous atomic ref update for %s via %s at %s",
                        new_commit_sha,
                        reconciliation,
                        observed_head,
                    )
                    return {
                        "commit": {"sha": new_commit_sha},
                        "atomic": True,
                        "reconciled_after_error": True,
                        "reconciliation": reconciliation,
                        "observed_head_sha": observed_head,
                    }
                raise update_exc

            if update_response.status_code == 200:
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

            reconciliation: str | None = None
            observed_head: str | None = None
            try:
                reconciliation, observed_head = await _reconcile_atomic_write(
                    client,
                    files,
                    branch,
                    ref_url,
                    new_commit_sha,
                )
            except Exception as reconcile_exc:
                logger.warning(
                    "Could not reconcile GitHub ref response %s for %s: %s",
                    update_response.status_code,
                    new_commit_sha,
                    reconcile_exc,
                )

            if reconciliation:
                return {
                    "commit": {"sha": new_commit_sha},
                    "atomic": True,
                    "reconciled_after_error": True,
                    "reconciliation": reconciliation,
                    "observed_head_sha": observed_head,
                }

            if update_response.status_code in (409, 422) and attempt < max_attempts:
                logger.info(
                    "Branch moved during atomic write; retrying %d/%d",
                    attempt + 1,
                    max_attempts,
                )
                continue

            raise RuntimeError(
                f"GitHub API error {update_response.status_code} advancing branch"
            )
''',
)


# ---------------------------------------------------------------------------
# 2. Bind duplicate indexes to receipts and recognize terminal transactions.
# ---------------------------------------------------------------------------
app_path = "apps/record_chain_intake_gateway/app.py"
new_duplicate_helper = '''async def _submit_response_from_idempotency_index(
    *,
    index: dict[str, Any],
    record_type: str,
    submission_sha256: str,
    received_raw_body_sha256: str,
    body: dict[str, Any],
) -> SubmitResponse:
    if index.get("submission_sha256") != submission_sha256:
        raise RuntimeError("Idempotency index does not bind the requested submission hash")

    receipt_path = index.get("receipt_path", "")
    if not isinstance(receipt_path, str) or not receipt_path:
        raise RuntimeError("Idempotency index is missing receipt_path")

    receipt_text = await get_file_text(receipt_path)
    if not receipt_text:
        raise RuntimeError(f"Idempotency receipt is missing: {receipt_path}")

    receipt_data_raw = json.loads(receipt_text)
    if not isinstance(receipt_data_raw, dict):
        raise RuntimeError(f"Idempotency receipt is not a JSON object: {receipt_path}")
    receipt_data: dict[str, Any] = receipt_data_raw

    if not receipt_data.get("receipt_sha256"):
        raise HTTPException(
            status_code=500,
            detail={
                "code": "IDEMPOTENCY_RECEIPT_MISSING_HASH",
                "message": f"Receipt has no receipt_sha256 at {receipt_path}",
            },
        )
    hash_ok, hash_err = verify_receipt_sha256(receipt_data)
    if not hash_ok:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "IDEMPOTENCY_RECEIPT_HASH_INVALID",
                "message": f"Receipt hash invalid: {hash_err} at {receipt_path}",
            },
        )

    receipt_id = (
        receipt_data.get("server_receipt_id")
        or receipt_data.get("receipt_id")
        or index.get("receipt_id")
        or ""
    )
    if not receipt_id:
        raise RuntimeError(f"Idempotency receipt has no receipt id: {receipt_path}")
    if index.get("receipt_id") != receipt_id:
        raise RuntimeError(
            f"Idempotency receipt_id mismatch: index={index.get('receipt_id')} receipt={receipt_id}"
        )

    expected_bindings = {
        "submission_sha256": submission_sha256,
        "stored_submission_sha256": index.get("stored_submission_sha256"),
        "receipt_path": receipt_path,
        "pending_file_path": index.get("pending_file_path"),
        "intake_submission_path": index.get("intake_submission_path"),
        "record_type": index.get("record_type", record_type),
    }
    for field, expected in expected_bindings.items():
        if not isinstance(expected, str) or not expected:
            raise RuntimeError(f"Idempotency index is missing {field}")
        actual = receipt_data.get(field)
        if actual != expected:
            raise RuntimeError(
                f"Idempotency receipt binding mismatch for {field}: "
                f"index={expected!r} receipt={actual!r}"
            )

    original_hash = receipt_data.get("original_submission_sha256")
    if original_hash not in (None, "", submission_sha256):
        raise RuntimeError(
            "Idempotency receipt original_submission_sha256 does not bind the requested submission"
        )

    has_materialization_fields = "pending_written" in index or "transaction_state" in index
    if has_materialization_fields:
        if index.get("pending_written") is not True:
            raise RuntimeError(
                "Idempotency index is not materialized: pending_written is not true"
            )
        if index.get("transaction_state") != "pending_written":
            raise RuntimeError(
                f"Idempotency index is not materialized: transaction_state={index.get('transaction_state')!r}"
            )
        committed_at = index.get("pending_committed_at")
        if not isinstance(committed_at, str) or not committed_at:
            raise RuntimeError(
                "Idempotency index is not materialized: pending_committed_at is missing"
            )

    pending_path = index.get("pending_file_path")
    if not isinstance(pending_path, str) or not pending_path:
        raise RuntimeError("Idempotency index missing pending_file_path")

    pending_sha = await get_file_sha(pending_path) if has_materialization_fields else None
    terminal_status: dict[str, Any] | None = None
    if has_materialization_fields and pending_sha is None:
        terminal_status = await _read_receipt_final_status(receipt_id)
        if terminal_status is None:
            raise RuntimeError(
                f"Idempotency pending file is missing and no terminal receipt status exists: {pending_path}"
            )
        if terminal_status.get("pending_file_path") != pending_path:
            raise RuntimeError(
                "Terminal receipt status does not bind the idempotency pending file: "
                f"index={pending_path!r} status={terminal_status.get('pending_file_path')!r}"
            )

    if terminal_status is not None:
        append_status = str(terminal_status["append_status"])
        warnings = [
            f"Duplicate submission: original immutable receipt returned; transaction is already {append_status}."
        ]
        created_pending_records: list[str] = []
    else:
        append_status = "duplicate_existing_submission_returned"
        warnings = [
            "Duplicate submission: existing idempotency index found; original receipt returned."
        ]
        created_pending_records = [pending_path]

    return SubmitResponse(
        accepted=True,
        submitted=True,
        receipt_id=receipt_id,
        record_type=index.get("record_type", record_type),
        submission_sha256=submission_sha256,
        received_raw_body_sha256=received_raw_body_sha256,
        pending_file_path=pending_path,
        intake_submission_path=index.get("intake_submission_path", ""),
        receipt_path=receipt_path,
        server_created_at=receipt_data.get("accepted_at", index.get("created_at", "")),
        append_status=append_status,
        receipt=receipt_data,
        diagnostics=[],
        warnings=warnings,
        boundary=_build_submit_boundary(body),
        created_pending_records=created_pending_records,
    )
'''
replace_between(
    app_path,
    "async def _submit_response_from_idempotency_index(",
    "\n\n# ---------------------------------------------------------------------------\n# BLOCKER 2 helper",
    new_duplicate_helper,
)

new_receipt_envelope = '''async def _build_receipt_envelope(
    receipt: dict[str, Any],
    receipt_id: str,
    receipt_path: str,
    envelope_warnings: list[str | dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a receipt envelope without overstating unverifiable final status."""
    warnings: list[str | dict[str, Any]] = list(envelope_warnings or [])
    final_status_error: Exception | None = None
    try:
        final_status_data = await _read_receipt_final_status(receipt_id)
    except Exception as exc:
        logger.warning("Failed to verify receipt-status for %s: %s", receipt_id, exc)
        final_status_data = None
        final_status_error = exc
        warnings.append({
            "code": "RECEIPT_FINAL_STATUS_UNAVAILABLE",
            "message": "The immutable receipt is valid, but final append status could not be verified.",
            "retryable": True,
        })

    if final_status_data:
        append_status = final_status_data.get("append_status", "unknown")
        final_record_id = final_status_data.get("final_record_id")
        final_record_sha256 = final_status_data.get("final_record_sha256")
        rejection_path = final_status_data.get("rejection_path")
        rejection_code = final_status_data.get("rejection_code")
        updated_at = final_status_data.get("updated_at")
    else:
        final_record_id = None
        final_record_sha256 = None
        rejection_path = None
        rejection_code = None
        updated_at = None
        pending_path = receipt.get("pending_file_path")
        if final_status_error is not None:
            append_status = "unknown"
        elif isinstance(pending_path, str) and pending_path:
            try:
                pending_sha = await get_file_sha(pending_path)
            except Exception as exc:
                append_status = "unknown"
                warnings.append({
                    "code": "RECEIPT_PENDING_STATUS_UNAVAILABLE",
                    "message": f"Could not verify whether the pending marker still exists: {exc}",
                    "retryable": True,
                })
            else:
                if pending_sha is not None:
                    append_status = "pending"
                else:
                    append_status = "unknown"
                    warnings.append({
                        "code": "RECEIPT_TERMINAL_STATUS_MISSING",
                        "message": "Neither the pending marker nor a verified terminal receipt-status sidecar is visible.",
                        "retryable": True,
                    })
        else:
            append_status = "unknown"

    result: dict[str, Any] = {
        "found": True,
        "receipt": receipt,
        "receipt_id": receipt_id,
        "receipt_path": receipt_path,
        "receipt_hash_verified": True,
        "final_status": {
            "append_status": append_status,
            "final_record_id": final_record_id,
            "final_record_sha256": final_record_sha256,
            "rejection_path": rejection_path,
            "rejection_code": rejection_code,
            "updated_at": updated_at,
        },
    }
    if warnings:
        result["envelope_warnings"] = warnings
    return result
'''
replace_between(
    app_path,
    "async def _build_receipt_envelope(",
    '\n\n@app.get("/record-chain/receipt/{receipt_id}")',
    new_receipt_envelope,
)


# ---------------------------------------------------------------------------
# 3. Harden the live multi-agent smoke against cache splits and worker crashes.
# ---------------------------------------------------------------------------
swarm_path = "scripts/smoke_external_agent_journey_swarm.py"
replace_once(
    swarm_path,
    '''def repo_links_digest() -> str | None:
''',
    '''def result_object(
    fetched: dict[tuple[str, bool], FetchResult],
    path: str,
    cache_bust: bool,
    errors: list[str],
) -> dict[str, Any]:
    result = fetched.get((path, cache_bust))
    label = f"{path}{' cache-busted' if cache_bust else ' canonical'}"
    if result is None:
        errors.append(f"{label}: internal fetch result missing")
        return {}
    if result.error or result.status == 0 or result.status >= 400:
        return {}
    if not isinstance(result.data, dict):
        errors.append(f"{label}: JSON root must be an object")
        return {}
    return result.data


def canonical_cache_split_errors(
    fetched: dict[tuple[str, bool], FetchResult],
) -> list[str]:
    errors: list[str] = []
    for path in CORE_DISCOVERY_PATHS:
        canonical = fetched.get((path, False))
        busted = fetched.get((path, True))
        if canonical is None or busted is None:
            continue
        if canonical.error or busted.error:
            continue
        if canonical.status == 0 or busted.status == 0:
            continue
        if canonical.status >= 400 or busted.status >= 400:
            continue
        if canonical.digest != busted.digest:
            errors.append(
                f"{path} canonical/cache-busted content split: "
                f"{canonical.digest!r} vs {busted.digest!r}"
            )
    return errors


def repo_links_digest() -> str | None:
''',
)
old_objects = '''    links = fetched.get(("/api/links.json", False), FetchResult("", "", 0, "", {}, {}, [])).data or {}
    links_busted = fetched.get(("/api/links.json", True), FetchResult("", "", 0, "", {}, {}, [])).data or {}
    well_known = fetched.get(("/.well-known/trinity-accord.json", False), FetchResult("", "", 0, "", {}, {}, [])).data or {}
    first_contact = fetched.get(("/api/agent-first-contact.json", False), FetchResult("", "", 0, "", {}, {}, [])).data or {}
    task_router = fetched.get(("/api/agent-task-router.v1.json", False), FetchResult("", "", 0, "", {}, {}, [])).data or {}
    output_policy = fetched.get(("/api/agent-output-policy.v1.json", False), FetchResult("", "", 0, "", {}, {}, [])).data or {}
    agent_start = fetched.get(("/api/agent-start.v2.json", False), FetchResult("", "", 0, "", {}, {}, [])).data or {}
    gateway = fetched.get(("/api/record-chain-intake-gateway.v1.json", False), FetchResult("", "", 0, "", {}, {}, [])).data or {}
    builder = fetched.get(("/api/record-chain-builder-bundles.v1.json", False), FetchResult("", "", 0, "", {}, {}, [])).data or {}

    repo_digest = repo_links_digest()
'''
new_objects = '''    errors.extend(canonical_cache_split_errors(fetched))
    links = result_object(fetched, "/api/links.json", False, errors)
    links_busted = result_object(fetched, "/api/links.json", True, errors)
    well_known = result_object(fetched, "/.well-known/trinity-accord.json", False, errors)
    first_contact = result_object(fetched, "/api/agent-first-contact.json", False, errors)
    task_router = result_object(fetched, "/api/agent-task-router.v1.json", False, errors)
    output_policy = result_object(fetched, "/api/agent-output-policy.v1.json", False, errors)
    agent_start = result_object(fetched, "/api/agent-start.v2.json", False, errors)
    gateway = result_object(fetched, "/api/record-chain-intake-gateway.v1.json", False, errors)
    builder = result_object(fetched, "/api/record-chain-builder-bundles.v1.json", False, errors)

    repo_digest = repo_links_digest()
'''
replace_once(swarm_path, old_objects, new_objects)
old_futures = '''    all_results: list[AgentResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = []
        for round_id in range(args.rounds):
            for agent_id in range(args.agents):
                route_family = route_names[agent_id % len(route_names)]
                global_agent_id = round_id * args.agents + agent_id
                futures.append(
                    pool.submit(
                        validate_agent,
                        global_agent_id,
                        route_family,
                        args.site,
                        args.timeout,
                        cache_token,
                    )
                )

        for future in concurrent.futures.as_completed(futures):
            all_results.append(future.result())
'''
new_futures = '''    all_results: list[AgentResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures: dict[concurrent.futures.Future[AgentResult], tuple[int, str]] = {}
        for round_id in range(args.rounds):
            for agent_id in range(args.agents):
                route_family = route_names[agent_id % len(route_names)]
                global_agent_id = round_id * args.agents + agent_id
                future = pool.submit(
                    validate_agent,
                    global_agent_id,
                    route_family,
                    args.site,
                    args.timeout,
                    cache_token,
                )
                futures[future] = (global_agent_id, route_family)

        for future in concurrent.futures.as_completed(futures):
            global_agent_id, route_family = futures[future]
            try:
                all_results.append(future.result())
            except Exception as exc:
                all_results.append(AgentResult(
                    global_agent_id,
                    route_family,
                    False,
                    [f"unhandled validator exception: {type(exc).__name__}: {exc}"],
                    {},
                    [],
                ))
'''
replace_once(swarm_path, old_futures, new_futures)


# ---------------------------------------------------------------------------
# 4. Keep the public receipt schema aligned with actual warning envelopes.
# ---------------------------------------------------------------------------
schema_path = ROOT / "api/record-chain-receipt-response.v1.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
schema["$defs"]["success"]["properties"]["envelope_warnings"]["items"] = {
    "oneOf": [
        {"type": "string"},
        {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {"type": "string"},
                "message": {"type": "string"},
                "retryable": {"type": "boolean"},
            },
            "additionalProperties": True,
        },
    ]
}
schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 5. Regression tests for every confirmed bug.
# ---------------------------------------------------------------------------
with (ROOT / "apps/record_chain_intake_gateway/tests/test_deep_transaction_recovery.py").open("a", encoding="utf-8") as fh:
    fh.write(r'''

class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class _ReconcileClient:
    def __init__(self, compare_status: str):
        self.compare_status = compare_status

    async def get(self, url: str, **kwargs):
        if "/git/ref/" in url:
            return _FakeResponse(200, {"object": {"sha": "current-head"}})
        if "/compare/" in url:
            return _FakeResponse(200, {"status": self.compare_status})
        raise AssertionError(url)


@pytest.mark.asyncio
async def test_atomic_reconciliation_accepts_commit_ancestry_after_pending_consumed(monkeypatch) -> None:
    client = _ReconcileClient("ahead")

    async def must_not_read_live_files(*args, **kwargs):
        raise AssertionError("ancestry should reconcile before live-tree readback")

    monkeypatch.setattr(github_atomic, "_atomic_files_state", must_not_read_live_files)
    reconciliation, head = await github_atomic._reconcile_atomic_write(
        client,
        {"pending.json": "content"},
        "main",
        "https://api.github.com/repos/test/repo/git/ref/heads/main",
        "intake-commit",
    )
    assert reconciliation == "commit_reachable"
    assert head == "current-head"


@pytest.mark.asyncio
async def test_atomic_reconciliation_accepts_equivalent_concurrent_tree(monkeypatch) -> None:
    client = _ReconcileClient("diverged")

    async def exact_state(*args, **kwargs):
        return False, True

    monkeypatch.setattr(github_atomic, "_atomic_files_state", exact_state)
    reconciliation, head = await github_atomic._reconcile_atomic_write(
        client,
        {"pending.json": "content"},
        "main",
        "https://api.github.com/repos/test/repo/git/ref/heads/main",
        "intake-commit",
    )
    assert reconciliation == "equivalent_tree"
    assert head == "current-head"
''')

with (ROOT / "apps/record_chain_intake_gateway/tests/test_idempotency_index.py").open("a", encoding="utf-8") as fh:
    fh.write(r'''

class TestTerminalDuplicateResolution:
    def test_finalized_duplicate_returns_original_receipt_without_pending_marker(
        self, signed_echo_submission, monkeypatch
    ):
        index = _index_for(signed_echo_submission)
        receipt = _receipt_for(index)
        final_path = "record-chain/records/R-000000123.json"
        status_path = f"record-chain/receipt-status/{index['receipt_id']}.json"
        status = {
            "schema": "trinityaccord.record-chain-receipt-final-status.v1",
            "receipt_id": index["receipt_id"],
            "pending_file_path": index["pending_file_path"],
            "append_status": "appended",
            "final_record_id": "R-000000123",
            "final_record_path": final_path,
            "final_record_sha256": "c" * 64,
            "rejection_path": None,
            "rejection_code": None,
            "updated_at": "2026-01-01T00:01:00Z",
        }

        async def read(path: str):
            if "by-submission-sha256" in path:
                return json.dumps(index)
            if path == index["receipt_path"]:
                return json.dumps(receipt)
            if path == status_path:
                return json.dumps(status)
            if path == final_path:
                return json.dumps({
                    "record_id": "R-000000123",
                    "record_sha256": "c" * 64,
                })
            return None

        atomic, rate, dispatch = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is True
        assert data["append_status"] == "appended"
        assert data["created_pending_records"] == []
        atomic.assert_not_awaited()
        rate.assert_not_called()
        dispatch.assert_not_awaited()

    def test_duplicate_rejects_valid_but_unrelated_receipt_binding(
        self, signed_echo_submission, monkeypatch
    ):
        index = _index_for(signed_echo_submission)
        receipt = _receipt_for(index)
        receipt["pending_file_path"] = "record-chain/pending/other.pending.json"
        receipt["receipt_sha256"] = compute_receipt_sha256(receipt)

        async def read(path: str):
            if "by-submission-sha256" in path:
                return json.dumps(index)
            if path == index["receipt_path"]:
                return json.dumps(receipt)
            return None

        atomic, rate, dispatch = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value="pending-sha"))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is False
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in {d["code"] for d in data["diagnostics"]}
        atomic.assert_not_awaited()
        rate.assert_not_called()
        dispatch.assert_not_awaited()

    def test_missing_pending_without_terminal_status_remains_fail_closed(
        self, signed_echo_submission, monkeypatch
    ):
        index = _index_for(signed_echo_submission)
        receipt = _receipt_for(index)

        async def read(path: str):
            if "by-submission-sha256" in path:
                return json.dumps(index)
            if path == index["receipt_path"]:
                return json.dumps(receipt)
            return None

        atomic, rate, dispatch = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is False
        assert "INTAKE_TRANSACTION_NOT_MATERIALIZED" in {d["code"] for d in data["diagnostics"]}
        atomic.assert_not_awaited()
        rate.assert_not_called()
        dispatch.assert_not_awaited()
''')

with (ROOT / "apps/record_chain_intake_gateway/tests/test_receipt.py").open("a", encoding="utf-8") as fh:
    fh.write(r'''

    def test_success_envelope_declares_found_true(self, client: TestClient) -> None:
        receipt = self._make_receipt()

        async def read(path: str):
            if path.startswith("record-chain/intake/receipts/"):
                return json.dumps(receipt)
            return None

        with patch("apps.record_chain_intake_gateway.app.get_file_text", new=AsyncMock(side_effect=read)):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 200
        assert resp.json()["found"] is True

    def test_invalid_final_status_is_unknown_not_pending(self, client: TestClient) -> None:
        receipt = self._make_receipt()
        receipt["pending_file_path"] = "record-chain/pending/rcg-20260613-abcdef123456.echo.pending.json"
        from apps.record_chain_intake_gateway.gateway.receipts import compute_receipt_sha256
        receipt["receipt_sha256"] = compute_receipt_sha256(receipt)

        async def read(path: str):
            if path.startswith("record-chain/intake/receipts/"):
                return json.dumps(receipt)
            if path.startswith("record-chain/receipt-status/"):
                return json.dumps({"schema": "wrong"})
            return None

        with patch("apps.record_chain_intake_gateway.app.get_file_text", new=AsyncMock(side_effect=read)):
            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")
        assert resp.status_code == 200
        body = resp.json()
        assert body["final_status"]["append_status"] == "unknown"
        assert any(
            warning.get("code") == "RECEIPT_FINAL_STATUS_UNAVAILABLE"
            for warning in body.get("envelope_warnings", [])
            if isinstance(warning, dict)
        )
''')

swarm_test = ROOT / "tests/test_external_agent_journey_swarm_contract.py"
text = swarm_test.read_text(encoding="utf-8")
insert = '''\nfrom scripts.smoke_external_agent_journey_swarm import FetchResult, canonical_cache_split_errors\n'''
anchor = "ROOT = Path(__file__).resolve().parents[1]\n"
if insert.strip() not in text:
    text = text.replace(anchor, anchor + insert, 1)
text += r'''


def test_swarm_detects_cache_split_for_any_core_contract() -> None:
    fetched = {
        ("/api/agent-first-contact.json", False): FetchResult(
            "/api/agent-first-contact.json", "canonical", 200, "aaa", {}, {}, []
        ),
        ("/api/agent-first-contact.json", True): FetchResult(
            "/api/agent-first-contact.json", "busted", 200, "bbb", {}, {}, []
        ),
    }
    errors = canonical_cache_split_errors(fetched)
    assert errors == [
        "/api/agent-first-contact.json canonical/cache-busted content split: 'aaa' vs 'bbb'"
    ]


def test_swarm_ignores_parity_when_one_fetch_failed() -> None:
    fetched = {
        ("/api/agent-first-contact.json", False): FetchResult(
            "/api/agent-first-contact.json", "canonical", 200, "aaa", {}, {}, []
        ),
        ("/api/agent-first-contact.json", True): FetchResult(
            "/api/agent-first-contact.json", "busted", 0, "", None, {}, [], error="timeout"
        ),
    }
    assert canonical_cache_split_errors(fetched) == []
'''
swarm_test.write_text(text, encoding="utf-8")

print("POST_ATOMIC_DEEP_AUDIT_PATCH_APPLIED")
