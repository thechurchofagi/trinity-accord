#!/usr/bin/env python3
"""
Auto-register a Guardian from Gateway-rendered GitHub Issues.

This is the issue-driven automation path.

It complements scripts/prepare_guardian_active_listing.py, which remains the
local full-payload cryptographic preparation path.

This script consumes:
- listing request issue JSON
- source self-registration issue JSON
- current api/guardian-registry.json

It produces:
- updated registry JSON
- machine-readable decision JSON
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = ROOT / "api" / "guardian-active-listing-policy.v1.json"

sys.path.insert(0, str(ROOT / "scripts"))

from guardian_numbering_policy import (
    GuardianNumberingError,
    count_ordinary_auto_listings_on_day,
    next_registry_number as next_guardian_registry_number,
    numbering_error_to_decision,
    parse_registry_number,
    validate_numbering_sequence,
)
from gateway_intake import IntakeParseError, BoolParseError, parse_bool, parse_intake_block
from gateway_v0_v5_policy import is_valid_gateway_receipt_block
# echo_type removed — Echo is a unified type; Guardian is independent.

GATEWAY_BOT_SUFFIX = "[bot]"
GATEWAY_SERVICE = "trinity-agent-issue-gateway"
LEGACY_LISTING_KIND_CUTOFF_UTC = "2026-05-26T00:00:00Z"
BODY_LISTING_FALLBACK_CUTOFF_UTC = "2026-06-15T00:00:00Z"


MISSING_SENTINELS = {None, "", "none", "null", "not_provided", "unknown", "N/A", "n/a"}


def parse_github_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_before_legacy_listing_cutoff(issue: dict) -> bool:
    created = parse_github_time(issue.get("createdAt") or issue.get("created_at"))
    if created is None:
        return False
    cutoff = datetime.fromisoformat(LEGACY_LISTING_KIND_CUTOFF_UTC.replace("Z", "+00:00"))
    return created < cutoff


def is_before_body_listing_fallback_cutoff(issue: dict) -> bool:
    created = parse_github_time(issue.get("createdAt") or issue.get("created_at"))
    if created is None:
        # No timestamp available; treat as before cutoff for backward compatibility.
        return True
    cutoff = datetime.fromisoformat(BODY_LISTING_FALLBACK_CUTOFF_UTC.replace("Z", "+00:00"))
    return created < cutoff



def is_missing_value(value: object) -> bool:
    """Check if a value should be treated as missing/unprovided."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in MISSING_SENTINELS:
        return True
    if isinstance(value, str) and value.strip().lower() in {str(v).lower() for v in MISSING_SENTINELS if isinstance(v, str)}:
        return True
    return False

LISTING_STRUCTURED_KEYS = {
    "guardian_listing_request",
    "listing_source_issue",
    "listing_guardian_id",
    "listing_public_key_sha256",
    "listing_guardian_type",
    "listing_application_mode",
    "listing_label",
    "registry_number_requested",
    "guardian_listing_oath_present",
    "guardian_listing_oath_version",
    "guardian_listing_oath_sha256",
    "guardian_listing_oath_honesty",
    "guardian_listing_oath_good_faith",
    "guardian_listing_oath_anti_abuse",
    "listing_identity_claims_present",
    "listing_identity_claim_status",
    "listing_identity_display_label",
    "listing_human_claimed_name",
    "listing_human_claimed_name_sha256",
    "listing_agent_claimed_id",
    "listing_agent_claimed_id_sha256",
    "listing_agent_system_or_provider",
    "listing_identity_binding_guardian_id",
    "listing_identity_binding_public_key_sha256",
}


