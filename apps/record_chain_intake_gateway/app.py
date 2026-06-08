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

from apps.record_chain_intake_gateway.gateway.authorship import strip_authorship_for_signing, verify_authorship_proof
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
from apps.record_chain_intake_gateway.gateway.receipts import make_legacy_receipt_id, make_receipt, make_receipt_id
from apps.record_chain_intake_gateway.gateway.runtime import get_runtime_info
from apps.record_chain_intake_gateway.gateway.validation import ALLOWED_RECORD_TYPES, detect_route, validate_submission

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

# Gateway schema info
_GATEWAY_SCHEMA: dict[str, Any] = {
    "version": "1.0.0",
    "accepted_record_types": sorted(ALLOWED_RECORD_TYPES),
    "required_submission_fields": ["record_type", "record_draft", "submission_boundary"],
    "optional_submission_fields": ["authorship_proof", "metadata", "boundary_acknowledgement"],
    "boundary_acknowledgement_fields": 8,
    "context_readiness_path": "record_draft.context_readiness.declared_context_level",
    "oath_gate": {
        "required": True,
        "policy_url": "/api/record-chain-oath-policy.v1.json",
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
# Middleware — body-size enforcement
# ---------------------------------------------------------------------------

@app.middleware("http")
async def enforce_body_size(request: Request, call_next):
    """Reject requests whose Content-Length exceeds the configured maximum."""
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > _MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={
                        "ok": False,
                        "accepted": False,
                        "error": f"Request body too large ({content_length} > {_MAX_BODY_BYTES} bytes)",
                    },
                )
        except ValueError:
            pass
    return await call_next(request)


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


def _authorship_preflight_diagnostic(body: dict[str, Any]) -> Diagnostic | None:
    """Verify authorship proof during preflight if proof is present."""
    draft = body.get("record_draft") or body.get("draft") or {}
    proof = (
        body.get("authorship_proof")
        or body.get("proof")
        or (draft.get("authorship_proof") if isinstance(draft, dict) else None)
    )
    record_type = (
        body.get("record_type")
        or body.get("type")
        or (draft.get("record_type") if isinstance(draft, dict) else "")
    )

    if not isinstance(draft, dict):
        return None

    if record_type in _FORMAL_RECORD_TYPES and isinstance(proof, dict):
        ok, err = verify_authorship_proof(draft, proof)
        if not ok:
            return Diagnostic(
                code="AUTHORSHIP_PROOF_INVALID",
                severity="error",
                field="authorship_proof",
                message=f"Authorship proof verification failed: {err}",
                meaning="The signature or public-key proof does not match the record draft.",
                suggested_fix="Rebuild the submission with the latest builder and the correct authorship key.",
                help_url="https://www.trinityaccord.org/record-chain-field-helper/#AUTHORSHIP_PROOF_INVALID",
                retry_allowed=True,
            )
    return None


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


def _build_linked_guardian_draft(
    draft: dict[str, Any],
    proof: dict[str, Any] | None,
    receipt_id: str,
    submission_sha256: str,
) -> dict[str, Any]:
    """Build a complete guardian_application draft from a linked Guardian request.

    The linked Guardian draft copies/derives submission_oath_verification from the
    originating submission, ensuring guardian_stewardship_v1 is included in oath_modules.
    Raw readback_text is never included.
    """
    linked = draft.get("optional_linked_guardian_application_request", {})

    guardian_content = {
        "requested_guardian_identifier": linked.get("requested_guardian_identifier", ""),
        "guardian_public_key_pem": linked.get("guardian_public_key_pem", ""),
        "guardian_public_key_sha256": linked.get("guardian_public_key_sha256", ""),
        "guardian_stewardship_oath": linked.get("guardian_stewardship_oath", ""),
        "guardian_application_statement": linked.get("guardian_application_statement", ""),
        "guardian_understands_role_is_non_governing": linked.get(
            "guardian_understands_role_is_non_governing"
        )
        is True,
        "guardian_understands_role_is_not_authority": linked.get(
            "guardian_understands_role_is_not_authority"
        )
        is True,
        "guardian_understands_retirement_does_not_delete_history": linked.get(
            "guardian_understands_retirement_does_not_delete_history"
        )
        is True,
    }

    authorization_ctx = draft.get("authorization_context", {})
    if not isinstance(authorization_ctx, dict):
        authorization_ctx = {}

    # Derive submission_oath_verification for linked Guardian
    origin_oath = draft.get("submission_oath_verification")
    linked_oath: dict[str, Any] | None = None
    if isinstance(origin_oath, dict):
        import copy
        linked_oath = copy.deepcopy(origin_oath)
        # Ensure guardian_stewardship_v1 is in oath_modules
        oath_modules = list(linked_oath.get("oath_modules", []))
        if "guardian_stewardship_v1" not in oath_modules:
            oath_modules.append("guardian_stewardship_v1")
        linked_oath["oath_modules"] = oath_modules
        # Mark as linked/derived
        linked_oath["linked_guardian_oath_coverage"] = True
        linked_oath["derived_from_originating_submission"] = True
        linked_oath["originating_receipt_id"] = receipt_id
        linked_oath["originating_submission_sha256"] = submission_sha256
        # Remove any raw readback text if present
        linked_oath.pop("readback_text", None)
        linked_oath.pop("participant_readback_excerpt", None)

    guardian_draft: dict[str, Any] = {
        "schema": draft.get("schema", "trinityaccord.record-chain-entry-draft.v2"),
        "record_type": "guardian_application",
        "submitting_participant_identity": draft.get("submitting_participant_identity", {}),
        "discovery_and_introduction_context": draft.get(
            "discovery_and_introduction_context", {}
        ),
        "decision_autonomy_context": draft.get("decision_autonomy_context", {}),
        "submission_execution_context": draft.get("submission_execution_context", {}),
        "authorization_context": {
            **authorization_ctx,
            "authorization_scope": "apply_for_guardian",
        },
        "context_readiness": draft.get("context_readiness", {}),
        "non_authority_boundary_acknowledgement": draft.get(
            "non_authority_boundary_acknowledgement", {}
        ),
        "guardian_application_content": guardian_content,
        # Compatibility fields for current append/index consumers
        "requested_guardian_identifier": guardian_content["requested_guardian_identifier"],
        "guardian_public_key_pem": guardian_content["guardian_public_key_pem"],
        "guardian_public_key_sha256": guardian_content["guardian_public_key_sha256"],
        "guardian_stewardship_oath": guardian_content["guardian_stewardship_oath"],
        "guardian_understands_role_is_non_governing": guardian_content[
            "guardian_understands_role_is_non_governing"
        ],
        "guardian_understands_role_is_not_authority": guardian_content[
            "guardian_understands_role_is_not_authority"
        ],
        "guardian_understands_retirement_does_not_delete_history": guardian_content[
            "guardian_understands_retirement_does_not_delete_history"
        ],
        "linked_origin_record": {
            "originating_submission_sha256": submission_sha256,
            "originating_record_type": draft.get("record_type"),
            "originating_receipt_id": receipt_id,
            "relationship": "guardian_application_requested_during_primary_record_submission",
        },
        "created_as_linked_record": True,
    }

    # Add derived oath verification (no raw readback)
    if linked_oath is not None:
        guardian_draft["submission_oath_verification"] = linked_oath

    # Copy authorship proof so formal linked Guardian application can append
    if proof:
        guardian_draft["authorship_proof"] = proof

    # Add compatibility projections
    guardian_draft = _normalize_public_v2_draft_for_pending(guardian_draft)

    return guardian_draft


async def _best_effort_delete_created_files(created_files: list[tuple[str, str]], receipt_id: str) -> None:
    """Best-effort rollback for files created during a failed intake transaction."""
    for path, sha in reversed(created_files):
        try:
            await delete_file(path, f"rollback failed intake {receipt_id}: delete {path}", sha=sha)
            logger.info("Rolled back created intake file %s for %s", path, receipt_id)
        except Exception as cleanup_exc:
            logger.error("Failed to roll back %s for %s: %s", path, receipt_id, cleanup_exc)


# ---------------------------------------------------------------------------
# Health & readiness
# ---------------------------------------------------------------------------

@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"ok": True, "service": "record-chain-intake-gateway"}


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
async def preflight(request: Request) -> PreflightResponse:
    raw_body = await request.body()
    received_raw_body_sha256 = _compute_raw_body_sha256(raw_body)

    # Check raw body size (handles requests without Content-Length)
    if len(raw_body) > _MAX_BODY_BYTES:
        diag = Diagnostic(
            code="REQUEST_BODY_TOO_LARGE",
            severity="error",
            message=f"Request body too large ({len(raw_body)} > {_MAX_BODY_BYTES} bytes)",
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
            boundary={},
            agent_recovery=_build_agent_recovery([diag]),
        )

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
            boundary={},
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
            boundary={},
            agent_recovery=_build_agent_recovery([diag]),
        )

    # validate_submission now returns list[Diagnostic] directly
    diagnostics = validate_submission(body)

    # P0-4: verify authorship signature during preflight
    if not any(d.code == "MISSING_AUTHORSHIP_PROOF" for d in diagnostics):
        authorship_diag = _authorship_preflight_diagnostic(body)
        if authorship_diag is not None:
            diagnostics.append(authorship_diag)

    route = detect_route(body)
    submission_sha256 = sha256_canonical_json(body)
    record_type = body.get("record_type") or body.get("type") or ""
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
        boundary=_build_boundary(body),
        agent_recovery=agent_recovery,
    )


