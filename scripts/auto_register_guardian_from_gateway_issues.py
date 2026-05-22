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

GATEWAY_BOT_SUFFIX = "[bot]"
GATEWAY_SERVICE = "trinity-agent-issue-gateway"


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


def extract_intake_block(body: str) -> dict[str, str]:
    m = re.search(r"```trinity-issue-intake\s*(.*?)```", body or "", re.DOTALL | re.IGNORECASE)
    if not m:
        return {}
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        m_kv = re.match(r"^([A-Za-z0-9_]+):\s*(.*?)\s*$", line.rstrip())
        if m_kv:
            fields[m_kv.group(1)] = m_kv.group(2).strip()
    return fields


def boolish(value: str) -> bool:
    return str(value).strip().lower() == "true"


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

    if not boolish(fields.get("created_by_gateway", "false")):
        return decision(False, "blocked", f"{role.upper()}_NOT_CREATED_BY_GATEWAY", f"{role} issue missing created_by_gateway=true")

    if fields.get("gateway_service") != GATEWAY_SERVICE:
        return decision(
            False,
            "blocked",
            f"{role.upper()}_BAD_GATEWAY_SERVICE",
            f"{role} issue gateway_service mismatch.",
            got=fields.get("gateway_service"),
        )

    if not boolish(fields.get("server_validated", "false")):
        return decision(False, "blocked", f"{role.upper()}_NOT_SERVER_VALIDATED", f"{role} issue missing server_validated=true")

    if not boolish(fields.get("server_rendered", "false")):
        return decision(False, "blocked", f"{role.upper()}_NOT_SERVER_RENDERED", f"{role} issue missing server_rendered=true")

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


def parse_source_issue(source_issue: dict, allow_non_bot: bool) -> tuple[dict | None, dict | None]:
    body = issue_body(source_issue)
    fields = extract_intake_block(body)

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
        if not boolish(fields.get(key, "false")):
            return None, decision(
                False,
                "blocked",
                "SOURCE_REQUIRED_FIELD_NOT_TRUE",
                f"Source issue field {key} must be true.",
                field=key,
                got=fields.get(key),
            )

    guardian_id = fields.get("guardian_id", "")
    if not re.fullmatch(r"guardian_ed25519_[a-f0-9]{16}", guardian_id):
        return None, decision(False, "blocked", "SOURCE_GUARDIAN_ID_INVALID", "Invalid source guardian_id.", guardian_id=guardian_id)

    return {
        "issue_number": issue_number(source_issue),
        "guardian_id": guardian_id,
        "guardian_registry_status": fields.get("guardian_registry_status"),
        "guardian_registry_number": fields.get("guardian_registry_number"),
    }, None


def parse_listing_issue(listing_issue: dict, allow_non_bot: bool) -> tuple[dict | None, dict | None]:
    body = issue_body(listing_issue)
    fields = extract_intake_block(body)

    err = require_gateway_rendered(listing_issue, fields, "listing", allow_non_bot)
    if err:
        return None, err

    err = block_self_assigned_registry_number(body)
    if err:
        return None, err

    if fields.get("submission_type") != "echo_candidate":
        return None, decision(False, "blocked", "LISTING_NOT_ECHO_CANDIDATE", "Listing request must be echo_candidate.", got=fields.get("submission_type"))

    if fields.get("requested_archive_kind") != "agent_declared_echo_archive":
        return None, decision(False, "blocked", "LISTING_NOT_AGENT_DECLARED_ECHO_ARCHIVE", "Listing request must use agent_declared_echo_archive.", got=fields.get("requested_archive_kind"))

    if fields.get("echo_type") != "E7_propagation_echo":
        return None, decision(False, "blocked", "LISTING_NOT_E7", "Listing request must be E7_propagation_echo.", got=fields.get("echo_type"))

    if not boolish(fields.get("archive_ready", "false")):
        return None, decision(False, "blocked", "LISTING_NOT_ARCHIVE_READY", "Listing request must be archive_ready=true.")

    source_issue_no = None
    guardian_id = None
    public_key_sha256 = None
    guardian_type = None
    application_mode = None
    label = None

    if fields.get("related_issue") and fields["related_issue"].isdigit():
        source_issue_no = int(fields["related_issue"])

    m = re.search(r"Source self-registration issue:\s*#?([0-9]+)", body, re.IGNORECASE)
    if m:
        source_issue_no = int(m.group(1))

    m = re.search(r"Guardian ID:\s*(guardian_ed25519_[a-f0-9]{16})", body)
    if m:
        guardian_id = m.group(1)

    m = re.search(r"Public Key SHA256:\s*([a-f0-9]{64})", body)
    if m:
        public_key_sha256 = m.group(1)

    m = re.search(r"Guardian type:\s*([A-Za-z0-9_]+)", body)
    if m:
        guardian_type = m.group(1)

    m = re.search(r"Application mode:\s*([A-Za-z0-9_]+)", body)
    if m:
        application_mode = m.group(1)

    m = re.search(r"Active registry listing request for Guardian\s+(.+?)\.", body)
    if m:
        label = m.group(1).strip()

    if not label:
        m = re.search(r"Active Registry Listing Request\s*[—-]\s*(.+)$", issue_title(listing_issue))
        if m:
            label = m.group(1).strip()

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
    }, None


def validate_registry(registry: dict) -> dict | None:
    if registry.get("schema") != "trinityaccord.guardian-registry.v1":
        return decision(False, "blocked", "BAD_REGISTRY_SCHEMA", "Bad registry schema.")

    guardians = registry.get("guardians")
    if not isinstance(guardians, list):
        return decision(False, "blocked", "BAD_REGISTRY_GUARDIANS", "registry.guardians must be a list.")

    numbers = set()
    guardian_ids = set()
    public_keys = set()

    for g in guardians:
        n = str(g.get("guardian_registry_number") or "")
        gid = str(g.get("guardian_id") or "")
        pk = str(g.get("public_key_sha256") or "")

        if not re.fullmatch(r"[0-9]{5}", n):
            return decision(False, "blocked", "BAD_REGISTRY_NUMBER", "Invalid registry number.", number=n)

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

    if numbers:
        got = sorted(int(n) for n in numbers)
        expected = list(range(1, max(got) + 1))
        if got != expected:
            return decision(False, "blocked", "REGISTRY_NUMBER_GAP", "Existing registry numbers must be gapless.", got=got, expected=expected)

    return None


def next_registry_number(registry: dict) -> str:
    max_n = 0
    for g in registry.get("guardians", []):
        max_n = max(max_n, int(g["guardian_registry_number"]))
    return f"{max_n + 1:05d}"


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


def auto_register(registry: dict, listing_issue: dict, source_issue: dict, listed_at: str, allow_non_bot: bool = False) -> tuple[dict, dict]:
    err = validate_registry(registry)
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

    number = next_registry_number(registry)
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
    }

    updated = json.loads(json.dumps(registry, ensure_ascii=False))
    updated["guardians"].append(entry)

    err = validate_registry(updated)
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
    args = parser.parse_args()

    registry = load_json(args.registry)
    listing_issue = load_json(args.listing_issue_json)
    source_issue = load_json(args.source_issue_json)

    listed_at = args.listed_at or datetime.now(timezone.utc).date().isoformat()

    updated, d = auto_register(
        registry,
        listing_issue,
        source_issue,
        listed_at,
        allow_non_bot=args.allow_non_bot_issues,
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