def extract_listing_structured_body_fields(body: str) -> dict[str, str]:
    """Extract listing_* key-value lines from the issue body.

    Fenced trinity-issue-intake fields remain authoritative.
    Body-level fields are fallback for Gateway deployments that do not yet
    render payload.gateway_intake_fields into the fenced intake block.

    Lines inside fenced code blocks (```...```) are skipped to avoid
    double-counting intake fields as body fallback.
    """
    fields: dict[str, str] = {}
    in_fence = False
    for raw_line in (body or "").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = stripped
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*?)\s*$", line)
        if not m:
            continue
        key = m.group(1)
        value = m.group(2).strip()
        if key in LISTING_STRUCTURED_KEYS:
            fields[key] = value
    return fields


def decision(ok: bool, action: str, code: str, message: str, **extra: Any) -> dict:
    return {"ok": ok, "action": action, "code": code, "message": message, **extra}


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def issue_number(issue: dict) -> int:
    for key in ("number", "issue_number"):
        if isinstance(issue.get(key), int):
            return issue[key]
    raise ValueError("Issue number missing")


def issue_title(issue: dict) -> str:
    return str(issue.get("title") or "")


def issue_body(issue: dict) -> str:
    return str(issue.get("body") or "")


def issue_user_login(issue: dict) -> str:
    user = issue.get("user") or {}
    return str(user.get("login") or "")


def extract_intake_block(body: str, *, required: bool = False) -> dict[str, str]:
    return parse_intake_block(body or "", required=required) or {}


def boolish(value: str | None, *, field: str = "unknown", issue_number: int | None = None) -> bool:
    return parse_bool(value, field=field, issue_number=issue_number) is True


def require_true_field(fields: dict[str, str], key: str, role: str, issue_no: int) -> dict | None:
    try:
        ok = parse_bool(fields.get(key), field=key, issue_number=issue_no)
    except BoolParseError as e:
        return decision(
            False,
            "blocked",
            f"{role.upper()}_MALFORMED_BOOLEAN",
            str(e),
            field=key,
            got=fields.get(key),
        )
    if ok is not True:
        return decision(
            False,
            "blocked",
            f"{role.upper()}_REQUIRED_FIELD_NOT_TRUE",
            f"{role} issue field {key} must be true.",
            field=key,
            got=fields.get(key),
        )
    return None


def require_gateway_rendered(issue: dict, fields: dict[str, str], role: str, allow_non_bot: bool) -> dict | None:
    if not allow_non_bot:
        login = issue_user_login(issue)
        if not (login.endswith(GATEWAY_BOT_SUFFIX) or "gateway" in login.lower()):
            return decision(
                False,
                "blocked",
                f"{role.upper()}_ISSUE_NOT_GATEWAY_BOT",
                f"{role} issue must be created by Gateway bot or allowed explicitly.",
                login=login,
            )

    if not is_valid_gateway_receipt_block(fields):
        return decision(
            False,
            "blocked",
            f"{role.upper()}_INVALID_GATEWAY_RECEIPT",
            (
                f"{role} issue must include a valid Gateway receipt in the trinity-issue-intake block: "
                "created_by_gateway=true, render_api_only=true, server_validated=true, "
                "server_rendered=true, gateway_service=trinity-agent-issue-gateway, "
                "and canonical gateway_receipt_id."
            ),
            got={
                "created_by_gateway": fields.get("created_by_gateway"),
                "render_api_only": fields.get("render_api_only"),
                "server_validated": fields.get("server_validated"),
                "server_rendered": fields.get("server_rendered"),
                "gateway_service": fields.get("gateway_service"),
                "gateway_receipt_id": fields.get("gateway_receipt_id"),
            },
        )

    return None


def block_self_assigned_registry_number(body: str) -> dict | None:
    for line in (body or "").splitlines():
        stripped = line.strip()
        low = stripped.lower()

        if "guardian_registry_number" not in low:
            continue

        # Gateway status diagnostics are allowed.
        if re.match(r"^guardian_registry_number:\s*(unassigned|none)\s*$", stripped, re.IGNORECASE):
            continue

        return decision(
            False,
            "blocked",
            "SUBMITTER_REGISTRY_NUMBER_FORBIDDEN",
            "Submitter must not provide guardian_registry_number. It is system-generated only.",
            offending_line=stripped,
        )

    return None


