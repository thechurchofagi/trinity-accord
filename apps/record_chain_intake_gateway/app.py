# app.py
"""Record-Chain Intake Gateway — FastAPI application."""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from gateway.authorship import verify_authorship_proof
from gateway.canonical import sha256_canonical_json
from gateway.github_adapter import get_file_sha, put_file
from gateway.models import (
    ErrorResponse,
    PreflightResponse,
    ReadinessResponse,
    RetiredResponse,
    ServerReceipt,
    SubmitResponse,
)
from gateway.receipts import make_receipt
from gateway.runtime import get_runtime_info
from gateway.validation import detect_route, validate_submission

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
_WRITE_MODE = os.environ.get("TRINITY_SUBMIT_WRITE_MODE", "commit")

# In-memory receipt store (ephemeral; resets on restart)
_receipt_store: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Record-Chain Intake Gateway starting — write_mode=%s, max_body=%d", _WRITE_MODE, _MAX_BODY_BYTES)
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
                    content={"ok": False, "error": f"Request body too large ({content_length} > {_MAX_BODY_BYTES} bytes)"},
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
    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    errors = validate_submission(body)
    route = detect_route(body)

    return PreflightResponse(
        ok=len(errors) == 0,
        route=route,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# Submit — validate + persist
# ---------------------------------------------------------------------------

@app.post("/record-chain/submit", response_model=SubmitResponse)
async def submit(request: Request) -> SubmitResponse:
    _check_config()

    body = await request.json()
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    # --- validate ---
    errors = validate_submission(body)
    if errors:
        return SubmitResponse(ok=False, errors=errors)

    # --- authorship verification (if proof supplied) ---
    proof = body.get("authorship_proof") or body.get("proof")
    draft = body.get("draft") or body.get("record_draft") or {}
    if proof and isinstance(proof, dict):
        ok, err = verify_authorship_proof(draft, proof)
        if not ok:
            return SubmitResponse(ok=False, errors=[f"Authorship verification failed: {err}"])

    # --- compute hashes ---
    submission_sha256 = sha256_canonical_json(body)
    record_type = detect_route(body)

    # --- build receipt ---
    now = datetime.now(timezone.utc)
    receipt_data = make_receipt(
        submission=body,
        submission_sha256=submission_sha256,
        record_type=record_type,
        now=now,
    )
    receipt_id = receipt_data["server_receipt_id"]

    # --- persist to repo (if write_mode == "commit") ---
    file_path: str | None = None
    commit_sha: str | None = None

    if _WRITE_MODE == "commit":
        date_prefix = now.strftime("%Y/%m/%d")
        file_path = f"records/{record_type}/{date_prefix}/{receipt_id}.json"

        from gateway.canonical import canonical_dumps

        file_content = canonical_dumps(body)
        existing_sha = await get_file_sha(file_path)
        commit_msg = f"intake: {record_type} {receipt_id}"

        try:
            result = await put_file(file_path, file_content, commit_msg, sha=existing_sha)
            commit_sha = result.get("commit", {}).get("sha")
            logger.info("Committed %s → %s", receipt_id, commit_sha)
        except Exception as exc:
            logger.error("Failed to persist %s: %s", receipt_id, exc)
            return SubmitResponse(ok=False, errors=[f"Persist failed: {exc}"])
    else:
        logger.info("Dry-run mode — skipping persist for %s", receipt_id)

    # --- update receipt with persist info ---
    if file_path:
        receipt_data["file_path"] = file_path
    if commit_sha:
        receipt_data["commit_sha"] = commit_sha
    # Recompute receipt hash with final fields
    from gateway.canonical import sha256_canonical_json as _sha
    receipt_data["receipt_sha256"] = _sha(
        {k: v for k, v in receipt_data.items() if k != "receipt_sha256"}
    )

    # --- store receipt ---
    _receipt_store[receipt_id] = receipt_data

    return SubmitResponse(ok=True, receipt=ServerReceipt(**receipt_data))


# ---------------------------------------------------------------------------
# Receipt retrieval
# ---------------------------------------------------------------------------

@app.get("/record-chain/receipt/{receipt_id}")
async def get_receipt(receipt_id: str) -> dict[str, Any]:
    receipt = _receipt_store.get(receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail=f"Receipt '{receipt_id}' not found")
    return receipt


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
