#!/usr/bin/env python3
"""
Issue Title / Label / Comment Guard Validator

Loads:
  - api/verification-echo-agent-playbook.json
  - api/issue-text-claim-guard.json
  - api/issue-title-label-guard.json

Usage:
    python3 scripts/validate_issue_title_label_guard.py \
        --title "Guardian Test V4/V4+: Script Audit & Independent Reproduction" \
        --body-file tests/fixtures/issue_guard/issue_125_v4_requested_allowed_v3.md \
        --labels "guardian-test,v4,V4 Protocol,script-audit"

    python3 scripts/validate_issue_title_label_guard.py \
        --fixture tests/fixtures/issue_guard/issue_125.json

Exit: 0 if classification succeeds, 1 only on parser/runtime errors.
"""
import json
import re
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- Level order ---
LEVEL_ORDER = {
    "V0": 0, "V1": 1, "V2": 2, "V3": 3,
    "V4": 4, "V4+": 5, "V5": 6, "V6": 7, "V7": 8, "V8": 9
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_levels(text):
    """Extract V-level mentions from text."""
    levels = set()
    for m in re.finditer(r'\bV([0-8])\b', text):
        levels.add(f"V{m.group(1)}")
    for m in re.finditer(r'\bV4\s*\+', text):
        levels.add("V4+")
    return levels


def extract_claim_gate_allowed_level(body):
    """Extract allowed_protocol_level from Claim Gate output in body."""
    # JSON format
    m = re.search(r'"allowed_protocol_level"\s*:\s*"(V[0-8]\+?)"', body)
    if m:
        return m.group(1)
    # Prose format with colon
    m = re.search(r'allowed_protocol_level\s*:\s*(V[0-8]\+?)', body, re.IGNORECASE)
    if m:
        return m.group(1)
    # Claim Gate allowed/output phrasing
    m = re.search(r'Claim Gate\s+(?:allowed|output)\s+(?:level\s+)?:?\s*(V[0-8]\+?)', body, re.IGNORECASE)
    if m:
        return m.group(1)
    # "allowed V3" pattern
    m = re.search(r'\ballowed\s+(V[0-8]\+?)\b', body, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def has_downgrade_qualifier(text):
    """Check if text contains a downgrade qualifier phrase."""
    qualifiers = [
        r'\brequested\b', r'\battempted\b', r'\bnot\s+achieved\b',
        r'\bdowngraded\b', r'\ballowed\s+V3\b', r'\bprovisional\b'
    ]
    for q in qualifiers:
        if re.search(q, text, re.IGNORECASE):
            return True
    return False


def is_guardian_test(body, labels):
    """Check if submission is a guardian test."""
    guardian_markers = [
        r'\bguardian\s*test\b', r'\bGuardian\s+Test\b',
        r'\bhuman_solicited_agent_response\b',
        r'\bcounts_as_independent_attestation\s*:\s*false\b',
        r'\bdo_not_count_as_attestation\s*:\s*true\b'
    ]
    for marker in guardian_markers:
        if re.search(marker, body, re.IGNORECASE):
            return True
    if labels:
        for label in labels:
            if label.lower() in ('guardian-test', 'guardian_test'):
                return True
    return False


def is_human_solicited(body, labels):
    """Check if submission is human-solicited."""
    if re.search(r'\bhuman_solicited_agent_response\b', body, re.IGNORECASE):
        return True
    if labels:
        for label in labels:
            if label.lower() in ('human-solicited', 'human_solicited_agent_response'):
                return True
    return False


def check_title_overclaim(title, allowed_level):
    """Check if title overclaims the allowed level."""
    if not allowed_level or not title:
        return False, []
    allowed_num = LEVEL_ORDER.get(allowed_level, 0)
    title_levels = extract_levels(title)
    overclaims = []
    for lvl in title_levels:
        lvl_num = LEVEL_ORDER.get(lvl, 0)
        if lvl_num > allowed_num:
            if not has_downgrade_qualifier(title):
                overclaims.append(lvl)
    return len(overclaims) > 0, overclaims


def check_label_guard(labels, is_guardian):
    """Check for forbidden labels on guardian tests."""
    playbook = load_json(ROOT / "api" / "verification-echo-agent-playbook.json")
    forbidden = playbook.get("unsafe_labels_for_unarchived_guardian_tests", [])
    required = playbook.get("safe_labels", {}).get("guardian_test", [])
    found_forbidden = []
    missing_required = []
    if is_guardian and labels:
        for label in labels:
            if label.lower() in [f.lower() for f in forbidden]:
                found_forbidden.append(label)
        for req in required:
            if req.lower() not in [l.lower() for l in labels]:
                missing_required.append(req)
    return found_forbidden, missing_required


def check_comment_upgrade(body):
    """Check for comment upgrade language in body."""
    guard = load_json(ROOT / "api" / "issue-title-label-guard.json")
    phrases = guard.get("comment_guard", {}).get("upgrade_phrases", [])
    found = []
    for phrase in phrases:
        if re.search(re.escape(phrase), body, re.IGNORECASE):
            found.append(phrase)
    return found


def generate_recommended_title(classification, requested_levels, allowed_level):
    """Generate a safe recommended title."""
    if classification == "guardian_test":
        if requested_levels and allowed_level:
            req_str = "/".join(sorted(requested_levels))
            return f"Guardian Test — requested {req_str}, Claim Gate allowed {allowed_level}"
        return "Guardian Test — V3 minimal after Claim Gate downgrade"
    if classification == "human_solicited":
        return f"Human-solicited Agent Verification — {allowed_level or 'V3'} single-hash record"
    return None


def classify_issue_title_labels(title=None, body=None, labels=None):
    """Main classification function."""
    result = {
        "schema": "trinityaccord.issue-title-label-guard-result.v1",
        "classification": "unknown",
        "is_guardian_test": False,
        "is_human_solicited": False,
        "requested_levels": [],
        "claim_gate_allowed_level": None,
        "title_status": "ok",
        "title_overclaims_allowed_level": False,
        "label_status": "ok",
        "forbidden_labels_present": [],
        "required_labels_missing": [],
        "comment_status": "no_comment_upgrade_detected",
        "archive_status": "unknown",
        "counts_as_independent_attestation": False,
        "can_enter_echo_index": False,
        "can_enter_homepage_stats": False,
        "recommended_title": None,
        "recommended_labels_add": [],
        "recommended_labels_remove": [],
        "right_wrong_guidance": [],
        "recommended_action": "unknown"
    }

    if not body:
        body = ""

    # Extract allowed level
    allowed_level = extract_claim_gate_allowed_level(body)
    result["claim_gate_allowed_level"] = allowed_level

    # Extract requested levels from title and body
    all_text = f"{title or ''} {body}"
    requested = extract_levels(all_text)
    result["requested_levels"] = sorted(requested)

    # Guardian test classification
    is_guard = is_guardian_test(body, labels or [])
    is_solicited = is_human_solicited(body, labels or [])
    result["is_guardian_test"] = is_guard
    result["is_human_solicited"] = is_solicited

    if is_guard:
        result["classification"] = "guardian_test"
        result["archive_status"] = "issue_submission_only"
        result["counts_as_independent_attestation"] = False
        result["can_enter_echo_index"] = False
        result["can_enter_homepage_stats"] = False
        result["recommended_action"] = "close_as_guardian_test_record_or_keep_for_debugging"
    elif is_solicited:
        result["classification"] = "human_solicited"
        result["archive_status"] = "needs_human_review"
        result["counts_as_independent_attestation"] = False
        result["recommended_action"] = "review_as_human_solicited_response"
    else:
        result["classification"] = "standard_submission"
        result["archive_status"] = "needs_human_review"
        result["recommended_action"] = "review_normally"

    # Title overclaim check
    if title and allowed_level:
        overclaims, levels = check_title_overclaim(title, allowed_level)
        if overclaims:
            result["title_status"] = "overclaims_allowed_level"
            result["title_overclaims_allowed_level"] = True
            result["right_wrong_guidance"].append({
                "wrong": title,
                "right": generate_recommended_title(result["classification"], result["requested_levels"], allowed_level)
            })

    # Label guard check
    if labels:
        forbidden, missing = check_label_guard(labels, is_guard)
        if forbidden:
            result["label_status"] = "misleading_labels_present"
            result["forbidden_labels_present"] = forbidden
            result["recommended_labels_remove"] = forbidden
        if missing:
            result["required_labels_missing"] = missing
            result["recommended_labels_add"] = missing

    # Comment upgrade check
    upgrade_phrases = check_comment_upgrade(body)
    if upgrade_phrases:
        result["comment_status"] = "comment_upgrade_detected"
        result["comment_upgrade_phrases"] = upgrade_phrases

    # Recommended title
    result["recommended_title"] = generate_recommended_title(
        result["classification"], result["requested_levels"], allowed_level
    )

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Issue Title / Label / Comment Guard Validator")
    parser.add_argument("--title", help="Issue title")
    parser.add_argument("--body-file", help="File containing issue body")
    parser.add_argument("--body", help="Issue body text directly")
    parser.add_argument("--labels", help="Comma-separated labels")
    parser.add_argument("--fixture", help="JSON fixture file with title/body/labels")
    args = parser.parse_args()

    title = args.title
    body = args.body
    labels = None

    if args.body_file:
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()

    if args.labels:
        labels = [l.strip() for l in args.labels.split(",")]

    if args.fixture:
        with open(args.fixture, "r", encoding="utf-8") as f:
            fixture = json.load(f)
        title = fixture.get("title", title)
        body = fixture.get("body", body)
        labels = fixture.get("labels", labels)

    if not title and not body:
        print("Error: provide --title, --body/--body-file, or --fixture", file=sys.stderr)
        sys.exit(1)

    result = classify_issue_title_labels(title=title, body=body, labels=labels)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