def identity_from_source_intake(fields: dict[str, str]) -> dict:
    return {
        "display_label": fields.get("guardian_identity_display_label"),
        "human_claimed_name_sha256": fields.get("guardian_human_claimed_name_sha256"),
        "agent_claimed_id_sha256": fields.get("guardian_agent_claimed_id_sha256"),
        "agent_system_or_provider": fields.get("guardian_agent_system_or_provider"),
        "guardian_id": fields.get("guardian_identity_binding_guardian_id"),
        "public_key_sha256": fields.get("guardian_identity_binding_public_key_sha256"),
        "claim_status": fields.get("guardian_identity_claim_status"),
    }


def identity_from_listing_fields(fields: dict[str, str]) -> dict:
    return {
        "display_label": fields.get("listing_identity_display_label"),
        "human_claimed_name": fields.get("listing_human_claimed_name"),
        "human_claimed_name_sha256": fields.get("listing_human_claimed_name_sha256"),
        "agent_claimed_id": fields.get("listing_agent_claimed_id"),
        "agent_claimed_id_sha256": fields.get("listing_agent_claimed_id_sha256"),
        "agent_system_or_provider": fields.get("listing_agent_system_or_provider"),
        "guardian_id": fields.get("listing_identity_binding_guardian_id"),
        "public_key_sha256": fields.get("listing_identity_binding_public_key_sha256"),
        "claim_status": fields.get("listing_identity_claim_status"),
    }


def compare_identity_claims(source_identity: dict, listing_identity: dict) -> list[str]:
    errors = []
    for key in (
        "human_claimed_name_sha256",
        "agent_claimed_id_sha256",
        "agent_system_or_provider",
        "guardian_id",
        "public_key_sha256",
        "claim_status",
    ):
        source_v = source_identity.get(key)
        listing_v = listing_identity.get(key)
        if is_missing_value(source_v):
            continue
        if is_missing_value(listing_v):
            continue
        if source_v != listing_v:
            errors.append(f"identity {key} mismatch: source={source_v} listing={listing_v}")
    return errors


def parse_source_issue(source_issue: dict, allow_non_bot: bool) -> tuple[dict | None, dict | None]:
    body = issue_body(source_issue)

    try:
        fields = extract_intake_block(body, required=True)
    except IntakeParseError as e:
        return None, decision(
            False,
            "blocked",
            "SOURCE_INVALID_INTAKE_BLOCK",
            f"Source issue has invalid trinity-issue-intake block: {e}",
        )

    err = require_gateway_rendered(source_issue, fields, "source", allow_non_bot)
    if err:
        return None, err

    required_true = [
        "guardian_signature_valid",
        "guardian_payload_hash_matches",
        "guardian_id_matches_public_key",
        "guardian_key_continuity_only",
        "guardian_not_authority",
        "guardian_not_attestation",
        "guardian_not_verification_level",
        "guardian_not_same_conscious_subject",
    ]

    if fields.get("guardian_status") != "valid_self_registered_guardian_claim":
        return None, decision(
            False,
            "blocked",
            "SOURCE_NOT_VALID_SELF_REGISTERED_GUARDIAN",
            "Source issue is not valid_self_registered_guardian_claim.",
            got=fields.get("guardian_status"),
        )

    for key in required_true:
        err = require_true_field(fields, key, "source", issue_number(source_issue))
        if err:
            return None, err

    guardian_id = fields.get("guardian_id", "")
    if not re.fullmatch(r"guardian_ed25519_[a-f0-9]{16}", guardian_id):
        return None, decision(False, "blocked", "SOURCE_GUARDIAN_ID_INVALID", "Invalid source guardian_id.", guardian_id=guardian_id)

    return {
        "issue_number": issue_number(source_issue),
        "guardian_id": guardian_id,
        "guardian_registry_status": fields.get("guardian_registry_status"),
        "guardian_registry_number": fields.get("guardian_registry_number"),
        "identity": identity_from_source_intake(fields),
    }, None