# ---------------------------------------------------------------------------
# Submit — validate + persist (triple file write + optional linked Guardian)
# ---------------------------------------------------------------------------

@app.post("/record-chain/submit", response_model=SubmitResponse)
async def submit(request: Request) -> SubmitResponse:
    raw_body = await request.body()
    received_raw_body_sha256 = _compute_raw_body_sha256(raw_body)

    # Check raw body size (handles requests without Content-Length)
    if len(raw_body) > _MAX_BODY_BYTES:
        return SubmitResponse(
            accepted=False,
            submitted=False,
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[Diagnostic(
                code="REQUEST_BODY_TOO_LARGE",
                severity="error",
                message=f"Request body too large ({len(raw_body)} > {_MAX_BODY_BYTES} bytes)",
            )],
            boundary={},
        )

    _check_config()

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
            boundary={},
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
            boundary={},
        )

    # --- validate (now returns list[Diagnostic] directly) ---
    diagnostics = validate_submission(body)
    if diagnostics:
        return SubmitResponse(
            accepted=False,
            submitted=False,
            received_raw_body_sha256=received_raw_body_sha256,
            submission_sha256=sha256_canonical_json(body),
            diagnostics=diagnostics,
            boundary=_build_boundary(body),
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
        return SubmitResponse(
            accepted=False,
            submitted=False,
            received_raw_body_sha256=received_raw_body_sha256,
            submission_sha256=sha256_canonical_json(body),
            diagnostics=rate_diags,
            boundary=_build_boundary(body),
        )

    # --- compute hashes ---
    submission_sha256 = sha256_canonical_json(body)
    record_type = detect_route(body)

    # --- extract draft ---
    draft: dict[str, Any] = body.get("record_draft") or body.get("draft") or {}

    # --- authorship verification (if proof supplied) ---
    proof = body.get("authorship_proof") or body.get("proof")
    authorship_verified = False
    authorship_error: str | None = None

    if proof and isinstance(proof, dict):
        ok, err = verify_authorship_proof(draft, proof)
        if not ok:
            authorship_error = f"Authorship verification failed: {err}"
            return SubmitResponse(
                accepted=False,
                submitted=False,
                record_type=record_type,
                submission_sha256=submission_sha256,
                received_raw_body_sha256=received_raw_body_sha256,
                diagnostics=[Diagnostic(
                    code="AUTHORSHIP_FAILED",
                    severity="error",
                    message=authorship_error,
                )],
                boundary=_build_boundary(body),
            )
        authorship_verified = True

    # --- redact transient oath readback before persistence ---
    from apps.record_chain_intake_gateway.gateway.validation import redact_transient_oath_readback
    original_submission_sha256 = sha256_canonical_json(body)
    body = redact_transient_oath_readback(body)
    stored_submission_sha256 = sha256_canonical_json(body)
    # Re-extract draft after redaction
    draft = body.get("record_draft") or body.get("draft") or {}

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
            boundary=_build_boundary(body),
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

    # Pending file = normalized record_draft only (not outer submission)
    # Include authorship_proof if verified
    pending_content_dict = _normalize_public_v2_draft_for_pending(dict(draft))
    if authorship_verified and proof:
        pending_content_dict["authorship_proof"] = proof
    pending_content = canonical_dumps(pending_content_dict)

    receipt_content = canonical_dumps(receipt_data)

    # --- persist to GitHub (write order: submission → pending → linked guardian → receipt LAST) ---
    # receipt_data is NOT mutated after creation; commit_sha is returned at response envelope level
    commit_sha: str | None = None
    created_files_for_rollback: list[tuple[str, str]] = []
    append_status = "pending"
    warnings: list[str] = []

    if _WRITE_MODE == "github_contents_pending":
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
                    boundary=_build_boundary(body),
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

            # Write 2: pending file (create only)
            result2 = await put_file(
                pending_file_path,
                pending_content,
                f"intake: pending {receipt_id} ({record_type})",
                sha=None,
            )
            if result2.get("content", {}).get("sha"):
                created_files_for_rollback.append((pending_file_path, result2["content"]["sha"]))
            logger.info("Wrote pending %s", pending_file_path)

            # Write 3: receipt (LAST — create only)
            result4 = await put_file(
                receipt_path,
                receipt_content,
                f"intake: receipt {receipt_id}",
                sha=None,
            )
            if result4.get("content", {}).get("sha"):
                created_files_for_rollback.append((receipt_path, result4["content"]["sha"]))
            logger.info("Wrote receipt %s", receipt_path)

            commit_sha = result4.get("commit", {}).get("sha")

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
                boundary=_build_boundary(body),
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
        boundary=_build_boundary(body),
        created_pending_records=created_pending_records,
    )


