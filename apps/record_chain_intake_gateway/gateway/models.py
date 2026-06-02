# gateway/models.py
"""Pydantic models for request / response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, computed_field


# ---------------------------------------------------------------------------
# Diagnostic
# ---------------------------------------------------------------------------

class Diagnostic(BaseModel):
    """A single diagnostic message attached to a response."""

    code: str = Field(..., description="Machine-readable diagnostic code")
    severity: str = Field(..., description="error | warning | info")
    field: str | None = Field(None, description="Field path that triggered this diagnostic")
    message: str = Field(..., description="Human-readable explanation")
    meaning: str | None = Field(None, description="Extended explanation of what this diagnostic means")
    suggested_fix: str | None = Field(None, description="Suggested remediation step")
    help_url: str | None = Field(None, description="URL to documentation for this diagnostic code")
    retry_allowed: bool = Field(True, description="Whether retrying with corrections is allowed")


# ---------------------------------------------------------------------------
# Agent recovery guidance
# ---------------------------------------------------------------------------

class AgentRecovery(BaseModel):
    """Machine-readable recovery guidance for agents after a failed preflight."""

    should_retry: bool = Field(..., description="Whether the agent should retry")
    recommended_next_step: str = Field(..., description="Human-readable next step recommendation")
    helper_url: str | None = Field(None, description="URL to helper documentation")
    human_readable_helper_url: str | None = Field(None, description="Human-readable version of helper_url")
    builder_doctor_command: str | None = Field(None, description="CLI command to diagnose the issue")
    builder_error_help_command: str | None = Field(None, description="CLI command for error-specific help")
    requires_human_attention: bool = Field(False, description="Whether a human must review this issue")


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AuthorshipProof(BaseModel):
    """Ed25519 authorship proof attached to a submission."""

    schema_: str | None = Field(None, alias="schema", description="Proof schema identifier")
    method: str | None = Field(None, description="Signing method (e.g. ed25519)")
    algorithm: str | None = Field(None, description="Algorithm identifier")
    public_key_pem: str = Field(..., description="PEM-encoded Ed25519 public key")
    public_key_sha256: str | None = Field(None, description="SHA-256 hex of raw public key bytes")
    signed_payload_sha256: str | None = Field(None, description="SHA-256 hex of canonical draft bytes")
    signature_base64: str | None = Field(None, description="Base-64 Ed25519 signature")
    signed_message: str | None = Field(None, description="Human-readable message that was signed")
    claim_boundary: dict[str, bool] | None = Field(None, description="Boundary claims the signer acknowledges")

    model_config = {"populate_by_name": True}


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
    oath_gate_mode: str = Field("required", description="Oath gate enforcement mode: required | warn | disabled")


class PreflightResponse(BaseModel):
    """Response for the preflight (validate-only) endpoint."""

    accepted: bool
    preflight: bool = True
    route_detected: str = ""
    record_type: str = ""
    submission_sha256: str = ""
    received_raw_body_sha256: str = ""
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    gateway_runtime: dict[str, Any] = Field(default_factory=dict)
    gateway_schema: dict[str, Any] = Field(default_factory=dict)
    boundary: dict[str, bool] = Field(default_factory=dict)
    agent_recovery: AgentRecovery | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ok(self) -> bool:
        """Backward-compat alias for accepted."""
        return self.accepted

    @property
    def route(self) -> str:
        return self.route_detected

    @property
    def errors(self) -> list[str]:
        return [d.message for d in self.diagnostics if d.severity == "error"]


class ServerReceipt(BaseModel):
    """Receipt returned after a successful submission."""

    server_receipt_id: str
    service: str
    gateway_version: str
    record_type: str
    submission_sha256: str
    received_raw_body_sha256: str = ""
    accepted_at: str
    file_path: str | None = None
    intake_submission_path: str = ""
    pending_file_path: str = ""
    receipt_path: str = ""
    commit_sha: str | None = None
    receipt_sha256: str
    receipt_is_not_final_chain_record: bool = True


class SubmitResponse(BaseModel):
    """Response for the submit endpoint."""

    accepted: bool
    submitted: bool = False
    receipt_id: str = ""
    record_type: str = ""
    submission_sha256: str = ""
    received_raw_body_sha256: str = ""
    pending_file_path: str = ""
    intake_submission_path: str = ""
    receipt_path: str = ""
    server_created_at: str = ""
    append_status: str = ""
    receipt: dict[str, Any] | None = None
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    boundary: dict[str, bool] = Field(default_factory=dict)
    created_pending_records: list[str] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ok(self) -> bool:
        """Backward-compat alias for accepted."""
        return self.accepted

    @property
    def errors(self) -> list[str]:
        return [d.message for d in self.diagnostics if d.severity == "error"]

    @property
    def route(self) -> str:
        return self.record_type


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