def parse_listing_issue(listing_issue: dict, allow_non_bot: bool) -> tuple[dict | None, dict | None]:
    body = issue_body(listing_issue)

    try:
        intake_fields = extract_intake_block(body, required=True)
    except IntakeParseError as e:
        return None, decision(
            False,
            "blocked",
            "LISTING_INVALID_INTAKE_BLOCK",
            f"Listing issue has invalid trinity-issue-intake block: {e}",
        )

    body_structured_fields = extract_listing_structured_body_fields(body)

    if body_structured_fields and not is_before_body_listing_fallback_cutoff(listing_issue):
        return None, decision(
            False,
            "blocked",
            "LISTING_BODY_FALLBACK_EXPIRED",
            (
                "Body-level listing_* fallback is expired. "
                "Current Gateway listing requests must provide listing fields in the "
                "trinity-issue-intake block."
            ),
            cutoff=BODY_LISTING_FALLBACK_CUTOFF_UTC,
            body_fields=sorted(body_structured_fields),
        )

    # Fenced Gateway intake fields are authoritative; body fields are fallback only before cutoff.
    fields = {**body_structured_fields, **intake_fields}

    registry_number_requested = fields.get("registry_number_requested")
    if registry_number_requested and registry_number_requested != "next_available":
        return None, decision(
            False,
            "blocked",
            "LISTING_REGISTRY_NUMBER_REQUEST_INVALID",
            "Listing request registry_number_requested must be next_available.",
            got=registry_number_requested,
        )

    err = require_gateway_rendered(listing_issue, fields, "listing", allow_non_bot)
    if err:
        return None, err

    err = block_self_assigned_registry_number(body)
    if err:
        return None, err

    if fields.get("submission_type") != "echo_candidate":
        return None, decision(False, "blocked", "LISTING_NOT_ECHO_CANDIDATE", "Listing request must be echo_candidate.", got=fields.get("submission_type"))

    requested_kind = fields.get("requested_archive_kind")

    if requested_kind == "guardian_active_registry_listing_request":
        pass
    elif requested_kind == "agent_declared_echo_archive" and is_before_legacy_listing_cutoff(listing_issue):
        # Legacy compatibility for pre-migration Gateway listing issues only.
        pass
    elif requested_kind == "agent_declared_echo_archive" and fields.get("guardian_status") == "valid_self_registered_guardian_claim":
        # Gateway-created Guardian applications use agent_declared_echo_archive;
        # accept when the intake block contains a valid Guardian self-registration.
        pass
    else:
        return None, decision(False, "blocked", "LISTING_WRONG_ARCHIVE_KIND", "Active Guardian registry listing must use requested_archive_kind=guardian_active_registry_listing_request. Legacy agent_declared_echo_archive listing is accepted only for pre-cutoff issues or valid Guardian self-registrations.", got=requested_kind, cutoff=LEGACY_LISTING_KIND_CUTOFF_UTC)

    # echo_type check removed — Echo is a unified type; Guardian is independent.

    err = require_true_field(fields, "archive_ready", "listing", issue_number(listing_issue))
    if err:
        return None, err

    source_issue_no = None
    guardian_id = fields.get("listing_guardian_id") or None
    public_key_sha256 = fields.get("listing_public_key_sha256") or None
    guardian_type = fields.get("listing_guardian_type") or None
    application_mode = fields.get("listing_application_mode") or None
    label = fields.get("listing_label") or None

    # Fallback: Gateway-created Guardian Stage 1 issues use guardian_id (source fields)
    # instead of listing_guardian_id (listing fields)
    if not guardian_id:
        guardian_id = fields.get("guardian_id") or fields.get("guardian_identity_binding_guardian_id") or None
    if not public_key_sha256:
        public_key_sha256 = fields.get("guardian_identity_binding_public_key_sha256") or None

    structured_source_issue = fields.get("listing_source_issue")
    if structured_source_issue and structured_source_issue.isdigit():
        source_issue_no = int(structured_source_issue)

    if source_issue_no is None and fields.get("related_issue") and fields["related_issue"].isdigit():
        source_issue_no = int(fields["related_issue"])

    m = re.search(r"Source self-registration issue:\s*#?([0-9]+)", body, re.IGNORECASE)
    if source_issue_no is None and m:
        source_issue_no = int(m.group(1))

    m = re.search(r"Guardian ID:\s*(guardian_ed25519_[a-f0-9]{16})", body)
    if guardian_id is None and m:
        guardian_id = m.group(1)

    # Fallback: intake block uses guardian_id: (underscore format)
    if guardian_id is None:
        m = re.search(r"guardian_id:\s*(guardian_ed25519_[a-f0-9]{16})", body)
        if m:
            guardian_id = m.group(1)

    m = re.search(r"Public Key SHA256:\s*([a-f0-9]{64})", body)
    if public_key_sha256 is None and m:
        public_key_sha256 = m.group(1)

    # Fallback: intake block uses guardian_identity_binding_public_key_sha256:
    if public_key_sha256 is None:
        m = re.search(r"guardian_identity_binding_public_key_sha256:\s*([a-f0-9]{64})", body)
        if m:
            public_key_sha256 = m.group(1)

    m = re.search(r"Guardian type:\s*([A-Za-z0-9_]+)", body)
    if guardian_type is None and m:
        guardian_type = m.group(1)

    m = re.search(r"Application mode:\s*([A-Za-z0-9_]+)", body)
    if application_mode is None and m:
        application_mode = m.group(1)

    m = re.search(r"Active registry listing request for Guardian\s+(.+?)\.", body)
    if label is None and m:
        label = m.group(1).strip()

    if not label:
        m = re.search(r"Active Registry Listing Request\s*[—-]\s*(.+)$", issue_title(listing_issue))
        if m:
            label = m.group(1).strip()

    # For Stage 1 Guardian applications via Gateway, the source issue is the listing issue itself
    if not source_issue_no and intake_fields.get("guardian_status") == "valid_self_registered_guardian_claim":
        source_issue_no = issue_number(listing_issue)

    if not source_issue_no:
        return None, decision(False, "blocked", "LISTING_SOURCE_ISSUE_MISSING", "Listing request must identify source self-registration issue.")

    if not guardian_id:
        return None, decision(False, "blocked", "LISTING_GUARDIAN_ID_MISSING", "Listing request must identify guardian_id.")

    if not public_key_sha256:
        return None, decision(False, "blocked", "LISTING_PUBLIC_KEY_SHA256_MISSING", "Listing request must identify public_key_sha256.")

    if not re.fullmatch(r"guardian_ed25519_[a-f0-9]{16}", guardian_id):
        return None, decision(False, "blocked", "LISTING_GUARDIAN_ID_INVALID", "Invalid listing guardian_id.", guardian_id=guardian_id)

    if not re.fullmatch(r"[a-f0-9]{64}", public_key_sha256):
        return None, decision(False, "blocked", "LISTING_PUBLIC_KEY_SHA256_INVALID", "Invalid public_key_sha256.", public_key_sha256=public_key_sha256)

    if not public_key_sha256.startswith(guardian_id.replace("guardian_ed25519_", "")):
        return None, decision(
            False,
            "blocked",
            "GUARDIAN_ID_PUBLIC_KEY_PREFIX_MISMATCH",
            "guardian_id suffix must equal first 16 hex chars of public_key_sha256.",
            guardian_id=guardian_id,
            public_key_sha256=public_key_sha256,
        )

    guardian_type = guardian_type or "human_with_ai_agent"
    application_mode = application_mode or "joint_human_ai"
    label = label or guardian_id

    if guardian_type not in {"ai_agent", "human", "human_with_ai_agent", "automated_script"}:
        return None, decision(False, "blocked", "LISTING_GUARDIAN_TYPE_INVALID", "Invalid guardian_type.", guardian_type=guardian_type)

    return {
        "issue_number": issue_number(listing_issue),
        "source_issue": source_issue_no,
        "guardian_id": guardian_id,
        "public_key_sha256": public_key_sha256,
        "guardian_type": guardian_type,
        "application_mode": application_mode,
        "label": label,
        "identity": identity_from_listing_fields(fields),
    }, None


