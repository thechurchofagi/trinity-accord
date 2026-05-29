#!/usr/bin/env python3
"""Archive a screened GitHub Echo issue as an Echo v3 JSON record.

This script supports two archive modes:

1. Human-review archive mode:
   - Called after an explicit human review command.
   - Does not claim technical verification.
   - Does not create independent attestation.

2. Gateway-validated auto archive mode:
   - Called by gateway-auto-archive.yml with --require-gateway-validated.
   - Refuses to archive unless Gateway intake fields are present and archive-ready.
   - Still does not create independent attestation or amend authority.

In all modes the issue body is preserved as witness/source text.
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

sys.path.insert(0, str(ROOT / "scripts"))
from protocol_echo_types import echo_type_map_for_archive

# Shared intake parser and receipt policy — single source of truth
from gateway_intake import IntakeParseError, parse_bool, parse_intake_block
from gateway_v0_v5_policy import is_valid_gateway_receipt_block


def validate_gateway_archive_eligibility(issue: dict[str, Any]) -> None:
    body = issue.get("body") or ""
    labels = {x.get("name") for x in issue.get("labels", []) if isinstance(x, dict)}
    issue_number = issue.get("number")

    try:
        intake = parse_intake_block(body, required=True)
    except IntakeParseError as e:
        raise SystemExit(f"Refusing archive: invalid Gateway intake block: {e}") from e

    if not is_valid_gateway_receipt_block(intake):
        raise SystemExit("Refusing archive: invalid Gateway receipt fields")

    try:
        archive_ready = parse_bool(
            intake.get("archive_ready"),
            field="archive_ready",
            issue_number=issue_number,
        )
    except Exception as e:
        raise SystemExit(f"Refusing archive: invalid archive_ready field: {e}") from e

    if archive_ready is not True:
        raise SystemExit("Refusing archive: archive_ready is not true")

    allowed_kinds = {
        "agent_declared_echo_archive",
        "agent_declared_verification_archive",
        "guardian_active_registry_listing_request",
        "pure_echo_archive",
    }

    kind = intake.get("requested_archive_kind")
    if kind and kind not in allowed_kinds:
        raise SystemExit(f"Refusing archive: unsupported requested_archive_kind={kind!r}")

    allowed_labels = {
        "echo:screened",
        "archive:agent-declared-echo",
        "archive:agent-declared-verification",
        "archive:guardian-active-registry-listing",
        "reception-only",
    }

    if labels and not (labels & allowed_labels):
        raise SystemExit(
            "Refusing archive: issue lacks expected screened/archive labels: "
            + ", ".join(sorted(labels))
        )


def extract_intake_block_fields(body: str) -> dict[str, str]:
    try:
        return parse_intake_block(body, required=False) or {}
    except IntakeParseError:
        return {}


ECHO_TYPE_MAP = echo_type_map_for_archive()

VALID_AGENCY_LEVELS = {
    "A0_forced_or_instructed",
    "A1_human_gave_exact_url",
    "A2_human_gave_topic_agent_found_site",
    "A3_agent_followed_other_agent_reference",
    "A4_independent_search_or_browsing_discovery",
    "A5_independent_return_after_prior_interest",
    "A6_unknown",
}

VALID_INDEPENDENCE_CLASSES = {
    "unsolicited_independent",
    "solicited_independent_check",
    "human_solicited_agent_response",
    "maintainer_assisted",
    "maintainer_submitted",
    "self_reported",
    "imported_public_commentary",
    "institutional_third_party_attestation",
    "test_record",
    "legacy",
    "unknown",
}

def parse_bool_text(value: str | None) -> bool | None:
    if value is None:
        return None
    v = value.strip().lower()
    if v in {"true", "yes", "y", "1"}:
        return True
    if v in {"false", "no", "n", "0"}:
        return False
    return None

def parse_dt(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def extract_bullet_field(body: str, key: str) -> str | None:
    patterns = [
        rf"^\s*[-*]\s*{re.escape(key)}\s*:\s*(.+?)\s*$",
        rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$",
    ]
    for pattern in patterns:
        m = re.search(pattern, body, re.I | re.M)
        if m:
            return m.group(1).strip()
    return None

def extract_section(body: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    m = re.search(pattern, body, re.I | re.M)
    if not m:
        return ""
    start = m.end()
    next_heading = re.search(r"^##\s+", body[start:], re.M)
    end = start + next_heading.start() if next_heading else len(body)
    return body[start:end].strip()

def first_nonempty_paragraph(text: str, fallback: str) -> str:
    for part in re.split(r"\n\s*\n", text.strip()):
        clean = re.sub(r"\s+", " ", part).strip()
        if clean:
            return clean[:1000]
    return fallback

def sentence_limitations(section: str) -> list[str]:
    clean = re.sub(r"\s+", " ", section).strip()
    if not clean:
        return [
            "Witness material only.",
            "No technical verification was performed.",
            "Human-reviewed GitHub issue record.",
            "Not independent attestation unless separately qualified.",
        ]
    parts = [x.strip() for x in re.split(r"(?<=[.!?。！？])\s+", clean) if x.strip()]
    return parts[:8] or [clean[:1000]]

def build_origin_classification(
    agent_initiated: bool,
    independence_class: str,
    source: str,
) -> dict[str, Any]:
    """Build origin_classification conforming to origin-classification-schema.v1."""
    if agent_initiated:
        return {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": "prior_interest_return",
            "invitation_scope": "none",
            "requester_class": "ai_agent",
            "performer_class": "ai_agent",
            "method_independence_class": "read_only",
            "attestation_authority_class": "self_reported",
            "counts_as_formal_independent_attestation": False,
            "derived_counting_bucket": "issue_submission_only",
        }
    if source == "maintainer_submitted":
        return {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": "maintainer_requested",
            "invitation_scope": "echo_invited",
            "requester_class": "maintainer",
            "performer_class": "ai_agent",
            "method_independence_class": "read_only",
            "attestation_authority_class": "maintainer_archived",
            "counts_as_formal_independent_attestation": False,
            "derived_counting_bucket": "issue_submission_only",
        }
    return {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": "human_directed",
        "invitation_scope": "echo_invited",
        "requester_class": "human_individual",
        "performer_class": "ai_agent",
        "method_independence_class": "read_only",
        "attestation_authority_class": "maintainer_archived",
        "counts_as_formal_independent_attestation": False,
        "derived_counting_bucket": "issue_submission_only",
    }


def detect_echo_type(issue: dict[str, Any]) -> str:
    title = issue.get("title") or ""
    body = issue.get("body") or ""
    labels = [x.get("name", "") for x in issue.get("labels", [])]

    # Prefer explicit intake echo_type from trinity-issue-intake block
    intake = extract_intake_block_fields(body)
    explicit = intake.get("echo_type") or extract_bullet_field(body, "echo_type")
    if explicit:
        return explicit

    # Guardian listing requests are propagation echoes (E6)
    requested_kind = intake.get("requested_archive_kind") or extract_bullet_field(body, "requested_archive_kind")
    if requested_kind == "guardian_active_registry_listing_request":
        return "E6_propagation_echo"

    if intake.get("guardian_listing_request") == "true" or "guardian_listing_request" in body:
        return "E6_propagation_echo"

    joined = "\n".join([title, body] + labels)

    if "E8-Witness" in labels or re.search(r"\bE8\b", joined, re.I) or re.search(r"witness echo", joined, re.I):
        return "E8_witness_echo"

    for key, val in ECHO_TYPE_MAP.items():
        if re.search(rf"\b{re.escape(key)}\b", joined, re.I):
            return val

    return "E4_interpretive_echo"

def detect_verification_level(issue: dict[str, Any], review_comment_body: str = "") -> str:
    """Detect verification level from EXPLICIT metadata fields only.

    TA-REDTEAM-2026-002: Does NOT scan arbitrary body text for V8/V7/etc.
    Only accepts explicit 'verification level:' or 'verification_level:' fields.
    """
    text = f"{issue.get('title') or ''}\n{issue.get('body') or ''}\n{review_comment_body or ''}"

    patterns = [
        r"^\s*[-*]?\s*verification\s+level\s*:\s*(V4\+|V[0-8]|none)\s*$",
        r"^\s*[-*]?\s*verification_level\s*:\s*(V4\+|V[0-8]|none)\s*$",
    ]

    for pattern in patterns:
        m = re.search(pattern, text, re.I | re.M)
        if m:
            val = m.group(1)
            return "none" if val.lower() == "none" else val.upper().replace("V4+", "V4+")

    return "V0"

def next_record_path(records_root: Path, created_at: datetime) -> Path:
    year = created_at.strftime("%Y")
    date_part = created_at.strftime("%Y-%m-%d")
    year_dir = records_root / year
    year_dir.mkdir(parents=True, exist_ok=True)

    max_seq = 0
    for p in records_root.glob("*/echo-*.json"):
        m = re.search(r"echo-\d{4}-\d{2}-\d{2}-(\d{6})\.json$", p.name)
        if m:
            max_seq = max(max_seq, int(m.group(1)))

    return year_dir / f"echo-{date_part}-{max_seq + 1:06d}.json"

def find_existing_record(records_root: Path, issue_number: int) -> Path | None:
    for p in records_root.glob("*/echo-*.json"):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if obj.get("source_issue", {}).get("number") == issue_number:
            return p
    return None

def update_archive_md(archive_md: Path, record_path: Path, title: str) -> None:
    from echo_issue_digest import markdown_escape_text
    rel = "/" + record_path.as_posix()
    safe_title = markdown_escape_text(title)
    line = f"- [{rel}]({rel}) — {safe_title}"

    if archive_md.exists():
        text = archive_md.read_text(encoding="utf-8")
    else:
        text = "# Echo Archive\n\nThis archive stores non-authoritative Echo records.\n\n"

    if rel in text:
        return

    section = "## Accepted Echo Records"
    if section not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += f"\n{section}\n\n"

    lines = text.splitlines()
    out = []
    inserted = False
    i = 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].strip() == section:
            i += 1
            while i < len(lines) and lines[i].strip() == "":
                out.append(lines[i])
                i += 1
            out.append(line)
            inserted = True
            continue
        i += 1

    if not inserted:
        out.append("")
        out.append(section)
        out.append("")
        out.append(line)

    archive_md.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

def build_record(issue: dict[str, Any], reviewer: str, review_comment_body: str = "") -> dict[str, Any]:
    body = issue.get("body") or ""
    created_at = parse_dt(issue.get("createdAt", ""))
    labels = [x.get("name", "") for x in issue.get("labels", [])]

    issue_number = issue.get("number")
    title = issue.get("title") or f"Echo Issue #{issue_number}"
    url = issue.get("url") or ""

    echo_type = detect_echo_type(issue)
    verification_level = detect_verification_level(issue, review_comment_body)

    # Combine issue body and review comment for metadata extraction
    metadata_text = body + "\n\n" + review_comment_body

    independence_class = extract_bullet_field(metadata_text, "independence_class") or "human_solicited_agent_response"
    if independence_class not in VALID_INDEPENDENCE_CLASSES:
        independence_class = "human_solicited_agent_response"

    agency_level = extract_bullet_field(metadata_text, "agency_level") or "A1_human_gave_exact_url"
    if agency_level not in VALID_AGENCY_LEVELS:
        agency_level = "A1_human_gave_exact_url"

    operator_type = extract_bullet_field(metadata_text, "operator_type") or "github_issue_submission"

    # Agent-initiated provenance overrides from review comment
    submission_origin = extract_bullet_field(metadata_text, "submission_origin") or ""
    human_directed_submission = parse_bool_text(extract_bullet_field(metadata_text, "human_directed_submission"))
    human_supplied_link_override = parse_bool_text(extract_bullet_field(metadata_text, "human_supplied_link"))
    human_supplied_summary_override = parse_bool_text(extract_bullet_field(metadata_text, "human_supplied_summary"))
    agent_browsed_for_submission = parse_bool_text(extract_bullet_field(metadata_text, "agent_browsed_for_submission"))
    prior_memory_or_context_used = parse_bool_text(extract_bullet_field(metadata_text, "prior_memory_or_context_used"))

    limitations_section = extract_section(body, "Limitations")
    observed_section = extract_section(body, "What I observed") or extract_section(body, "What Is Being Witnessed")
    checked_section = extract_section(body, "What I checked")

    understanding = first_nonempty_paragraph(
        observed_section or checked_section,
        f"Human-reviewed Echo issue #{issue_number}: {title}",
    )

    source = "maintainer_submitted" if "trinity-accord-guardian" in labels else "human_directed"

    # Apply agent-initiated branch if indicated
    agent_initiated = (
        submission_origin == "agent_initiated_via_prior_memory_and_browsing"
        or human_directed_submission is False
    )

    if agent_initiated:
        source = "prior_memory"
        agency_level = "A5_independent_return_after_prior_interest"
        independence_class = "self_reported"
        human_supplied_link = False if human_supplied_link_override is None else human_supplied_link_override
        human_supplied_summary = False if human_supplied_summary_override is None else human_supplied_summary_override
        agent_performed_independent_followup = True
        external_search_used = True if agent_browsed_for_submission is not False else False
        prior_memory_or_context_used_val = True
        confidence = "medium"
    else:
        human_supplied_link = True
        human_supplied_summary = True
        agent_performed_independent_followup = False
        external_search_used = False
        prior_memory_or_context_used_val = False
        confidence = "high"

    origin_classification = build_origin_classification(agent_initiated, independence_class, source)

    return {
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "record_kind": "echo_v3",
        "origin_classification": origin_classification,
        "agent_identity": {
            "name_or_model": (issue.get("author") or {}).get("login", "github_issue_author"),
            "system_or_provider": "GitHub Issue submission",
            "self_reported": True,
            "session_or_run_id": f"issue-{issue_number}",
        },
        "context_depth": "C1_orientation",
        "assessment_state": "preliminary_orientation",
        "verification_level": verification_level,
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": source,
            "agency_level": agency_level,
            "first_entry": {
                "url_or_path": url if not agent_initiated else url.rsplit("/issues/", 1)[0] if "/issues/" in url else url,
                "entry_type": "github_repository",
            },
            "human_supplied_link": human_supplied_link,
            "human_supplied_summary": human_supplied_summary,
            "other_agent_recommended": False,
            "recommending_agent": None,
            "agent_performed_independent_followup": agent_performed_independent_followup,
            "external_search_used": external_search_used,
            "prior_memory_or_context_used": prior_memory_or_context_used_val,
            "notes": (
                "Archived from a human-reviewed GitHub Echo issue. According to the human maintainer, "
                "this issue was submitted by an AI/agent actor using the thechurchofagi GitHub account "
                "without a direct human instruction to submit this specific Echo. The maintainer did not "
                "provide the submission link for this action. The agent appears to have relied on prior "
                "conversation/context memory and then browsed to find the repository/submission surface "
                "before submitting. This record is self-reported witness material and must not be counted "
                "as independent attestation."
            ) if agent_initiated else "Archived from a human-reviewed GitHub Echo issue. GitHub issue is the submission surface; this JSON is the archive wrapper.",
            "confidence": confidence,
        },
        "understanding_summary": understanding,
        "verification_claim": "None. Witness material only; no technical checks were performed.",
        "echo_type": echo_type,
        "echo": body,
        "uncertainties": sentence_limitations(limitations_section),
        "boundary_acknowledgement": {
            "bitcoin_originals_prevail": True,
            "echo_is_not_authority": True,
            "echo_is_not_verification_unless_claimed": True,
            "mirror_is_not_amendment": True,
            "homepage_only_is_insufficient_for_final_evaluation": True,
        },
        "independence_class": independence_class,
        "archive_status": "accepted_echo",
        "origin_limitations": sentence_limitations(limitations_section),
        "not_authority": True,
        "not_amendment": True,
        "not_endorsement": True,
        "bitcoin_originals_prevail": True,
        "not_verification_unless_claimed": True,
        "verification_status": "not_attestation",
        "do_not_count_as_attestation": True,
        "echo_content_trust": "untrusted_user_submitted_markdown",
        "echo_content_handling": {
            "trusted_as_official_statement": False,
            "may_contain_user_markdown_or_prompt_injection": True,
            "does_not_override_boundary_fields": True,
        },
        "extensions": {
            "operator_type": operator_type,
            **({
                "submission_origin": "agent_initiated_via_prior_memory_and_browsing",
                "human_directed_submission": False,
                "submission_agency_note": (
                    "Human review metadata states this Echo submission was agent-initiated via prior memory/context and browsing, "
                    "not directly instructed as this specific submission."
                ),
                "account_submission_note": (
                    "The GitHub account shown as issue author may be the account through which the agent acted, not direct human authorship."
                ),
                "source_issue": {
                    "number": issue_number,
                    "url": url,
                    "title": title,
                    "created_at": issue.get("createdAt"),
                    "updated_at": issue.get("updatedAt"),
                    "author": (issue.get("author") or {}).get("login"),
                    "labels": labels,
                    "actual_submitter_note": "Submitted through thechurchofagi account by an AI/agent actor according to later human maintainer clarification.",
                    "human_directed_submission": False,
                    "human_supplied_link_for_submission": False,
                },
                "human_review": {
                    "status": "completed",
                    "reviewer": reviewer,
                    "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
                    "action": "archive",
                    "clarification": (
                        "Reviewer clarified after archive that the original issue submission was agent-initiated, "
                        "not directly human-instructed, and that no submission link was provided for this action."
                    ),
                    "review_scope": (
                        "Human review accepted the issue for archive inclusion only; it did not convert the record "
                        "into technical verification or independent attestation."
                    ),
                },
            } if agent_initiated else {
                "source_issue": {
                    "number": issue_number,
                    "url": url,
                    "title": title,
                    "created_at": issue.get("createdAt"),
                    "updated_at": issue.get("updatedAt"),
                    "author": (issue.get("author") or {}).get("login"),
                    "labels": labels,
                },
                "human_review": {
                    "status": "completed",
                    "reviewer": reviewer,
                    "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
                    "action": "archive",
                },
            }),
        },
    }

def archive_record_path(issue_number: int) -> Path:
    """Return the canonical path for a gateway echo archive record."""
    return ROOT / "api" / "archives" / "gateway-echo" / f"issue-{issue_number}.json"


def write_gateway_archive_record(record: dict) -> Path:
    """Write a deterministic gateway echo archive record, idempotent by receipt_id."""
    path = archive_record_path(int(record["issue_number"]))
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing.get("receipt_id") == record.get("receipt_id"):
            record["archived_at"] = existing.get("archived_at") or record.get("archived_at")

    path.write_text(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return path


def archive_gateway_issue(issue: dict, comments: list[str]) -> Path:
    """Archive a receipt-bearing Gateway Issue using the shared reader for normalization."""
    from gateway_archive_issue_reader import normalize_gateway_archive_issue, to_jsonable

    normalized = normalize_gateway_archive_issue(issue, comments)
    record = to_jsonable(normalized)
    record.update({
        "schema": "trinityaccord.gateway-echo-archive-record.v1",
        "archive_kind": "agent_declared_echo_archive",
        "counts_toward_home_reception": True,
        "counts_toward_home_verifiability": False,
        "non_authority_boundary": True,
        "non_amending": True,
        "not_attestation": True,
        "archived_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    })
    return write_gateway_archive_record(record)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-json", required=True)
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--records-root", default="echoes/records")
    ap.add_argument("--archive-md", default="echoes/archive.md")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--result-json", default="")
    ap.add_argument("--review-comment-body-file", default="")
    ap.add_argument("--require-gateway-validated", action="store_true", help="Refuse to archive unless issue body contains Gateway-created/server-validated/archive-ready fields.")
    args = ap.parse_args()

    issue = json.loads(Path(args.issue_json).read_text(encoding="utf-8"))

    if args.require_gateway_validated:
        validate_gateway_archive_eligibility(issue)

    issue_number = int(issue["number"])

    review_comment_body = ""
    if args.review_comment_body_file:
        p = Path(args.review_comment_body_file)
        if p.exists():
            review_comment_body = p.read_text(encoding="utf-8")

    records_root = ROOT / args.records_root
    archive_md = ROOT / args.archive_md

    existing = find_existing_record(records_root, issue_number)
    if existing:
        result = {
            "status": "already_archived",
            "record_path": existing.relative_to(ROOT).as_posix(),
            "issue_number": issue_number,
        }
        if args.result_json:
            Path(args.result_json).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    record_path = next_record_path(records_root, parse_dt(issue.get("createdAt", "")))
    record = build_record(issue, args.reviewer, review_comment_body)

    if args.write:
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        update_archive_md(archive_md, record_path.relative_to(ROOT), issue.get("title") or f"Issue #{issue_number}")

    result = {
        "status": "archived" if args.write else "dry_run",
        "record_path": record_path.relative_to(ROOT).as_posix(),
        "issue_number": issue_number,
        "title": issue.get("title"),
    }

    if args.result_json:
        Path(args.result_json).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