# ---------------------------------------------------------------------------
# Receipt retrieval
# ---------------------------------------------------------------------------

@app.get("/record-chain/receipt/{receipt_id}")
async def get_receipt(receipt_id: str) -> dict[str, Any]:
    """Retrieve a receipt by ID. Checks in-memory cache first, then GitHub.

    Receipt ID format: rcg-YYYYMMDD-<sha12-or-sha24>
    The date in the ID determines the storage path directly.
    """
    receipt = _receipt_store.get(receipt_id)
    if receipt is not None:
        return receipt

    # Parse receipt ID to extract date
    import re
    match = re.fullmatch(r"rcg-(\d{8})-([a-f0-9]{12}|[a-f0-9]{24})", receipt_id)
    if not match:
        raise HTTPException(status_code=400, detail=f"Invalid receipt ID format: '{receipt_id}'. Expected: rcg-YYYYMMDD-<sha12-or-sha24>")

    try:
        dt = datetime.strptime(match.group(1), "%Y%m%d")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date in receipt ID: '{receipt_id}'")

    receipt_path = f"record-chain/intake/receipts/{dt.year:04d}/{dt.month:02d}/{receipt_id}.receipt.json"
    try:
        text = await get_file_text(receipt_path)
        if text is not None:
            receipt = json.loads(text)
            _receipt_store[receipt_id] = receipt
            return receipt
    except Exception as exc:
        logger.debug("GitHub lookup for %s at %s failed: %s", receipt_id, receipt_path, exc)

    raise HTTPException(status_code=404, detail=f"Receipt '{receipt_id}' not found")


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