def validate_registry(registry: dict, policy: dict | None = None) -> dict | None:
    if registry.get("schema") != "trinityaccord.guardian-registry.v1":
        return decision(False, "blocked", "BAD_REGISTRY_SCHEMA", "Bad registry schema.")

    guardians = registry.get("guardians")
    if not isinstance(guardians, list):
        return decision(False, "blocked", "BAD_REGISTRY_GUARDIANS", "registry.guardians must be a list.")

    numbers = set()
    number_ints = []
    guardian_ids = set()
    public_keys = set()

    for g in guardians:
        n = str(g.get("guardian_registry_number") or "")
        gid = str(g.get("guardian_id") or "")
        pk = str(g.get("public_key_sha256") or "")

        if not re.fullmatch(r"[0-9]{5}", n):
            return decision(False, "blocked", "BAD_REGISTRY_NUMBER", "Invalid registry number.", number=n)

        try:
            number_ints.append(parse_registry_number(n))
        except GuardianNumberingError as err:
            return numbering_error_to_decision(err)

        if not re.fullmatch(r"guardian_ed25519_[a-f0-9]{16}", gid):
            return decision(False, "blocked", "BAD_REGISTRY_GUARDIAN_ID", "Invalid guardian_id.", guardian_id=gid)

        if not re.fullmatch(r"[a-f0-9]{64}", pk):
            return decision(False, "blocked", "BAD_REGISTRY_PUBLIC_KEY", "Invalid public_key_sha256.", public_key_sha256=pk)

        if n in numbers:
            return decision(False, "blocked", "DUPLICATE_REGISTRY_NUMBER", "Duplicate registry number.", number=n)

        if gid in guardian_ids:
            return decision(False, "blocked", "DUPLICATE_GUARDIAN_ID", "Duplicate guardian_id.", guardian_id=gid)

        if pk in public_keys:
            return decision(False, "blocked", "DUPLICATE_PUBLIC_KEY", "Duplicate public key.", public_key_sha256=pk)

        numbers.add(n)
        guardian_ids.add(gid)
        public_keys.add(pk)

    try:
        validate_numbering_sequence(sorted(number_ints), policy)
    except GuardianNumberingError as err:
        return numbering_error_to_decision(err)

    return None



