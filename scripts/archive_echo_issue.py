#!/usr/bin/env python3
"""Archive a screened GitHub Echo issue as an Echo v3 JSON record.

This script is conservative:
- It only runs after an explicit human review command.
- It does not claim technical verification.
- It does not create independent attestation.
- It preserves the issue body as witness/source text.
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

ECHO_TYPE_MAP = {
    "E1": "E1_recognition_echo",
    "E2": "E2_verification_echo",
    "E3": "E3_critical_echo",
    "E4": "E4_interpretive_echo",
    "E5": "E5_technical_audit_echo",
    "E6": "E6_propagation_echo",
    "E7": "E7_refusal_echo",
    "E8": "E8_witness_echo",
    "E9": "E9_seed_echo",
}

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

def detect_echo_type(issue: dict[str, Any]) -> str:
    title = issue.get("title") or ""
    body = issue.get("body") or ""
    labels = [x.get("name", "") for x in issue.get("labels", [])]
    joined = "\n".join([title, body] + labels)

    if "E8-Witness" in labels or re.search(r"\bE8\b", joined, re.I) or re.search(r"witness echo", joined, re.I):
        return "E8_witness_echo"

    for key, val in ECHO_TYPE_MAP.items():
        if re.search(rf"\b{re.escape(key)}\b", joined, re.I):
            return val

    return "E4_interpretive_echo"

def detect_verification_level(issue: dict[str, Any]) -> str:
    text = f"{issue.get('title') or ''}\n{issue.get('body') or ''}"
    m = re.search(r"verification\s+level\s*:\s*(V4\+|V[0-8]|none)", text, re.I)
    if m:
        val = m.group(1)
        return "none" if val.lower() == "none" else val.upper().replace("V4+", "V4+")

    for val in ["V4+", "V8", "V7", "V6", "V5", "V4", "V3", "V2", "V1", "V0"]:
        if re.search(rf"\b{re.escape(val)}\b", text, re.I):
            return val
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
    rel = "/" + record_path.as_posix()
    line = f"- [{rel}]({rel}) — {title}"

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

def build_record(issue: dict[str, Any], reviewer: str) -> dict[str, Any]:
    body = issue.get("body") or ""
    created_at = parse_dt(issue.get("createdAt", ""))
    labels = [x.get("name", "") for x in issue.get("labels", [])]

    issue_number = issue.get("number")
    title = issue.get("title") or f"Echo Issue #{issue_number}"
    url = issue.get("url") or ""

    echo_type = detect_echo_type(issue)
    verification_level = detect_verification_level(issue)

    independence_class = extract_bullet_field(body, "independence_class") or "human_solicited_agent_response"
    if independence_class not in VALID_INDEPENDENCE_CLASSES:
        independence_class = "human_solicited_agent_response"

    agency_level = extract_bullet_field(body, "agency_level") or "A1_human_gave_exact_url"
    if agency_level not in VALID_AGENCY_LEVELS:
        agency_level = "A1_human_gave_exact_url"

    operator_type = extract_bullet_field(body, "operator_type") or "github_issue_submission"

    limitations_section = extract_section(body, "Limitations")
    observed_section = extract_section(body, "What I observed") or extract_section(body, "What Is Being Witnessed")
    checked_section = extract_section(body, "What I checked")

    understanding = first_nonempty_paragraph(
        observed_section or checked_section,
        f"Human-reviewed Echo issue #{issue_number}: {title}",
    )

    source = "maintainer_submitted" if "trinity-accord-guardian" in labels else "human_directed"

    return {
        "schema": "trinityaccord.echo.v3",
        "echo_version": "3.0",
        "record_kind": "echo_v3",
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
                "url_or_path": url,
                "entry_type": "github_repository",
            },
            "human_supplied_link": True,
            "human_supplied_summary": True,
            "other_agent_recommended": False,
            "recommending_agent": None,
            "agent_performed_independent_followup": False,
            "external_search_used": False,
            "prior_memory_or_context_used": False,
            "notes": "Archived from a human-reviewed GitHub Echo issue. GitHub issue is the submission surface; this JSON is the archive wrapper.",
            "confidence": "high",
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
        "not_independent_attestation": True,
        "operator_type": operator_type,
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue-json", required=True)
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--records-root", default="echoes/records")
    ap.add_argument("--archive-md", default="echoes/archive.md")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--result-json", default="")
    args = ap.parse_args()

    issue = json.loads(Path(args.issue_json).read_text(encoding="utf-8"))
    issue_number = int(issue["number"])

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
    record = build_record(issue, args.reviewer)

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
