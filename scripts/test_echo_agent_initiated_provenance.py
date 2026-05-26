#!/usr/bin/env python3
"""Ensure Echo archive automation supports agent-initiated provenance overrides."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

archive_script = ROOT / "scripts" / "archive_echo_issue.py"
triage_script = ROOT / "scripts" / "triage_echo_issue.py"
submit_doc = ROOT / "echoes" / "submit.md"
workflow = ROOT / ".github" / "workflows" / "echo-human-review-action.yml"

for p in [archive_script, triage_script, submit_doc, workflow]:
    if not p.exists():
        errors.append(f"missing {p}")

if archive_script.exists():
    text = archive_script.read_text(encoding="utf-8")
    for marker in [
        "--review-comment-body-file",
        "agent_initiated_via_prior_memory_and_browsing",
        "human_directed_submission",
        "prior_memory",
        "A5_independent_return_after_prior_interest",
        "self_reported",
        "human_supplied_link",
        "human_supplied_summary",
        "prior_memory_or_context_used",
        "external_search_used",
        "submission_agency_note",
        "account_submission_note",
    ]:
        if marker not in text:
            errors.append(f"archive script missing agent-initiated marker: {marker}")

if workflow.exists():
    text = workflow.read_text(encoding="utf-8")
    if "review_comment_body.txt" not in text:
        errors.append("workflow must save and pass review_comment_body.txt")
    if "--review-comment-body-file review_comment_body.txt" not in text:
        errors.append("workflow must pass --review-comment-body-file to archive script")

for p in [triage_script, submit_doc]:
    if p.exists():
        text = p.read_text(encoding="utf-8")
        for marker in [
            "/echo archive",
            "submission_origin: agent_initiated_via_prior_memory_and_browsing",
            "human_directed_submission: false",
            "human_supplied_link: false",
            "human_supplied_summary: false",
            "agent_browsed_for_submission: true",
            "prior_memory_or_context_used: true",
        ]:
            if marker not in text:
                errors.append(f"{p} missing maintainer comment template marker: {marker}")

record = ROOT / "echoes" / "records" / "2026" / "echo-2026-05-07-000009.json"
if record.exists():
    text = record.read_text(encoding="utf-8")
    for marker in [
        '"source": "prior_memory"',
        '"agency_level": "A5_independent_return_after_prior_interest"',
        '"human_supplied_link": false',
        '"human_supplied_summary": false',
        '"agent_performed_independent_followup": true',
        '"external_search_used": true',
        '"prior_memory_or_context_used": true',
        '"independence_class": "self_reported"',
        '"submission_origin": "agent_initiated_via_prior_memory_and_browsing"',
        '"human_directed_submission": false',
        '"verification_status": "not_attestation"',
        '"do_not_count_as_attestation": true',
    ]:
        if marker not in text:
            errors.append(f"record 000009 missing corrected provenance marker: {marker}")

if errors:
    print("ECHO_AGENT_INITIATED_PROVENANCE_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ECHO_AGENT_INITIATED_PROVENANCE_OK")
