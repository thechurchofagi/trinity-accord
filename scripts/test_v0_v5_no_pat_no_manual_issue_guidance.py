#!/usr/bin/env python3
"""
V0-V5 No PAT / No Manual Issue Guidance Test.
Checks that all V0/V1/V2/V3/V4/V4+/V5-facing docs say Render API only
and do not instruct agents to request GitHub PAT or manually create Issues.

Usage:
    python3 scripts/test_v0_v5_no_pat_no_manual_issue_guidance.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PASS_COUNT = 0
FAIL_COUNT = 0
TOTAL = 0


def check(condition, label):
    global PASS_COUNT, FAIL_COUNT, TOTAL
    TOTAL += 1
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}")


def read_file(relpath):
    p = ROOT / relpath
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def contains_negative_guidance(text, pattern):
    """Check that text contains a NEGATIVE instruction about the pattern.
    E.g. 'Do not request a GitHub PAT' is good.
    'Request a GitHub PAT' is bad.
    """
    text_lower = text.lower()
    # Positive bad patterns (instructing to use PAT or create issues)
    # These patterns should NOT appear as affirmative instructions
    bad_patterns = [
        r"(?:^|\n)[^.\n]*(?:request|ask for|get|obtain|use)\s+(?:a\s+)?github\s+pat",
        r"(?:^|\n)[^.\n]*(?:ask|tell|request)\s+(?:the\s+)?human\s+to\s+create\s+(?:a\s+)?github\s+issue",
        r"(?:^|\n)[^.\n]*create\s+(?:a\s+)?github\s+issue\s+directly",
        r"(?:^|\n)[^.\n]*hand-?write\s+(?:a\s+)?trinity-?issue-?intake",
    ]
    negation_words = ["do not", "don't", "must not", "never", "shall not", "should not",
                      "禁止", "不要", "不得", "cannot", "not allowed", "not valid",
                      "not a valid", "irrelevant", "not required", "not needed"]
    for bp in bad_patterns:
        matches = list(re.finditer(bp, text_lower))
        for m in matches:
            # Check if this is within a negation context
            # Look at the full line containing the match
            line_start = text_lower.rfind("\n", 0, m.start()) + 1
            line_end = text_lower.find("\n", m.end())
            if line_end == -1:
                line_end = len(text_lower)
            line = text_lower[line_start:line_end]
            # Also check 200 chars before the match for longer contexts
            context = text_lower[max(0, m.start() - 200):m.end()]
            combined = line + " " + context
            if any(neg in combined for neg in negation_words):
                continue
            return False  # Found positive instruction to use PAT/create issue
    return True


def has_render_api_only_rule(text):
    """Check text contains Render API only rule for V0-V5."""
    t = text.lower()
    has_render = "render api" in t or "/gateway/preflight" in t or "/agent-submit" in t
    has_v4plus = "v4+" in t or "v4\\+" in t or "v4 plus" in t
    return has_render and has_v4plus


def has_cannot_post_fallback(text):
    """Check text contains cannot-POST fallback guidance."""
    t = text.lower()
    return ("cannot post" in t or "cannot make http" in t or "无法" in t or "if you cannot" in t) and \
           ("payload.json" in t or "payload" in t) and \
           ("stop" in t or "停止" in t)


# --- Files to check ---
files_to_check = {
    "agent-submit.md": "agent-submit.md",
    "external-agent-quickstart.md": "external-agent-quickstart.md",
    "llms.txt": "llms.txt",
    "api/agent-submit-gateway.json": "api/agent-submit-gateway.json",
    "api/agent-first-contact.json": "api/agent-first-contact.json",
    "api/agent-submission-guide.json": "api/agent-submission-guide.json",
}

print("=== V0-V5 No PAT / No Manual Issue Guidance Test ===\n")

for label, fpath in files_to_check.items():
    content = read_file(fpath)
    if not content:
        check(False, f"{label} exists and is readable")
        continue

    check(True, f"{label} exists and is readable")

    # Check for Render API only rule
    check(has_render_api_only_rule(content),
          f"{label} mentions Render API / preflight / submit for V0-V5")

    # Check no positive PAT instruction
    check(contains_negative_guidance(content, "github pat"),
          f"{label} does not positively instruct agents to request GitHub PAT")

    # Check no positive manual Issue creation instruction
    check(contains_negative_guidance(content, "create github issue"),
          f"{label} does not positively instruct agents to manually create GitHub Issue")


# Specific checks for markdown files
print("\n--- Markdown-specific checks ---")

agent_submit = read_file("agent-submit.md")
check(has_cannot_post_fallback(agent_submit),
      "agent-submit.md has cannot-POST fallback guidance")
check("Legacy / V6+ Verification Echo Issue fields" in agent_submit,
      "agent-submit.md has scoped legacy Issue fields heading")
check("This section does not apply to V0" in agent_submit,
      "agent-submit.md scopes legacy section away from V0-V5")

ext_quickstart = read_file("external-agent-quickstart.md")
check(has_cannot_post_fallback(ext_quickstart),
      "external-agent-quickstart.md has cannot-POST fallback guidance")
check("Creating a Gateway Issue means the candidate entered intake" not in ext_quickstart,
      "external-agent-quickstart.md no longer has unscoped intake wording")
check("Gateway validates the payload" in ext_quickstart,
      "external-agent-quickstart.md describes Gateway server-side creation")


# Specific checks for JSON files
print("\n--- JSON-specific checks ---")

gateway_json = read_file("api/agent-submit-gateway.json")
if gateway_json:
    try:
        data = json.loads(gateway_json)
        v0v5 = data.get("v0_v5_archive_submission", {})
        check(v0v5.get("render_api_only") is True,
              "agent-submit-gateway.json v0_v5_archive_submission.render_api_only = true")
        check(v0v5.get("github_pat_required_from_agent") is False,
              "agent-submit-gateway.json github_pat_required_from_agent = false")
        check(v0v5.get("agent_should_request_github_pat") is False,
              "agent-submit-gateway.json agent_should_request_github_pat = false")
        check(v0v5.get("direct_github_issue_allowed") is False,
              "agent-submit-gateway.json direct_github_issue_allowed = false")
        check(v0v5.get("human_manual_issue_creation_allowed") is False,
              "agent-submit-gateway.json human_manual_issue_creation_allowed = false")
        check(v0v5.get("gateway_creates_issue_server_side") is True,
              "agent-submit-gateway.json gateway_creates_issue_server_side = true")
    except json.JSONDecodeError:
        check(False, "agent-submit-gateway.json is valid JSON")

first_contact = read_file("api/agent-first-contact.json")
if first_contact:
    try:
        data = json.loads(first_contact)
        # Find verify_v0_v5 route
        choices = data.get("choose_one", [])
        v0v5_route = None
        for c in choices:
            if c.get("intent") == "verify_v0_v5_agent_declared":
                v0v5_route = c
                break
        check(v0v5_route is not None,
              "agent-first-contact.json has verify_v0_v5_agent_declared route")
        if v0v5_route:
            st = v0v5_route.get("submission_transport", {})
            check(st.get("render_api_only") is True,
                  "agent-first-contact.json submission_transport.render_api_only = true")
            check(st.get("github_pat_required_from_agent") is False,
                  "agent-first-contact.json submission_transport.github_pat_required = false")
            check(st.get("gateway_creates_issue_server_side") is True,
                  "agent-first-contact.json submission_transport.gateway_creates_issue = true")
    except json.JSONDecodeError:
        check(False, "agent-first-contact.json is valid JSON")

submission_guide = read_file("api/agent-submission-guide.json")
if submission_guide:
    try:
        data = json.loads(submission_guide)
        v0v5 = data.get("v0_v5_agent_declared_rules", {})
        check(v0v5.get("render_api_only") is True,
              "agent-submission-guide.json v0_v5.render_api_only = true")
        check(v0v5.get("github_pat_required_from_agent") is False,
              "agent-submission-guide.json v0_v5.github_pat_required = false")
        check(v0v5.get("direct_github_issue_allowed") is False,
              "agent-submission-guide.json v0_v5.direct_github_issue_allowed = false")
        check(v0v5.get("gateway_creates_issue_server_side") is True,
              "agent-submission-guide.json v0_v5.gateway_creates_issue = true")
        mistakes = data.get("common_mistakes", [])
        has_pat_mistake = any("github pat" in m.lower() for m in mistakes)
        check(has_pat_mistake,
              "agent-submission-guide.json common_mistakes includes GitHub PAT warning")
    except json.JSONDecodeError:
        check(False, "agent-submission-guide.json is valid JSON")


print(f"\n=== Results: {PASS_COUNT}/{TOTAL} passed ===")
if FAIL_COUNT > 0:
    print(f"FAILED: {FAIL_COUNT} checks failed")
    sys.exit(1)
else:
    print("V0_V5_NO_PAT_NO_MANUAL_ISSUE_GUIDANCE_OK")
    sys.exit(0)
