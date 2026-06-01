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
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from gateway.authorship import strip_authorship_for_signing, verify_authorship_proof
from gateway.canonical import canonical_dumps, sha256_canonical_json
from gateway.github_adapter import get_file_sha, get_file_text, put_file
from gateway.models import (
    Diagnostic,
    ErrorResponse,
    PreflightResponse,
    ReadinessResponse,
    RetiredResponse,
    ServerReceipt,
    SubmitResponse,
)
from gateway.receipts import make_receipt
from gateway.runtime import get_runtime_info
from gateway.validation import ALLOWED_RECORD_TYPES, detect_route, validate_submission

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
_GATEWAY_BASE_URL = os.environ.get("TRINITY_GATEWAY_BASE_URL", "")

# In-memory receipt store (ephemeral; resets on restart)
_receipt_store: dict[str, dict[str, Any]] = {}

# Gateway schema info
_GATEWAY_SCHEMA: dict[str, Any] = {
    "version": "1.0.0",
    "accepted_record_types": sorted(ALLOWED_RECORD_TYPES),
    "required_submission_fields": ["record_type", "record_draft", "boundary_acknowledgement"],
    "optional_submission_fields": ["authorship_proof", "metadata"],
    "boundary_acknowledgement_fields": 6,
    "context_readiness_path": "record_draft.context_readiness.declared_context_level",
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


def _build_boundary(submission: dict[str, Any]) -> dict[str, bool]:
    """Extract boundary acknowledgement as a dict of bools for the response."""
    boundary = submission.get("boundary_acknowledgement", {})
    if isinstance(boundary, dict):
        return {k: bool(v) for k, v in boundary.items()}
    return {}


def _diagnostics_from_errors(errors: list[str], base_code: str = "VALIDATION") -> list[Diagnostic]:
    """Convert a list of error strings into Diagnostic objects."""
    diagnostics: list[Diagnostic] = []
    for i, msg in enumerate(errors):
        code = f"{base_code}_{i:03d}"
        diagnostics.append(Diagnostic(code=code, severity="error", message=msg))
    return diagnostics


# ---------------------------------------------------------------------------
# Health & readiness
# ---------------------------------------------------------------------------

@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"ok": True, "service": "record-chain-intake-gateway"}


@app.get("/record-chain/readiness", response_model=ReadinessResponse)
async def readiness() -> ReadinessResponse:
    info = get_runtime_info()
    return ReadinessResponse(
        ok=True,
        service=info["service"],
        version=info["version"],
        repo_configured=os.environ.get("TRINITY_REPO_FULL_NAME", "") != "",
        branch_configured=os.environ.get("TRINITY_TARGET_BRANCH", "") != "",
        token_configured=os.environ.get("TRINITY_GITHUB_TOKEN", "") != "",
        write_mode=info["write_mode"],
        max_submission_bytes=info["max_submission_bytes"],
    )


# ---------------------------------------------------------------------------
# Preflight — validate only
# ---------------------------------------------------------------------------

@app.post("/record-chain/preflight", response_model=PreflightResponse)
async def preflight(request: Request) -> PreflightResponse:
    raw_body = await request.body()
    received_raw_body_sha256 = _compute_raw_body_sha256(raw_body)

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        return PreflightResponse(
            accepted=False,
            preflight=True,
            route_detected="unknown",
            record_type="",
            submission_sha256="",
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[Diagnostic(
                code="INVALID_JSON",
                severity="error",
                message=f"Invalid JSON: {exc}",
            )],
            gateway_runtime=_build_gateway_runtime(),
            gateway_schema=_GATEWAY_SCHEMA,
            boundary={},
        )

    if not isinstance(body, dict):
        return PreflightResponse(
            accepted=False,
            preflight=True,
            route_detected="unknown",
            record_type="",
            submission_sha256="",
            received_raw_body_sha256=received_raw_body_sha256,
            diagnostics=[Diagnostic(
                code="INVALID_TYPE",
                severity="error",
                message="Request body must be a JSON object",
            )],
            gateway_runtime=_build_gateway_runtime(),
            gateway_schema=_GATEWAY_SCHEMA,
            boundary={},
        )

    errors = validate_submission(body)
    route = detect_route(body)
    submission_sha256 = sha256_canonical_json(body)
    record_type = body.get("record_type") or body.get("type") or ""
    if isinstance(record_type, str):
        record_type = record_type.strip().lower()

    return PreflightResponse(
        accepted=len(errors) == 0,
        preflight=True,
        route_detected=route,
        record_type=record_type,
        submission_sha256=submission_sha256,
        received_raw_body_sha256=received_raw_body_sha256,
        diagnostics=_diagnostics_from_errors(errors) if errors else [],
        warnings=[],
        gateway_runtime=_build_gateway_runtime(),
        gateway_schema=_GATEWAY_SCHEMA,
        boundary=_build_boundary(body),
    )