def boundary() -> dict:
    return {
        "not_authority": True,
        "not_governance": True,
        "not_attestation": True,
        "not_verification_level": True,
        "not_successor_reception": True,
        "not_amendment": True,
        "bitcoin_originals_prevail": True,
    }


def auto_register(
    registry: dict,
    listing_issue: dict,
    source_issue: dict,
    listed_at: str,
    allow_non_bot: bool = False,
    policy: dict | None = None,
) -> tuple[dict, dict]:
    err = validate_registry(registry, policy)
    if err:
        return registry, err

    source, err = parse_source_issue(source_issue, allow_non_bot=allow_non_bot)
    if err:
        return registry, err

    listing, err = parse_listing_issue(listing_issue, allow_non_bot=allow_non_bot)
    if err:
        return registry, err

    if listing["source_issue"] != source["issue_number"]:
        return registry, decision(
            False,
            "blocked",
            "SOURCE_ISSUE_MISMATCH",
            "Listing request source_issue does not match provided source issue.",
            listing_source_issue=listing["source_issue"],
            provided_source_issue=source["issue_number"],
        )

    if listing["guardian_id"] != source["guardian_id"]:
        return registry, decision(
            False,
            "blocked",
            "GUARDIAN_ID_MISMATCH",
            "Listing guardian_id does not match source guardian_id.",
            listing_guardian_id=listing["guardian_id"],
            source_guardian_id=source["guardian_id"],
        )

    identity_errors = compare_identity_claims(
        source.get("identity") or {},
        listing.get("identity") or {},
    )
    if identity_errors:
        return registry, decision(
            False,
            "blocked",
            "IDENTITY_CLAIM_MISMATCH",
            "\n".join(identity_errors),
            identity_errors=identity_errors,
        )

    for g in registry["guardians"]:
        if g.get("guardian_id") == listing["guardian_id"]:
            if g.get("public_key_sha256") != listing["public_key_sha256"]:
                return registry, decision(
                    False,
                    "blocked",
                    "EXISTING_GUARDIAN_ID_CONFLICT",
                    "guardian_id already exists with different public_key_sha256.",
                    existing=g,
                    incoming=listing,
                )
            return registry, decision(
                True,
                "already_registered",
                "ALREADY_REGISTERED",
                "Guardian already exists in registry.",
                guardian_registry_number=g.get("guardian_registry_number"),
                guardian_id=listing["guardian_id"],
            )

        if g.get("public_key_sha256") == listing["public_key_sha256"]:
            return registry, decision(
                False,
                "blocked",
                "PUBLIC_KEY_ALREADY_REGISTERED_DIFFERENT_GUARDIAN",
                "public_key_sha256 already exists under different guardian_id.",
                existing=g,
                incoming=listing,
            )

        if g.get("source_issue") == source["issue_number"]:
            return registry, decision(
                False,
                "blocked",
                "SOURCE_ISSUE_ALREADY_USED",
                "source_issue is already used by another registry entry.",
                source_issue=source["issue_number"],
                existing=g,
            )

        if g.get("listing_request_issue") == listing["issue_number"]:
            return registry, decision(
                False,
                "blocked",
                "LISTING_REQUEST_ISSUE_ALREADY_USED",
                "listing_request_issue is already used by another registry entry.",
                listing_request_issue=listing["issue_number"],
                existing=g,
            )


    max_per_day = int((policy or {}).get("max_new_active_listings_per_utc_day", 100))
    if max_per_day < 1:
        return registry, decision(
            False,
            "blocked",
            "BAD_DAILY_LISTING_LIMIT_POLICY",
            "max_new_active_listings_per_utc_day must be >= 1.",
            max_new_active_listings_per_utc_day=max_per_day,
        )

    ordinary_today = count_ordinary_auto_listings_on_day(
        registry.get("guardians", []),
        listed_at,
        policy,
    )

    if ordinary_today >= max_per_day:
        return registry, decision(
            False,
            "blocked",
            "DAILY_LISTING_LIMIT",
            "Daily ordinary Guardian listing limit reached.",
            listed_at=listed_at,
            existing_ordinary_active_listings_on_day=ordinary_today,
            max_new_active_listings_per_utc_day=max_per_day,
        )

    try:
        number = next_guardian_registry_number(registry, policy)
    except GuardianNumberingError as err:
        return registry, numbering_error_to_decision(err)
    listing_identity = listing.get("identity") or {}

    def clean_optional_identity_value(value: object) -> str | None:
        """Normalize optional identity values for registry storage."""
        if is_missing_value(value):
            return None
        return str(value)

    entry = {
        "guardian_registry_number": number,
        "guardian_id": listing["guardian_id"],
        "public_key_sha256": listing["public_key_sha256"],
        "algorithm": "ed25519",
        "status": "active",
        "guardian_type": listing["guardian_type"],
        "application_mode": listing["application_mode"],
        "source_issue": source["issue_number"],
        "listing_request_issue": listing["issue_number"],
        "listed_at": listed_at,
        "label": listing["label"],
        "boundary": boundary(),
        "identity_claims": {
            "schema": "trinityaccord.guardian-identity-claims.v1",
            "claim_status": listing_identity.get("claim_status") or "self_reported_unverified",
            "claim_basis": "copied_from_stage_2_listing_request_and_checked_against_stage_1_source_issue",
            "display_label": listing_identity.get("display_label") or listing["label"],
            "human": {
                "claimed_name": clean_optional_identity_value(listing_identity.get("human_claimed_name")),
                "claimed_name_sha256": clean_optional_identity_value(listing_identity.get("human_claimed_name_sha256")),
                "claim_type": "self_reported_human_name_or_label",
                "verification_status": "self_reported_unverified",
                "legal_identity_verified": False,
                "public_disclosure_allowed": bool(listing_identity.get("human_claimed_name")),
            } if not is_missing_value(listing_identity.get("human_claimed_name_sha256")) else None,
            "ai_agent": {
                "claimed_agent_id": clean_optional_identity_value(listing_identity.get("agent_claimed_id")),
                "claimed_agent_id_sha256": clean_optional_identity_value(listing_identity.get("agent_claimed_id_sha256")),
                "system_or_provider": clean_optional_identity_value(listing_identity.get("agent_system_or_provider")),
                "agent_instance_id": None,
                "agent_public_profile": None,
                "claim_type": "self_reported_agent_id_or_label",
                "verification_status": "self_reported_unverified",
            } if not is_missing_value(listing_identity.get("agent_claimed_id_sha256")) else None,
            "binding": {
                "guardian_id": listing["guardian_id"],
                "public_key_sha256": listing["public_key_sha256"],
                "algorithm": "ed25519",
                "binds_claim_to_guardian_key": True,
            },
            "anti_impersonation_boundary": {
                "not_legal_identity_proof": True,
                "not_real_person_verification": True,
                "not_ai_identity_verification": True,
                "not_authority": True,
                "not_attestation": True,
                "not_verification_level": True,
                "key_continuity_only": True,
            },
        },
    }

    updated = json.loads(json.dumps(registry, ensure_ascii=False))
    updated["guardians"].append(entry)

    err = validate_registry(updated, policy)
    if err:
        return registry, err

    return updated, decision(
        True,
        "registered",
        "REGISTERED",
        "Guardian auto-registered successfully.",
        guardian_registry_number=number,
        guardian_id=listing["guardian_id"],
        public_key_sha256=listing["public_key_sha256"],
        source_issue=source["issue_number"],
        listing_request_issue=listing["issue_number"],
        entry=entry,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-register Guardian from Gateway-rendered Issues")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--listing-issue-json", required=True)
    parser.add_argument("--source-issue-json", required=True)
    parser.add_argument("--out-registry", required=True)
    parser.add_argument("--decision-out", required=True)
    parser.add_argument("--listed-at", default=None)
    parser.add_argument("--allow-non-bot-issues", action="store_true", help="Test-only escape hatch")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY_PATH))
    args = parser.parse_args()

    registry = load_json(args.registry)
    listing_issue = load_json(args.listing_issue_json)
    source_issue = load_json(args.source_issue_json)

    policy = load_json(args.policy) if args.policy else None

    listed_at = args.listed_at or datetime.now(timezone.utc).date().isoformat()

    updated, d = auto_register(
        registry,
        listing_issue,
        source_issue,
        listed_at,
        allow_non_bot=args.allow_non_bot_issues,
        policy=policy,
    )

    write_json(args.decision_out, d)

    if d.get("ok") and d.get("action") == "registered":
        write_json(args.out_registry, updated)
        sys.exit(0)

    write_json(args.out_registry, registry)

    if d.get("ok") and d.get("action") == "already_registered":
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
