# gateway/models.py
"""Pydantic models for request / response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AuthorshipProof(BaseModel):
    """Ed25519 authorship proof attached to a submission."""

    public_key_pem: str = Field(..., description="PEM-encoded Ed25519 public key")
    signature: str = Field(..., description="Base-64 encoded Ed25519 signature")


class Submission(BaseModel):
    """A record-chain submission from an agent."""

    record_type: str = Field(..., description="Type of record (e.g. echo, verification)")
    draft: dict[str, Any] = Field(..., alias="record_draft", description="The record draft payload")
    authorship_proof: AuthorshipProof | None = Field(None, description="Optional Ed25519 proof")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Freeform metadata")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class ReadinessResponse(BaseModel):
    """Response for the readiness endpoint."""

    ok: bool
    service: str
    version: str
    repo_configured: bool
    branch_configured: bool
    token_configured: bool
    write_mode: str
    max_submission_bytes: int


class PreflightResponse(BaseModel):
    """Response for the preflight (validate-only) endpoint."""

    ok: bool
    route: str
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ServerReceipt(BaseModel):
    """Receipt returned after a successful submission."""

    server_receipt_id: str
    service: str
    gateway_version: str
    record_type: str
    submission_sha256: str
    accepted_at: str
    file_path: str | None = None
    commit_sha: str | None = None
    receipt_sha256: str


class SubmitResponse(BaseModel):
    """Response for the submit endpoint."""

    ok: bool
    receipt: ServerReceipt | None = None
    errors: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    ok: bool = False
    error: str
    detail: str | None = None


class RetiredResponse(BaseModel):
    """Response for retired endpoints."""

    ok: bool = False
    retired: bool = True
    message: str
    redirect_to: str