# ---------------------------------------------------------------------------
# Submit — validate + persist (triple file write)
# ---------------------------------------------------------------------------

@app.post("/record-chain/submit", response_model=SubmitResponse)
async def submit(request: Request) -> SubmitResponse:
    _check_config()

    raw_body = await request.body()
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

    # --- validate ---
    errors = validate_submission(body)
    if errors:
        return SubmitResponse(
            accepted=False,
            submitted=False,
            received_raw_body_sha256=received_raw_body_sha256,
            submission_sha256=sha256_canonical_json(body),
            diagnostics=_diagnostics_from_errors(errors),
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

    # --- build receipt ---
    now = datetime.now(timezone.utc)
    receipt_data = make_receipt(
        submission=body,
        submission_sha256=submission_sha256,
        record_type=record_type,
        received_raw_body_sha256=received_raw_body_sha256,
        now=now,
    )
    receipt_id = receipt_data["server_receipt_id"]
    date_prefix = now.strftime("%Y/%m")

    # --- define file paths ---
    intake_submission_path = f"record-chain/intake/submissions/{date_prefix}/{receipt_id}.submission.json"
    receipt_path = f"record-chain/intake/receipts/{date_prefix}/{receipt_id}.receipt.json"
    pending_file_path = f"record-chain/pending/{receipt_id}.{record_type}.pending.json"

    # --- prepare file contents ---
    submission_content = canonical_dumps(body)

    # Pending file = normalized record_draft only (not outer submission)
    # Include authorship_proof if verified
    pending_content_dict = strip_authorship_for_signing(draft) if not authorship_verified else dict(draft)
    if authorship_verified and proof:
        pending_content_dict["authorship_proof"] = proof
    pending_content = canonical_dumps(pending_content_dict)

    receipt_content = canonical_dumps(receipt_data)

    # --- persist to GitHub (triple file write) ---
    commit_sha: str | None = None

    if _WRITE_MODE == "github_contents_pending":
        try:
            # Write 1: intake submission
            existing_sub_sha = await get_file_sha(intake_submission_path)
            result1 = await put_file(
                intake_submission_path,
                submission_content,
                f"intake: submission {receipt_id}",
                sha=existing_sub_sha,
            )
            logger.info("Wrote submission %s", intake_submission_path)

            # Write 2: receipt
            existing_receipt_sha = await get_file_sha(receipt_path)
            result2 = await put_file(
                receipt_path,
                receipt_content,
                f"intake: receipt {receipt_id}",
                sha=existing_receipt_sha,
            )
            logger.info("Wrote receipt %s", receipt_path)

            # Write 3: pending file
            existing_pending_sha = await get_file_sha(pending_file_path)
            result3 = await put_file(
                pending_file_path,
                pending_content,
                f"intake: pending {receipt_id} ({record_type})",
                sha=existing_pending_sha,
            )
            logger.info("Wrote pending %s", pending_file_path)

            commit_sha = result3.get("commit", {}).get("sha")

        except Exception as exc:
            logger.error("Failed to persist %s: %s", receipt_id, exc)
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

    # --- update receipt with persist info ---
    receipt_data["intake_submission_path"] = intake_submission_path
    receipt_data["pending_file_path"] = pending_file_path
    receipt_data["receipt_path"] = receipt_path
    if commit_sha:
        receipt_data["commit_sha"] = commit_sha

    # Recompute receipt hash with final fields
    receipt_data["receipt_sha256"] = sha256_canonical_json(
        {k: v for k, v in receipt_data.items() if k != "receipt_sha256"}
    )

    # --- store receipt in memory ---
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
        append_status="pending",
        receipt=receipt_data,
        diagnostics=[],
        warnings=[],
        boundary=_build_boundary(body),
    )


# ---------------------------------------------------------------------------
# Receipt retrieval
# ---------------------------------------------------------------------------

@app.get("/record-chain/receipt/{receipt_id}")
async def get_receipt(receipt_id: str) -> dict[str, Any]:
    """Retrieve a receipt by ID. Checks in-memory cache first, then GitHub."""
    receipt = _receipt_store.get(receipt_id)
    if receipt is not None:
        return receipt

    # Try GitHub — check known path patterns
    now = datetime.now(timezone.utc)
    # Try current and recent months
    for delta_months in range(3):
        month = now.month - delta_months
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        date_prefix = f"{year}/{month:02d}"
        receipt_path = f"record-chain/intake/receipts/{date_prefix}/{receipt_id}.receipt.json"
        try:
            text = await get_file_text(receipt_path)
            if text is not None:
                receipt = json.loads(text)
                # Cache for future lookups
                _receipt_store[receipt_id] = receipt
                return receipt
        except Exception as exc:
            logger.debug("GitHub lookup for %s at %s failed: %s", receipt_id, receipt_path, exc)
            continue

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
