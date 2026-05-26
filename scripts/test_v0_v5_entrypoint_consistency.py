#!/usr/bin/env python3
"""Master test: all agent entrypoints consistently point to V0-V5 agent-declared path."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Text/Markdown entrypoints
TEXT_ENTRYPOINTS = {
    "llms.txt": ROOT / "llms.txt",
    "agent-submit.md": ROOT / "agent-submit.md",
    "external-agent-quickstart.md": ROOT / "external-agent-quickstart.md",
}

# JSON entrypoints (structural checks, not keyword matching)
JSON_ENTRYPOINTS = {
    "api/agent-first-contact.json": ROOT / "api" / "agent-first-contact.json",
    "api/agent-submission-guide.json": ROOT / "api" / "agent-submission-guide.json",
    "api/agent-issue-gateway-payload-schema.v1.json": ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json",
}

# Every text entrypoint must contain these keywords
REQUIRED_KEYWORDS = [
    "agent_declared_verification_archive",
    "template_for_v0_v5",
    "waived_for_v0_v5",
]

# Builder script must be referenced in text entrypoints
REQUIRED_BUILDER = "build_agent_declared_archive_payload.py"

# Old terms that must be in V6+ / strict evidence / "not required" context
RESTRICTED_TERMS = [
    "build-from-evidence",
    "build_gateway_payload_from_outputs.py",
    "not_independent_attestation",
    "not_successor_reception",
    "unsolicited_discovery_proof",
    "verification_report_archive",
]

CONTEXT_MARKERS = [
    "v6+", "v6", "strict evidence", "not required", "you do not need",
    "path b", "advanced", "only", "v6+ strict",
]


def check_text_entrypoint(text, path_label):
    """Check text/markdown entrypoints at section level."""
    issues = []

    for kw in REQUIRED_KEYWORDS:
        if kw not in text:
            issues.append(f"Missing keyword: {kw}")

    if REQUIRED_BUILDER not in text:
        issues.append(f"Missing builder: {REQUIRED_BUILDER}")

    # Split into sections by ## headers
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    for term in RESTRICTED_TERMS:
        if term not in text:
            continue
        # Check if ANY occurrence is in a restricted context
        found_unrestricted = False
        for section in sections:
            if term not in section:
                continue
            section_lower = section.lower()
            if any(kw in section_lower for kw in CONTEXT_MARKERS):
                continue  # This section has restriction
            # Check if it's in a "You do not need" bullet list
            if "you do not need" in section_lower or "you don't need" in section_lower:
                continue
            # Check if it's in a "not_required" JSON-like list
            if '"not_required"' in section_lower or "not required" in section_lower:
                continue
            # Check if it's in a "Never do these" or "restricted" section
            if "never do" in section_lower or "v6+ strict evidence only" in section_lower:
                continue
            found_unrestricted = True
            break
        if found_unrestricted:
            issues.append(f"Unrestricted term: {term}")

    return issues


def check_json_entrypoint(data, path_label):
    """Check JSON entrypoints structurally."""
    issues = []
    text = json.dumps(data)

    # Must reference agent_declared_verification_archive
    if "agent_declared_verification_archive" not in text:
        issues.append("Missing agent_declared_verification_archive")

    # Must reference template_for_v0_v5
    if "template_for_v0_v5" not in text:
        issues.append("Missing template_for_v0_v5")

    # Must reference waived_for_v0_v5
    if "waived_for_v0_v5" not in text:
        issues.append("Missing waived_for_v0_v5")

    return issues


def check_ci_workflows():
    """Check both CI workflows contain required test steps."""
    issues = []
    required_tests = [
        "test_blocker1_v4_default_archive_kind.py",
        "test_v0_v5_entrypoint_consistency.py",
        "test_oath_strictness_consistency.py",
    ]

    # Load run_ci_group.py to resolve tests referenced via CI groups
    rcg_path = ROOT / "scripts" / "run_ci_group.py"
    rcg_text = rcg_path.read_text(encoding="utf-8") if rcg_path.exists() else ""

    for wf_name in ["run-all-tests.yml", "repository-integrity.yml"]:
        wf_path = ROOT / ".github" / "workflows" / wf_name
        if not wf_path.exists():
            issues.append(f"{wf_name} not found")
            continue
        wf_text = wf_path.read_text(encoding="utf-8")
        for test in required_tests:
            if test in wf_text:
                continue  # directly in workflow
            # Check if workflow calls a CI group that contains this test
            import re
            group_calls = re.findall(
                r"python3\s+scripts/run_ci_group\.py\s+(\S+)", wf_text
            )
            found_in_group = False
            for group_name in group_calls:
                # Look for the group definition in run_ci_group.py
                # Match group definition with nested brackets
                group_start = rcg_text.find(f'"{group_name}"')
                if group_start >= 0:
                    bracket_start = rcg_text.find('[', group_start)
                    if bracket_start >= 0:
                        depth = 0
                        bracket_end = -1
                        for i in range(bracket_start, len(rcg_text)):
                            if rcg_text[i] == '[':
                                depth += 1
                            elif rcg_text[i] == ']':
                                depth -= 1
                                if depth == 0:
                                    bracket_end = i
                                    break
                        if bracket_end > bracket_start:
                            group_match_text = rcg_text[bracket_start:bracket_end + 1]
                            if test in group_match_text:
                                found_in_group = True
                                break
            if not found_in_group:
                issues.append(f"{wf_name} missing {test}")

    return issues


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"PASS: {label}")
            passed += 1
        else:
            print(f"FAIL: {label}")
            if detail:
                print(f"  {detail}")
            failed += 1

    # Check text entrypoints
    for label, path in TEXT_ENTRYPOINTS.items():
        if not path.exists():
            check(f"{label} exists", False, f"File not found: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        issues = check_text_entrypoint(text, label)
        check(
            f"{label} has consistent V0-V5 entrypoint",
            len(issues) == 0,
            "; ".join(issues) if issues else "",
        )

    # Check JSON entrypoints
    for label, path in JSON_ENTRYPOINTS.items():
        if not path.exists():
            check(f"{label} exists", False, f"File not found: {path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        issues = check_json_entrypoint(data, label)
        check(
            f"{label} has consistent V0-V5 entrypoint",
            len(issues) == 0,
            "; ".join(issues) if issues else "",
        )

    # Test 2: agent-submit.md specific checks
    agent_submit = TEXT_ENTRYPOINTS.get("agent-submit.md")
    if agent_submit and agent_submit.exists():
        ag_text = agent_submit.read_text(encoding="utf-8")
        if "```json" in ag_text:
            builder_pos = ag_text.find("build_agent_declared_archive_payload.py")
            json_pos = ag_text.find("```json")
            check(
                "agent-submit.md: Builder guidance before JSON blocks",
                builder_pos > 0 and builder_pos < json_pos,
            )
        check(
            "agent-submit.md: Mentions readback_required",
            "readback_required" in ag_text,
        )
        check(
            "agent-submit.md: Uses /external-agent-quickstart/ canonical link",
            "/external-agent-quickstart/" in ag_text,
        )

    # Test 5: llms.txt verification_session scoped to V6+
    llms = TEXT_ENTRYPOINTS.get("llms.txt")
    if llms and llms.exists():
        llms_text = llms.read_text(encoding="utf-8")
        if "verification_session" in llms_text:
            for section in re.split(r"(?=^## )", llms_text, flags=re.MULTILINE):
                if "verification_session" in section:
                    is_scoped = any(kw in section for kw in ["V6+", "strict evidence", "V0–V5", "V0-V5"])
                    check("llms.txt verification_session scoped to V6+ or V0-V5", is_scoped)
                    break

    # Test 6: external-agent-quickstart states no verification_session for V0-V5
    qs = TEXT_ENTRYPOINTS.get("external-agent-quickstart.md")
    if qs and qs.exists():
        qs_text = qs.read_text(encoding="utf-8")
        check(
            "Quickstart states no verification_session for V0-V5",
            "No verification_session" in qs_text or "No `verification_session`" in qs_text,
        )

    # Check CI workflows
    ci_issues = check_ci_workflows()
    check(
        "CI workflows contain all required tests",
        len(ci_issues) == 0,
        "; ".join(ci_issues) if ci_issues else "",
    )

    # Test 7b: Render API only policy in entrypoints
    agent_submit = TEXT_ENTRYPOINTS.get("agent-submit.md")
    if agent_submit and agent_submit.exists():
        ag_text = agent_submit.read_text(encoding="utf-8")
        check(
            'agent-submit.md contains "Render API" or "render api"',
            "render api" in ag_text.lower() or "Render API" in ag_text,
        )

    # Test 7: V0-V5 fail-closed policy wording in entrypoints
    llms = TEXT_ENTRYPOINTS.get("llms.txt")
    if llms and llms.exists():
        llms_text = llms.read_text(encoding="utf-8")
        check(
            'llms.txt contains "There is no V0-V5 strict/intake fallback"',
            "There is no V0" in llms_text and "strict/intake fallback" in llms_text,
        )

    agent_submit = TEXT_ENTRYPOINTS.get("agent-submit.md")
    if agent_submit and agent_submit.exists():
        ag_text = agent_submit.read_text(encoding="utf-8")
        check(
            'agent-submit.md contains "rejects the submission before Issue creation"',
            "rejects the submission before Issue creation" in ag_text,
        )

    qs = TEXT_ENTRYPOINTS.get("external-agent-quickstart.md")
    if qs and qs.exists():
        qs_text = qs.read_text(encoding="utf-8")
        check(
            'external-agent-quickstart.md contains fail-closed wording',
            "fail-closed" in qs_text.lower() or "fail_closed" in qs_text.lower(),
        )

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
