# app.py
"""Record-Chain Intake Gateway — FastAPI application."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from apps.record_chain_intake_gateway.gateway.authorship import (
    strip_authorship_for_signing,
    strip_unsigned_projection_fields,
)
from apps.record_chain_intake_gateway.gateway.canonical import canonical_dumps, sha256_canonical_json
from apps.record_chain_intake_gateway.gateway.github_adapter import delete_file, dispatch_workflow, get_file_sha, get_file_text, put_file
from apps.record_chain_intake_gateway.gateway.models import (
    AgentRecovery,
    Diagnostic,
    ErrorResponse,
    PreflightResponse,
    ReadinessResponse,
    RetiredResponse,
    ServerReceipt,
    SubmitResponse,
)
from apps.record_chain_intake_gateway.gateway.rate_limit import check_rate_limit
from apps.record_chain_intake_gateway.gateway.receipts import make_legacy_receipt_id, make_receipt, make_receipt_id, verify_receipt_sha256
from apps.record_chain_intake_gateway.gateway.runtime import get_runtime_info
from apps.record_chain_intake_gateway.gateway.validation import (
    ALLOWED_RECORD_TYPES,
    REQUIRED_BOUNDARY_FIELDS,
    detect_route,
    extract_record_draft,
    validate_submission,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("rcg")

# ---------------------------------------------------------------------------
# Env
# ---------------------------------------------------------------------------
load_dotenv()

_MAX_BODY_BYTES = int(os.environ.get("TRINITY_MAX_SUBMISSION_BYTES", "524288"))
_WRITE_MODE = os.environ.get("TRINITY_SUBMIT_WRITE_MODE", "github_contents_pending")
_APPEND_WORKFLOW = os.environ.get("TRINITY_APPEND_WORKFLOW_FILE", "record-chain-append.yml")
_DISPATCH_APPEND_WORKFLOW = os.environ.get("TRINITY_DISPATCH_APPEND_WORKFLOW", "1").strip().lower() not in {"0", "false", "no", "off"}
_GATEWAY_BASE_URL = os.environ.get("TRINITY_GATEWAY_BASE_URL", "")

# In-memory receipt store (ephemeral; resets on restart)
_receipt_store: dict[str, dict[str, Any]] = {}

# Gateway schema info — must reflect actual validation rules.
# authorship_proof is REQUIRED for all formal record types (not optional).
_GATEWAY_SCHEMA: dict[str, Any] = {
    "version": "1.1.0",
    "accepted_record_types": sorted(ALLOWED_RECORD_TYPES),
    "required_submission_fields": [
        "schema",
        "submission_type",
        "client_generated_at",
        "record_type",
        "record_draft",
        "builder",
        "client_context",
        "submission_boundary",
        "authorship_proof",
    ],
    "optional_submission_fields": ["metadata", "boundary_acknowledgement"],
    "boundary_acknowledgement_fields": len(REQUIRED_BOUNDARY_FIELDS),
    "boundary_acknowledgement_required_fields": sorted(REQUIRED_BOUNDARY_FIELDS),
    "context_readiness_path": "record_draft.context_readiness.declared_context_level",
    "oath_gate": {
        "required": True,
        "policy_url": "/api/record-chain-oath-policy.v1.json",
        "required_for": sorted({
            "echo", "verification", "guardian_application", "guardian_retirement",
            "propagation", "correction", "classification_update",
        }),
        "not_required_for": ["context_insufficient_notice"],
    },
}


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Record-Chain Intake Gateway starting — write_mode=%s, max_body=%d",
        _WRITE_MODE, _MAX_BODY_BYTES,
    )
    yield
    logger.info("Record-Chain Intake Gateway shutting down")


app = FastAPI(
    title="Record-Chain Intake Gateway",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware — body-size enforcement (uses diagnostic shape for 413)
# ---------------------------------------------------------------------------

def _body_too_large_diagnostic_payload(size: int) -> dict[str, Any]:
    """Route-agnostic 413 payload with diagnostic shape. Used by middleware."""
    return {
        "accepted": False,
        "diagnostics": [{
            "code": "REQUEST_BODY_TOO_LARGE",
            "severity": "error",
            "field": None,
            "message": f"Request body too large ({size} > {_MAX_BODY_BYTES} bytes)",
            "meaning": "The request body exceeded the gateway maximum before it could be safely parsed.",
            "suggested_fix": f"Submit a JSON body no larger than {_MAX_BODY_BYTES} bytes.",
            "retry_allowed": True,
        }],
        "boundary": {},
    }


@app.middleware("http")
async def enforce_body_size(request: Request, call_next):
    """Reject requests whose Content-Length exceeds the configured maximum."""
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            size = int(content_length)
            if size > _MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content=_body_too_large_diagnostic_payload(size),
                )
        except ValueError:
            pass
    return await call_next(request)


# ---------------------------------------------------------------------------
# Part G: Streaming body-size limit
# ---------------------------------------------------------------------------

class RequestBodyTooLarge(Exception):
    def __init__(self, size: int):
        self.size = size


async def _read_limited_body(request: Request) -> bytes:
    """Read request body with streaming size enforcement.

    Works even when Content-Length is absent (chunked transfer).
    """
    chunks: list[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > _MAX_BODY_BYTES:
            raise RequestBodyTooLarge(total)
        chunks.append(chunk)
    return b"".join(chunks)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_config() -> None:
    """Ensure required env vars are set."""
    missing = []
    for var in ("TRINITY_REPO_FULL_NAME", "TRINITY_TARGET_BRANCH", "TRINITY_GITHUB_TOKEN"):
        if not os.environ.get(var):
            missing.append(var)
    if missing:
        raise HTTPException(status_code=503, detail=f"Missing required config: {', '.join(missing)}")


def _compute_raw_body_sha256(raw_body: bytes) -> str:
    """Compute SHA-256 hex digest of raw request body bytes."""
    return hashlib.sha256(raw_body).hexdigest()


def _build_gateway_runtime() -> dict[str, Any]:
    """Build the gateway_runtime info dict for responses."""
    info = get_runtime_info()
    return {
        "service": info["service"],
        "version": info["version"],
        "deployed_at": info["deployed_at"],
        "write_mode": info["write_mode"],
        "max_submission_bytes": info["max_submission_bytes"],
        "base_url": _GATEWAY_BASE_URL,
    }


def _extract_oath_verification_summary(draft: dict[str, Any]) -> dict[str, Any] | None:
    """Extract a summary of oath verification for the receipt (no raw readback)."""
    oath = draft.get("submission_oath_verification")
    if not isinstance(oath, dict):
        return None
    return {
        "oath_policy": oath.get("oath_policy", ""),
        "oath_policy_sha256": oath.get("oath_policy_sha256", ""),
        "oath_modules": oath.get("oath_modules", []),
        "canonical_oath_text_sha256": oath.get("canonical_oath_text_sha256", ""),
        "participant_readback_sha256": oath.get("participant_readback_sha256", ""),
        "readback_matches_canonical_oath": oath.get("readback_matches_canonical_oath", False),
        "no_shortcut_oath_acknowledged": oath.get("no_shortcut_oath_acknowledged", False),
        "raw_readback_redacted": True,
    }


def _build_boundary(submission: dict[str, Any]) -> dict[str, bool]:
    """Extract boundary acknowledgement as a dict of bools for the response."""
    boundary = (
        submission.get("submission_boundary")
        or submission.get("boundary_acknowledgement")
    )
    if not boundary and "submission_boundary" not in submission and "boundary_acknowledgement" not in submission:
        boundary = (submission.get("record_draft") or {}).get("non_authority_boundary_acknowledgement")
    if isinstance(boundary, dict):
        return {k: bool(v) for k, v in boundary.items()}
    return {}


def _build_preflight_boundary(submission: dict[str, Any] | None = None) -> dict[str, bool]:
    base = _build_boundary(submission or {})
    base.update({
        "preflight_is_not_submission": True,
        "not_authority": True,
        "not_attestation": True,
        "not_amendment": True,
    })
    return base


def _build_submit_boundary(submission: dict[str, Any] | None = None) -> dict[str, bool]:
    base = _build_boundary(submission or {})
    base.update({
        "receipt_is_not_authority": True,
        "receipt_is_not_attestation": True,
        "receipt_is_not_final_chain_record": True,
        "record_chain_append_is_server_side": True,
    })
    return base


_UNSIGNED_CLIENT_PROJECTION_FIELDS = frozenset({
    "actor_identity",
    "boundary",
    "server_normalization",
    "server_append_metadata",
    "append_assigned_metadata",
    "authorship_verification_status",
    "record_id",
    "record_index",
    "assigned_at",
    "previous_record_sha256",
    "content_sha256",
    "record_sha256",
    "chain_id",
})


def _client_projection_diagnostics(body: dict[str, Any]) -> list[Diagnostic]:
    """Reject client-supplied server projection fields in record_draft.

    External clients should submit the pre-append signed draft. Projection and
    append-assigned fields are derived by the server after verification.
    """
    draft = extract_record_draft(body) or {}
    if not isinstance(draft, dict):
        return []
    diagnostics: list[Diagnostic] = []
    for field in sorted(_UNSIGNED_CLIENT_PROJECTION_FIELDS):
        if field in draft:
            diagnostics.append(Diagnostic(
                code="CLIENT_SUPPLIED_UNSIGNED_PROJECTION_FIELD",
                severity="error",
                field=f"record_draft.{field}",
                message=(
                    f"record_draft.{field} is server-derived or append-assigned "
                    "and must not be supplied by clients."
                ),
                meaning=(
                    "The authorship signature covers the participant's pre-append "
                    "draft. Server projection fields would change the signed payload "
                    "or be outside the signed scope."
                ),
                suggested_fix=(
                    f"Remove record_draft.{field} and rebuild/sign the submission "
                    "with the latest public builder."
                ),
                help_url="https://www.trinityaccord.org/record-chain-field-helper/#CLIENT_SUPPLIED_UNSIGNED_PROJECTION_FIELD",
                retry_allowed=True,
            ))
    return diagnostics


async def _load_json_text_or_none(path_text: str) -> dict[str, Any] | None:
    text = await get_file_text(path_text)
    if text is None:
        return None
    return json.loads(text)


def _existing_receipt_matches_current(
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


async def _find_existing_matching_receipt(
    *,
    candidate_receipt_paths: list[str],
    submission_sha256: str,
    stored_submission_sha256: str,
) -> tuple[str, dict[str, Any]] | None:
    for candidate_path in candidate_receipt_paths:
        existing_sha = await get_file_sha(candidate_path)
        if existing_sha is None:
            continue
        existing_receipt = await _load_json_text_or_none(candidate_path)
        if not existing_receipt:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "RECEIPT_PATH_CONFLICT",
                    "message": "Receipt path exists but could not be read as JSON. Refusing to overwrite immutable intake artifact.",
                    "receipt_path": candidate_path,
                },
            )
        if _existing_receipt_matches_current(
            existing_receipt=existing_receipt,
            submission_sha256=submission_sha256,
            stored_submission_sha256=stored_submission_sha256,
            receipt_path=candidate_path,
        ):
            return candidate_path, existing_receipt
        raise HTTPException(
            status_code=409,
            detail={
                "code": "RECEIPT_PATH_CONFLICT",
                "message": "Receipt path already exists but does not bind to this exact submission. Refusing to overwrite immutable intake artifact.",
                "receipt_path": candidate_path,
            },
        )
    return None


def _diagnostics_from_errors(errors: list[str | Diagnostic]) -> list[Diagnostic]:
    """Convert a list of error strings or Diagnostic objects into Diagnostic objects.

    If items are already Diagnostic objects, pass them through directly.
    """
    diagnostics: list[Diagnostic] = []
    for i, item in enumerate(errors):
        if isinstance(item, Diagnostic):
            diagnostics.append(item)
        else:
            code = f"VALIDATION_{i:03d}"
            diagnostics.append(Diagnostic(code=code, severity="error", message=str(item)))
    return diagnostics


def _build_agent_recovery(diagnostics: list[Diagnostic]) -> AgentRecovery:
    """Build agent recovery guidance from diagnostics."""
    error_codes = [d.code for d in diagnostics if d.severity == "error"]
    has_security = any(c.startswith("SECURITY") for c in error_codes)
    has_privacy = any("PRIVACY" in c for c in error_codes)

    if has_security or has_privacy:
        return AgentRecovery(
            should_retry=False,
            recommended_next_step="This submission contains security or privacy violations that cannot be retried automatically. A human must review and correct the submission.",
            helper_url=f"{_GATEWAY_BASE_URL}/docs/security-violations" if _GATEWAY_BASE_URL else None,
            human_readable_helper_url="Trinity Accord Security Documentation",
            requires_human_attention=True,
        )

    # Check if all diagnostics are retryable
    all_retryable = all(d.retry_allowed for d in diagnostics if d.severity == "error")

    if all_retryable:
        codes_summary = ", ".join(sorted(set(error_codes)))
        return AgentRecovery(
            should_retry=True,
            recommended_next_step=f"Fix the validation errors ({codes_summary}) and resubmit. Each diagnostic includes a suggested_fix and help_url.",
            helper_url=f"{_GATEWAY_BASE_URL}/docs/validation-errors" if _GATEWAY_BASE_URL else None,
            human_readable_helper_url="Trinity Accord Validation Error Reference",
            builder_doctor_command="trinity-doctor validate",
            builder_error_help_command=f"trinity-doctor explain {' '.join(error_codes[:5])}",
            requires_human_attention=False,
        )

    return AgentRecovery(
        should_retry=True,
        recommended_next_step="Review each diagnostic for its suggested_fix, correct the submission, and retry.",
        helper_url=f"{_GATEWAY_BASE_URL}/docs/validation-errors" if _GATEWAY_BASE_URL else None,
        human_readable_helper_url="Trinity Accord Validation Error Reference",
        requires_human_attention=False,
    )


def _has_linked_guardian_request(draft: dict[str, Any]) -> bool:
    """Check if the draft includes a complete linked Guardian application request."""
    linked = draft.get("optional_linked_guardian_application_request")
    if not isinstance(linked, dict):
        return False
    return linked.get("does_participant_request_guardian_application_with_this_record") is True


_FORMAL_RECORD_TYPES = {
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "guardian_key_rotation",
    "propagation",
    "correction",
    "classification_update",
}


def _normalize_public_v2_draft_for_pending(draft: dict[str, Any]) -> dict[str, Any]:
    """Add compatibility projections (actor_identity, boundary) for append path."""
    normalized = dict(draft)

    if not normalized.get("actor_identity") and isinstance(
        normalized.get("submitting_participant_identity"), dict
    ):
        p = normalized["submitting_participant_identity"]
        normalized["actor_identity"] = {
            "label": p.get("participant_public_display_label") or "Unknown Participant",
            "provider": (
                p.get("participant_provider_or_platform")
                or p.get("participant_model_or_runtime")
                or "Unknown Runtime"
            ),
            "id": (
                p.get("participant_self_declared_identifier")
                or p.get("participant_public_key_sha256")
                or None
            ),
        }

    if not normalized.get("boundary") and isinstance(
        normalized.get("non_authority_boundary_acknowledgement"), dict
    ):
        b = normalized["non_authority_boundary_acknowledgement"]
        normalized["boundary"] = {
            "not_authority": b.get("not_authority") is True,
            "not_governance": b.get("not_governance") is True,
            "not_attestation": b.get("not_attestation") is True,
            "not_successor_reception": b.get("not_successor_reception") is True,
            "not_amendment": b.get("not_amendment") is True,
            "bitcoin_originals_prevail": b.get("bitcoin_originals_prevail") is True,
        }

    return normalized


async def _best_effort_delete_created_files(created_files: list[tuple[str, str]], receipt_id: str) -> None:
    """Best-effort rollback for files created during a failed intake transaction."""
    for path, sha in reversed(created_files):
        try:
            await delete_file(path, f"rollback failed intake {receipt_id}: delete {path}", sha=sha)
            logger.info("Rolled back created intake file %s for %s", path, receipt_id)
        except Exception as cleanup_exc:
            logger.error("Failed to roll back %s for %s: %s", path, receipt_id, cleanup_exc)


# ---------------------------------------------------------------------------
# BLOCKER 1 helpers: Idempotency index fail-closed
# ---------------------------------------------------------------------------

def _idempotency_index_path(submission_sha256: str) -> str:
    return f"record-chain/intake/by-submission-sha256/{submission_sha256}.json"


def _build_idempotency_index_data(
    *,
    submission_sha256: str,
    stored_submission_sha256: str,
    receipt_id: str,
    receipt_path: str,
    pending_file_path: str,
    intake_submission_path: str,
    record_type: str,
    now: datetime,
) -> dict[str, Any]:
    return {
        "schema": "trinityaccord.record-chain-intake-idempotency.v1",
        "submission_sha256": submission_sha256,
        "stored_submission_sha256": stored_submission_sha256,
        "receipt_id": receipt_id,
        "receipt_path": receipt_path,
        "pending_file_path": pending_file_path,
        "intake_submission_path": intake_submission_path,
        "record_type": record_type,
        "created_at": now.isoformat().replace("+00:00", "Z"),
    }


async def _read_idempotency_index(submission_sha256: str) -> dict[str, Any] | None:
    path = _idempotency_index_path(submission_sha256)
    text = await get_file_text(path)
    if text is None:
        return None
    data = json.loads(text)
    if data.get("submission_sha256") != submission_sha256:
        raise RuntimeError(f"Idempotency index hash mismatch at {path}")
    return data


async def _submit_response_from_idempotency_index(
    *,
    index: dict[str, Any],
    record_type: str,
    submission_sha256: str,
    received_raw_body_sha256: str,
    body: dict[str, Any],
) -> SubmitResponse:
    receipt_path = index.get("receipt_path", "")
    if not isinstance(receipt_path, str) or not receipt_path:
        raise RuntimeError("Idempotency index is missing receipt_path")

    receipt_text = await get_file_text(receipt_path)
    if not receipt_text:
        raise RuntimeError(f"Idempotency receipt is missing: {receipt_path}")

    receipt_data: dict[str, Any] = json.loads(receipt_text)
    if not isinstance(receipt_data, dict):
        raise RuntimeError(f"Idempotency receipt is not a JSON object: {receipt_path}")

    # Verify receipt hash integrity
    # Fail-closed: receipt MUST have receipt_sha256
    if not receipt_data.get("receipt_sha256"):
        raise RuntimeError(f"IDEMPOTENCY_RECEIPT_MISSING_HASH: receipt has no receipt_sha256 at {receipt_path}")
    hash_ok, hash_err = verify_receipt_sha256(receipt_data)
    if not hash_ok:
        raise RuntimeError(f"IDEMPOTENCY_RECEIPT_HASH_INVALID: {hash_err} at {receipt_path}")

    receipt_id = (
        receipt_data.get("server_receipt_id")
        or receipt_data.get("receipt_id")
        or index.get("receipt_id")
        or ""
    )
    if not receipt_id:
        raise RuntimeError(f"Idempotency receipt has no receipt id: {receipt_path}")

    if index.get("receipt_id") and index.get("receipt_id") != receipt_id:
        raise RuntimeError(
            f"Idempotency receipt_id mismatch: index={index.get('receipt_id')} receipt={receipt_id}"
        )

    return SubmitResponse(
        accepted=True,
        submitted=True,
        receipt_id=receipt_id,
        record_type=index.get("record_type", record_type),
        submission_sha256=submission_sha256,
        received_raw_body_sha256=received_raw_body_sha256,
        pending_file_path=index.get("pending_file_path", ""),
        intake_submission_path=index.get("intake_submission_path", ""),
        receipt_path=receipt_path,
        server_created_at=receipt_data.get("accepted_at", index.get("created_at", "")),
        append_status="duplicate_existing_submission_returned",
        receipt=receipt_data,
        diagnostics=[],
        warnings=["Duplicate submission: existing idempotency index found; original receipt returned."],
        boundary=_build_submit_boundary(body),
        created_pending_records=[
            p for p in [index.get("pending_file_path", "")]
            if isinstance(p, str) and p
        ],
    )


# ---------------------------------------------------------------------------
# BLOCKER 2 helper: Streaming body overflow 413 payload
# ---------------------------------------------------------------------------

def _request_body_too_large_payload(size: int, *, preflight: bool) -> dict[str, Any]:
    """Extended 413 payload with route-specific fields for preflight/submit."""
    payload = _body_too_large_diagnostic_payload(size)
    payload["received_raw_body_sha256"] = ""
    if preflight:
        payload.update({
            "preflight": True,
            "route_detected": "unknown",
            "record_type": "",
            "submission_sha256": "",
            "warnings": [],
            "gateway_runtime": _build_gateway_runtime(),
            "gateway_schema": _GATEWAY_SCHEMA,
        })
    else:
        payload.update({
            "submitted": False,
        })
    return payload


# ---------------------------------------------------------------------------
# Health & readiness
# ---------------------------------------------------------------------------

@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"ok": True, "service": "record-chain-intake-gateway"}


@app.head("/healthz")
async def healthz_head() -> Response:
    return Response(status_code=200)


@app.get("/record-chain/readiness", response_model=ReadinessResponse)
async def readiness(response: Response) -> ReadinessResponse:
    info = get_runtime_info()

    repo_configured = bool(os.environ.get("TRINITY_REPO_FULL_NAME"))
    branch_configured = bool(os.environ.get("TRINITY_TARGET_BRANCH"))
    token_configured = bool(os.environ.get("TRINITY_GITHUB_TOKEN"))

    write_requires_github = info["write_mode"] == "github_contents_pending"
    submit_ready = (
        repo_configured
        and branch_configured
        and (token_configured if write_requires_github else True)
    )

    if not submit_ready:
        response.status_code = 503

    return ReadinessResponse(
        ok=submit_ready,
        preflight_ready=True,
        submit_ready=submit_ready,
        service=info["service"],
        version=info["version"],
        repo_configured=repo_configured,
        branch_configured=branch_configured,
        token_configured=token_configured,
        write_mode=info["write_mode"],
        max_submission_bytes=info["max_submission_bytes"],
        oath_gate_mode=os.environ.get("TRINITY_OATH_GATE_MODE", "required"),
    )


# ---------------------------------------------------------------------------
# Preflight — validate only
# ---------------------------------------------------------------------------

@app.post("/record-chain/preflight", response_model=PreflightResponse)
async def preflight(request: Request) -> PreflightResponse | JSONResponse:
    # Part G: streaming body-size limit
    try:
        raw_body = await _read_limited_body(request)
    except RequestBodyTooLarge as exc:
        return JSONResponse(
            status_code=413,
            content=_request_body_too_large_payload(exc.size, preflight=True),
        )

    received_raw_body_sha256 = _compute_raw_body_sha256(raw_body)

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        diag = Diagnostic(
            code="INVALID_JSON",
            severity="error",
            message=f"Invalid JSON: {exc}",
        )
        return PreflightResponse(
            accepted=False,
            preflight=True,
            route_detected="unknown",
            record_type="",
            submission_sha256="",
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[diag],
            gateway_runtime=_build_gateway_runtime(),
            gateway_schema=_GATEWAY_SCHEMA,
            boundary=_build_preflight_boundary({}),
            agent_recovery=_build_agent_recovery([diag]),
        )

    if not isinstance(body, dict):
        diag = Diagnostic(
            code="INVALID_TYPE",
            severity="error",
            message="Request body must be a JSON object",
        )
        return PreflightResponse(
            accepted=False,
            preflight=True,
            route_detected="unknown",
            record_type="",
            submission_sha256="",
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[diag],
            gateway_runtime=_build_gateway_runtime(),
            gateway_schema=_GATEWAY_SCHEMA,
            boundary=_build_preflight_boundary({}),
            agent_recovery=_build_agent_recovery([diag]),
        )

    # validate_submission now returns list[Diagnostic] directly
    diagnostics = validate_submission(body)
    diagnostics.extend(_client_projection_diagnostics(body))

    # Authorship verification is performed inside validate_submission().
    # Do not run a second verifier here; duplicate verifiers can produce conflicting diagnostics.

    route = detect_route(body)
    submission_sha256 = sha256_canonical_json(body)
    record_type = body.get("record_type") or ""
    if isinstance(record_type, str):
        record_type = record_type.strip().lower()

    accepted = len(diagnostics) == 0
    agent_recovery = None if accepted else _build_agent_recovery(diagnostics)

    return PreflightResponse(
        accepted=accepted,
        preflight=True,
        route_detected=route,
        record_type=record_type,
        submission_sha256=submission_sha256,
        received_raw_body_sha256=received_raw_body_sha256,
        diagnostics=diagnostics,
        warnings=[],
        gateway_runtime=_build_gateway_runtime(),
        gateway_schema=_GATEWAY_SCHEMA,
        boundary=_build_preflight_boundary(body),
        agent_recovery=agent_recovery,
    )


# ---------------------------------------------------------------------------
# Submit — validate + persist (triple file write + optional linked Guardian)
# ---------------------------------------------------------------------------

@app.post("/record-chain/submit", response_model=SubmitResponse)
async def submit(request: Request) -> SubmitResponse | JSONResponse:
    # Part G: streaming body-size limit
    try:
        raw_body = await _read_limited_body(request)
    except RequestBodyTooLarge as exc:
        return JSONResponse(
            status_code=413,
            content=_request_body_too_large_payload(exc.size, preflight=False),
        )

    received_raw_body_sha256 = _compute_raw_body_sha256(raw_body)

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        return SubmitResponse(
            accepted=False,
            submitted=False,
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[Diagnostic(
                code="INVALID_JSON",
                severity="error",
                message=f"Invalid JSON: {exc}",
            )],
            boundary=_build_submit_boundary({}),
        )

    if not isinstance(body, dict):
        return SubmitResponse(
            accepted=False,
            submitted=False,
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[Diagnostic(
                code="INVALID_TYPE",
                severity="error",
                message="Request body must be a JSON object",
            )],
            boundary=_build_submit_boundary({}),
        )

    # --- validate (now returns list[Diagnostic] directly) ---
    diagnostics = validate_submission(body)
    diagnostics.extend(_client_projection_diagnostics(body))
    if diagnostics:
        return SubmitResponse(
            accepted=False,
            submitted=False,
            received_raw_body_sha256=received_raw_body_sha256,
            submission_sha256=sha256_canonical_json(body),
            diagnostics=diagnostics,
            boundary=_build_submit_boundary(body),
        )

    # --- Part B: global idempotency check (fail-closed, before rate limit) ---
    original_submission_sha256 = sha256_canonical_json(body)
    record_type = detect_route(body)

    existing_idx: dict[str, Any] | None = None
    try:
        existing_idx = await _read_idempotency_index(original_submission_sha256)
    except Exception as exc:
        logger.warning(
            "Idempotency index lookup failed for %s: %s",
            original_submission_sha256[:16],
            exc,
        )
        return SubmitResponse(
            accepted=False,
            submitted=False,
            record_type=record_type,
            submission_sha256=original_submission_sha256,
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[Diagnostic(
                code="IDEMPOTENCY_INDEX_LOOKUP_FAILED",
                severity="error",
                field="record-chain/intake/by-submission-sha256",
                message=f"Could not safely check global idempotency index: {exc}",
                meaning="The gateway must not risk accepting a duplicate when the idempotency index cannot be checked safely.",
                suggested_fix="Retry later. If a prior submission succeeded, the gateway should return its existing receipt once idempotency storage is readable.",
                retry_allowed=True,
            )],
            boundary=_build_submit_boundary(body),
        )

    if existing_idx is not None:
        try:
            return await _submit_response_from_idempotency_index(
                index=existing_idx,
                record_type=record_type,
                submission_sha256=original_submission_sha256,
                received_raw_body_sha256=received_raw_body_sha256,
                body=body,
            )
        except Exception as exc:
            logger.warning(
                "Existing idempotency index could not be resolved for %s: %s",
                original_submission_sha256[:16],
                exc,
            )
            return SubmitResponse(
                accepted=False,
                submitted=False,
                record_type=record_type,
                submission_sha256=original_submission_sha256,
                received_raw_body_sha256=received_raw_body_sha256,
                diagnostics=[Diagnostic(
                    code="IDEMPOTENCY_INDEX_LOOKUP_FAILED",
                    severity="error",
                    field="record-chain/intake/by-submission-sha256",
                    message=f"Existing idempotency index could not be resolved to a valid receipt: {exc}",
                    meaning="The gateway found duplicate-submission state but could not safely return the original receipt.",
                    suggested_fix="Retry later or ask an operator to inspect the idempotency index and receipt path.",
                    retry_allowed=True,
                )],
                boundary=_build_submit_boundary(body),
            )

    # --- rate limit check (only on submit, not preflight) ---
    rate_limit_result = check_rate_limit(body)
    if rate_limit_result is not None:
        rate_diags = [
            Diagnostic(
                code=d["code"],
                severity=d["severity"],
                field=d.get("field", ""),
                message=d["message"],
                meaning=d.get("meaning"),
                suggested_fix=d.get("suggested_fix"),
                help_url=d.get("help_url"),
                retry_allowed=d.get("retry_allowed", True),
            )
            for d in rate_limit_result.get("diagnostics", [])
        ]
        payload = SubmitResponse(
            accepted=False,
            submitted=False,
            received_raw_body_sha256=received_raw_body_sha256,
            submission_sha256=sha256_canonical_json(body),
            diagnostics=rate_diags,
            boundary=_build_submit_boundary(body),
        ).model_dump(mode="json")
        payload["retry_after_seconds"] = rate_limit_result.get("retry_after_seconds")
        payload["rate_limit"] = rate_limit_result.get("rate_limit")
        return JSONResponse(status_code=429, content=payload)

    # --- compute hashes ---
    submission_sha256 = sha256_canonical_json(body)
    record_type = detect_route(body)

    # --- extract draft ---
    draft: dict[str, Any] = extract_record_draft(body) or {}

    # --- authorship verification is performed inside validate_submission() ---
    # At this point the proof is trusted as validation-passed input.
    proof = body.get("authorship_proof") or body.get("proof")
    authorship_verified = isinstance(proof, dict)

    # --- redact transient oath readback before persistence ---
    from apps.record_chain_intake_gateway.gateway.validation import redact_transient_oath_readback
    original_submission_sha256 = sha256_canonical_json(body)
    body = redact_transient_oath_readback(body)
    stored_submission_sha256 = sha256_canonical_json(body)
    # Re-extract draft after redaction
    draft = extract_record_draft(body) or {}

    # --- check for linked Guardian request ---
    has_linked_guardian = _has_linked_guardian_request(draft)
    if has_linked_guardian:
        return SubmitResponse(
            accepted=False,
            submitted=False,
            record_type=record_type,
            submission_sha256=submission_sha256,
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[Diagnostic(
                code="LINKED_GUARDIAN_AUTO_CREATION_DISABLED",
                severity="error",
                field="record_draft.optional_linked_guardian_application_request",
                message="Linked guardian auto-creation is disabled. Submit a separate signed guardian_application record instead.",
                meaning="The gateway must not copy an authorship proof from one draft onto a newly constructed guardian_application draft.",
                suggested_fix="Build and sign a standalone guardian_application submission.",
                retry_allowed=True,
            )],
            boundary=_build_submit_boundary(body),
        )

    # --- build receipt (prepare all paths FIRST, receipt is immutable after creation) ---
    now = datetime.now(timezone.utc)
    receipt_id_local = make_receipt_id(submission_sha256, now)
    legacy_receipt_id_local = make_legacy_receipt_id(submission_sha256, now)
    date_prefix = now.strftime("%Y/%m")

    intake_submission_path = f"record-chain/intake/submissions/{date_prefix}/{receipt_id_local}.submission.json"
    receipt_path = f"record-chain/intake/receipts/{date_prefix}/{receipt_id_local}.receipt.json"
    pending_file_path = f"record-chain/pending/{receipt_id_local}.{record_type}.pending.json"

    legacy_intake_submission_path = f"record-chain/intake/submissions/{date_prefix}/{legacy_receipt_id_local}.submission.json"
    legacy_receipt_path = f"record-chain/intake/receipts/{date_prefix}/{legacy_receipt_id_local}.receipt.json"
    legacy_pending_file_path = f"record-chain/pending/{legacy_receipt_id_local}.{record_type}.pending.json"

    # Track all created pending file paths
    created_pending_records: list[str] = [pending_file_path]

    # Extract oath verification summary for receipt (no raw readback)
    oath_summary = _extract_oath_verification_summary(draft)

    receipt_data = make_receipt(
        submission=body,
        submission_sha256=submission_sha256,
        original_submission_sha256=original_submission_sha256,
        stored_submission_sha256=stored_submission_sha256,
        record_type=record_type,
        received_raw_body_sha256=received_raw_body_sha256,
        intake_submission_path=intake_submission_path,
        pending_file_path=pending_file_path,
        receipt_path=receipt_path,
        now=now,
        oath_verification_summary=oath_summary,
    )
    receipt_id = receipt_data["server_receipt_id"]

    # --- prepare file contents ---
    submission_content = canonical_dumps(body)

    # Pending file = signed pre-append record_draft only (not outer submission).
    # Strip any server projection/append-assigned fields defensively. New clients
    # are rejected if they supply these fields, but this sanitizer prevents stale
    # runtime paths from persisting unsigned projections.
    pending_content_dict = strip_unsigned_projection_fields(draft)
    if authorship_verified and proof:
        pending_content_dict["authorship_proof"] = proof
    pending_content = canonical_dumps(pending_content_dict)

    receipt_content = canonical_dumps(receipt_data)

    # --- persist to GitHub ---
    # Safe order:
    #   1. submission
    #   2. receipt
    #   3. idempotency index
    #   4. pending LAST
    #
    # The pending file is the append-eligibility marker. It must not be visible
    # until durable intake state exists and is globally idempotent.
    commit_sha: str | None = None
    created_files_for_rollback: list[tuple[str, str]] = []
    append_status = "pending"
    warnings: list[str] = []

    if _WRITE_MODE == "github_contents_pending":
        _check_config()
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
                        p for p in [existing_receipt.get("pending_file_path", "")]
                        if isinstance(p, str) and p
                    ],
                )

            existing_sub_sha = await get_file_sha(intake_submission_path)
            existing_pending_sha = await get_file_sha(pending_file_path)
            legacy_sub_sha = await get_file_sha(legacy_intake_submission_path)
            legacy_pending_sha = await get_file_sha(legacy_pending_file_path)

            if existing_sub_sha is not None or existing_pending_sha is not None:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "INTAKE_ARTIFACT_PATH_CONFLICT",
                        "message": "Submission or pending path already exists without a matching immutable receipt. Refusing to overwrite.",
                        "submission_path_exists": existing_sub_sha is not None,
                        "pending_path_exists": existing_pending_sha is not None,
                        "submission_path": intake_submission_path,
                        "pending_file_path": pending_file_path,
                    },
                )

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

            # Write 1: intake submission (create only)
            result1 = await put_file(
                intake_submission_path,
                submission_content,
                f"intake: submission {receipt_id}",
                sha=None,
            )
            if result1.get("content", {}).get("sha"):
                created_files_for_rollback.append((intake_submission_path, result1["content"]["sha"]))
            logger.info("Wrote submission %s", intake_submission_path)

            # Write 2: receipt (create only)
            # The receipt must exist before pending becomes visible to append workers.
            result_receipt = await put_file(
                receipt_path,
                receipt_content,
                f"intake: receipt {receipt_id}",
                sha=None,
            )
            if result_receipt.get("content", {}).get("sha"):
                created_files_for_rollback.append((receipt_path, result_receipt["content"]["sha"]))
            logger.info("Wrote receipt %s", receipt_path)

            commit_sha = result_receipt.get("commit", {}).get("sha")

            # Write 3: global idempotency index (create only, fail-closed)
            idempotency_path = _idempotency_index_path(original_submission_sha256)
            idempotency_index_data = _build_idempotency_index_data(
                submission_sha256=original_submission_sha256,
                stored_submission_sha256=stored_submission_sha256,
                receipt_id=receipt_id,
                receipt_path=receipt_path,
                pending_file_path=pending_file_path,
                intake_submission_path=intake_submission_path,
                record_type=record_type,
                now=now,
            )

            try:
                result_idx = await put_file(
                    idempotency_path,
                    canonical_dumps(idempotency_index_data),
                    f"intake: idempotency index {original_submission_sha256[:16]}",
                    sha=None,
                )
                if result_idx.get("content", {}).get("sha"):
                    created_files_for_rollback.append((idempotency_path, result_idx["content"]["sha"]))
                logger.info("Wrote idempotency index %s", idempotency_path)

            except Exception as idemp_exc:
                logger.warning(
                    "Idempotency index write failed for %s: %s",
                    original_submission_sha256[:16],
                    idemp_exc,
                )

                existing_idx: dict[str, Any] | None = None
                try:
                    existing_idx = await _read_idempotency_index(original_submission_sha256)
                except Exception as read_exc:
                    logger.warning(
                        "Could not read existing idempotency index for %s after write failure: %s",
                        original_submission_sha256[:16],
                        read_exc,
                    )

                await _best_effort_delete_created_files(created_files_for_rollback, receipt_id)

                if existing_idx is not None:
                    try:
                        return await _submit_response_from_idempotency_index(
                            index=existing_idx,
                            record_type=record_type,
                            submission_sha256=original_submission_sha256,
                            received_raw_body_sha256=received_raw_body_sha256,
                            body=body,
                        )
                    except Exception as response_exc:
                        logger.error(
                            "Existing idempotency index could not be converted into response for %s: %s",
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
                        code="IDEMPOTENCY_INDEX_PERSIST_FAILED",
                        severity="error",
                        field="record-chain/intake/by-submission-sha256",
                        message=f"Persisted intake artifacts were rolled back because idempotency index creation failed: {idemp_exc}",
                        meaning="The gateway must not accept an intake without its global duplicate-submission index.",
                        suggested_fix="Retry the same submission later; if the original request succeeded concurrently, the gateway will return the existing receipt.",
                        retry_allowed=True,
                    )],
                    boundary=_build_submit_boundary(body),
                )

            # Write 4: pending file (create only) — LAST.
            # This file is the append-eligibility marker. It must not exist until
            # submission, receipt, and idempotency index are durable.
            result_pending = await put_file(
                pending_file_path,
                pending_content,
                f"intake: pending {receipt_id} ({record_type})",
                sha=None,
            )
            if result_pending.get("content", {}).get("sha"):
                created_files_for_rollback.append((pending_file_path, result_pending["content"]["sha"]))
            logger.info("Wrote pending %s", pending_file_path)

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
                        f"Append workflow dispatch failed after durable intake writes: {dispatch_exc}. "
                        "The record remains pending and can be picked up by push/scheduled/manual append."
                    )
                    warnings.append(warning)
                    logger.warning("Append dispatch failed for %s: %s", receipt_id, dispatch_exc)

        except Exception as exc:
            logger.error("Failed to persist %s: %s", receipt_id, exc)
            await _best_effort_delete_created_files(created_files_for_rollback, receipt_id)
            return SubmitResponse(
                accepted=False,
                submitted=False,
                record_type=record_type,
                submission_sha256=submission_sha256,
                received_raw_body_sha256=received_raw_body_sha256,
                diagnostics=[Diagnostic(
                    code="PERSIST_FAILED",
                    severity="error",
                    message=f"Persist failed: {exc}",
                )],
                boundary=_build_submit_boundary(body),
            )
    else:
        logger.info("Dry-run mode — skipping persist for %s", receipt_id)
        append_status = "dry_run"

    # --- store receipt in memory (NOT mutated — same bytes as persisted) ---
    _receipt_store[receipt_id] = receipt_data

    return SubmitResponse(
        accepted=True,
        submitted=True,
        receipt_id=receipt_id,
        record_type=record_type,
        submission_sha256=submission_sha256,
        received_raw_body_sha256=received_raw_body_sha256,
        pending_file_path=pending_file_path,
        intake_submission_path=intake_submission_path,
        receipt_path=receipt_path,
        server_created_at=receipt_data["accepted_at"],
        append_status=append_status,
        receipt_commit_sha=commit_sha,
        receipt=receipt_data,
        diagnostics=[],
        warnings=warnings,
        boundary=_build_submit_boundary(body),
        created_pending_records=created_pending_records,
    )


# ---------------------------------------------------------------------------
# Receipt retrieval
# ---------------------------------------------------------------------------

def _receipt_path_from_id(receipt_id: str) -> str:
    """Parse receipt ID and return the durable storage path.

    Raises HTTPException(400) for invalid format.
    """
    import re

    match = re.fullmatch(r"rcg-(\d{8})-([a-f0-9]{12}|[a-f0-9]{24})", receipt_id)
    if not match:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_RECEIPT_ID_FORMAT",
                "message": f"Invalid receipt ID format: '{receipt_id}'. Expected: rcg-YYYYMMDD-<sha12-or-sha24>",
                "expected": "rcg-YYYYMMDD-<sha12-or-sha24>",
            },
        )

    try:
        dt = datetime.strptime(match.group(1), "%Y%m%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_RECEIPT_ID_DATE",
                "message": f"Invalid date in receipt ID: '{receipt_id}'",
            },
        )

    return f"record-chain/intake/receipts/{dt.year:04d}/{dt.month:02d}/{receipt_id}.receipt.json"


async def _read_receipt_final_status(receipt_id: str) -> dict[str, Any] | None:
    """Read the final append/reject status sidecar for a receipt."""
    path = f"record-chain/receipt-status/{receipt_id}.json"
    text = await get_file_text(path)
    if text is None:
        return None
    status = json.loads(text)
    if status.get("receipt_id") != receipt_id:
        logger.error("receipt-status receipt_id mismatch at %s", path)
        return None
    return status


async def _build_receipt_envelope(
    receipt: dict[str, Any],
    receipt_id: str,
    receipt_path: str,
) -> dict[str, Any]:
    """Build a receipt envelope with immutable receipt and final status."""
    try:
        final_status_data = await _read_receipt_final_status(receipt_id)
    except Exception as exc:
        logger.warning("Failed to read receipt-status for %s: %s", receipt_id, exc)
        final_status_data = None

    if final_status_data:
        append_status = final_status_data.get("append_status", "unknown")
        final_record_id = final_status_data.get("final_record_id")
        final_record_sha256 = final_status_data.get("final_record_sha256")
        rejection_path = final_status_data.get("rejection_path")
        rejection_code = final_status_data.get("rejection_code")
        updated_at = final_status_data.get("updated_at")
    else:
        # No sidecar exists — check if receipt has pending file path
        pending_path = receipt.get("pending_file_path")
        append_status = "pending" if pending_path else "unknown"
        final_record_id = None
        final_record_sha256 = None
        rejection_path = None
        rejection_code = None
        updated_at = None

    return {
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


@app.get("/record-chain/receipt/{receipt_id}")
async def get_receipt(receipt_id: str) -> dict[str, Any]:
    """Retrieve a receipt by ID.

    Receipt ID format: rcg-YYYYMMDD-<sha12-or-sha24>.
    Durable receipt files are the primary source; memory is only a cache.
    """
    receipt_path = _receipt_path_from_id(receipt_id)

    # Try durable store first (primary source)
    backend_error: Exception | None = None
    try:
        text = await get_file_text(receipt_path)
        if text is not None:
            receipt = json.loads(text)
            # Fail-closed: receipt MUST have receipt_sha256
            if not receipt.get("receipt_sha256"):
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "RECEIPT_INTEGRITY_MISSING_HASH",
                        "message": "Receipt is missing receipt_sha256; cannot verify integrity",
                        "receipt_id": receipt_id,
                        "receipt_path": receipt_path,
                    },
                )
            # Verify receipt hash integrity
            hash_ok, hash_err = verify_receipt_sha256(receipt)
            if not hash_ok:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "RECEIPT_HASH_INVALID",
                        "message": f"Receipt hash verification failed: {hash_err}",
                        "receipt_id": receipt_id,
                        "receipt_path": receipt_path,
                    },
                )
            _receipt_store[receipt_id] = receipt  # update cache
            return await _build_receipt_envelope(receipt, receipt_id, receipt_path)
    except HTTPException:
        # Re-raise HTTPExceptions (integrity errors) — do not swallow
        raise
    except Exception as exc:
        backend_error = exc
        logger.warning("Durable receipt lookup failed for %s at %s: %s", receipt_id, receipt_path, exc)

    # Fallback to memory cache — also must verify hash
    cached = _receipt_store.get(receipt_id)
    if cached is not None:
        if not cached.get("receipt_sha256"):
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "RECEIPT_INTEGRITY_MISSING_HASH",
                    "message": "Cached receipt is missing receipt_sha256; cannot verify integrity",
                    "receipt_id": receipt_id,
                },
            )
        hash_ok, hash_err = verify_receipt_sha256(cached)
        if not hash_ok:
            _receipt_store.pop(receipt_id, None)  # evict corrupt cache
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "RECEIPT_HASH_INVALID",
                    "message": f"Cached receipt hash verification failed: {hash_err}",
                    "receipt_id": receipt_id,
                },
            )
        if backend_error is None:
            return await _build_receipt_envelope(cached, receipt_id, receipt_path)
        # Backend errored but we have verified cache — return cache with warning
        out = dict(cached)
        warnings = out.setdefault("warnings", [])
        if isinstance(warnings, list):
            warnings.append({
                "code": "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE",
                "receipt_path": receipt_path,
                "retryable": True,
            })
        return await _build_receipt_envelope(out, receipt_id, receipt_path)

    # No cache, no durable — determine error type
    if backend_error is not None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "RECEIPT_BACKEND_UNAVAILABLE",
                "message": "Receipt durable store lookup failed. Retry later.",
                "receipt_id": receipt_id,
                "receipt_path": receipt_path,
                "retryable": True,
            },
        )

    raise HTTPException(
        status_code=404,
        detail={
            "code": "RECEIPT_NOT_FOUND",
            "message": f"Receipt '{receipt_id}' not found",
            "receipt_id": receipt_id,
            "receipt_path": receipt_path,
            "retryable": False,
        },
    )


# ---------------------------------------------------------------------------
# Retired endpoints
# ---------------------------------------------------------------------------

@app.post("/gateway/preflight")
async def retired_gateway_preflight() -> RetiredResponse:
    return RetiredResponse(
        retired=True,
        message="This endpoint has been retired. Use POST /record-chain/preflight instead.",
        redirect_to="/record-chain/preflight",
    )


@app.post("/agent-submit")
async def retired_agent_submit() -> RetiredResponse:
    return RetiredResponse(
        retired=True,
        message="This endpoint has been retired. Use POST /record-chain/submit instead.",
        redirect_to="/record-chain/submit",
    )
