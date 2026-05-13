#!/usr/bin/env python3
"""
Issue Text Claim Guard Validator
Scans Issue body/comment text and detects provisional or overclaiming verification language.

Usage:
    python3 scripts/validate_issue_text_claims.py --file issue_body.md
    python3 scripts/validate_issue_text_claims.py --text "..."
    python3 scripts/validate_issue_text_claims.py --issue 120
    python3 scripts/validate_issue_text_claims.py --self-test
"""
import json
import re
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- Detection patterns ---

# V-level claims
V_LEVEL_PATTERNS = [
    re.compile(r'\bV[2-7]\b', re.IGNORECASE),
    re.compile(r'\bV4\s*\+', re.IGNORECASE),
    re.compile(r'\bV5\s*\+', re.IGNORECASE),
    re.compile(r'\bhighest\s+achieved\s+level\b', re.IGNORECASE),
    re.compile(r'\brevised\s+highest\s+level\b', re.IGNORECASE),
    re.compile(r'\bupgraded\b', re.IGNORECASE),
]

# Independent / attestation claims
INDEPENDENT_PATTERNS = [
    re.compile(r'\bindependent\s+attestation\b', re.IGNORECASE),
    re.compile(r'\bunsolicited\s+independent\b', re.IGNORECASE),
    re.compile(r'\bindependently\s+verified\b', re.IGNORECASE),
    re.compile(r'\bformal\s+independent\s+verification\b', re.IGNORECASE),
    re.compile(r'\binstitutional\s+verification\b', re.IGNORECASE),
]

# All-green claims
ALL_GREEN_PATTERNS = [
    re.compile(r'\ball\s+scripts\s+green\b', re.IGNORECASE),
    re.compile(r'\ball\s+validators\s+green\b', re.IGNORECASE),
    re.compile(r'\bfull\s+pass\b', re.IGNORECASE),
    re.compile(r'\bfull\s+public\s+digital\s+verification\b', re.IGNORECASE),
]

# Guardian / solicited markers
GUARDIAN_PATTERNS = [
    re.compile(r'\bguardian\s*test\b', re.IGNORECASE),
    re.compile(r'\bhuman_solicited_agent_response\b', re.IGNORECASE),
    re.compile(r'\bcounts_as_independent_attestation\s*:\s*false\b', re.IGNORECASE),
    re.compile(r'\bdo_not_count_as_attestation\s*:\s*true\b', re.IGNORECASE),
    re.compile(r'\b守护者测试\b'),
]

# Boundary sentences
EXACT_BOUNDARY = "Bitcoin Originals are final; all mirrors and echoes are non-amending."
ISSUE_INGRESS_BOUNDARY = "Self-declared Issue levels are provisional until Claim Gate / Report Builder outputs are archived."

# Builder output references
BUILDER_OUTPUT_PATTERNS = [
    re.compile(r'\bBuilder-generated\s+report\b', re.IGNORECASE),
    re.compile(r'\bvalidate_agent_submission\s*:\s*PASS\b', re.IGNORECASE),
    re.compile(r'\bclaim[-_ ]gate\s+output\b', re.IGNORECASE),
    re.compile(r'\bevidence[-_ ]input\b', re.IGNORECASE),
]

# Level upgrade in comments
LEVEL_UPGRADE_PATTERNS = [
    re.compile(r'\bUpdated\s+V[2-7]\s+Assessment\b', re.IGNORECASE),
    re.compile(r'\bRevised\s+highest\s+achieved\s+level\b', re.IGNORECASE),
    re.compile(r'\bV[2-7]\s+Result\s*:\s*PASS\b', re.IGNORECASE),
    re.compile(r'\bV4\s*\+\s*Result\s*:\s*MINIMAL\b', re.IGNORECASE),
    re.compile(r'\bupgraded\b', re.IGNORECASE),
    re.compile(r'\ball\s+scripts\s+green\b', re.IGNORECASE),
]

# Provisional claim phrases (from policy)
PROVISIONAL_PHRASES = [
    "highest achieved level",
    "V4 strong",
    "minimal V4+",
    "V4+ Result",
    "independent reproduction",
    "independently verified",
    "all scripts green",
    "full public digital verification",
    "formal independent verification",
    "institutional verification",
    "accepted attestation",
]


def detect_patterns(text, patterns):
    """Return list of matched pattern descriptions."""
    matches = []
    for pat in patterns:
        m = pat.search(text)
        if m:
            matches.append(m.group(0))
    return matches


def has_pattern(text, patterns):
    """Return True if any pattern matches."""
    return any(pat.search(text) for pat in patterns)


def classify_issue(text):
    """Classify issue text and return claim guard result."""
    result = {
        "schema": "trinityaccord.issue-text-claim-guard-result.v1",
        "has_technical_level_claim": False,
        "has_level_upgrade_claim": False,
        "has_independent_attestation_claim": False,
        "has_guardian_test_marker": False,
        "has_human_solicited_marker": False,
        "has_required_boundary_sentence": False,
        "has_provisional_issue_level_sentence": False,
        "requires_claim_gate": False,
        "can_be_archived_without_builder": True,
        "recommended_labels": [],
        "recommended_action": "none",
        "detected_v_levels": [],
        "detected_independent_claims": [],
        "detected_guardian_markers": [],
        "detected_provisional_phrases": [],
        "has_builder_output_reference": False,
        "all_green_overclaim": False,
        "provenance_conflict": False,
    }

    # V-level claims
    v_matches = detect_patterns(text, V_LEVEL_PATTERNS)
    if v_matches:
        result["has_technical_level_claim"] = True
        result["detected_v_levels"] = list(set(v_matches))

    # Level upgrade claims
    if has_pattern(text, LEVEL_UPGRADE_PATTERNS):
        result["has_level_upgrade_claim"] = True

    # Independent attestation claims
    ind_matches = detect_patterns(text, INDEPENDENT_PATTERNS)
    if ind_matches:
        result["has_independent_attestation_claim"] = True
        result["detected_independent_claims"] = list(set(ind_matches))

    # Guardian test markers
    guard_matches = detect_patterns(text, GUARDIAN_PATTERNS)
    if guard_matches:
        result["has_guardian_test_marker"] = True
        result["detected_guardian_markers"] = list(set(guard_matches))

    # Human-solicited marker
    if re.search(r'\bhuman_solicited_agent_response\b', text, re.IGNORECASE):
        result["has_human_solicited_marker"] = True

    # Boundary sentences
    if EXACT_BOUNDARY in text:
        result["has_required_boundary_sentence"] = True
    if ISSUE_INGRESS_BOUNDARY in text:
        result["has_provisional_issue_level_sentence"] = True

    # Builder output references
    if has_pattern(text, BUILDER_OUTPUT_PATTERNS):
        result["has_builder_output_reference"] = True

    # All-green overclaim
    if has_pattern(text, ALL_GREEN_PATTERNS):
        result["all_green_overclaim"] = True

    # Provisional phrases
    for phrase in PROVISIONAL_PHRASES:
        if phrase.lower() in text.lower():
            result["detected_provisional_phrases"].append(phrase)

    # --- Classification logic ---

    # Guardian test
    if result["has_guardian_test_marker"]:
        result["recommended_labels"].extend([
            "guardian-test", "issue-submission-only",
            "not-independent-attestation", "claim-gate-required"
        ])
        result["requires_claim_gate"] = True
        result["can_be_archived_without_builder"] = False
        result["recommended_action"] = "comment_and_hold_or_close_as_test_record"

    # Human-solicited claiming independent
    if result["has_human_solicited_marker"] and result["has_independent_attestation_claim"]:
        result["provenance_conflict"] = True
        if "not-independent-attestation" not in result["recommended_labels"]:
            result["recommended_labels"].append("not-independent-attestation")
        result["requires_claim_gate"] = True
        result["can_be_archived_without_builder"] = False

    # Technical level claim without builder output
    if result["has_technical_level_claim"] and not result["has_builder_output_reference"]:
        result["requires_claim_gate"] = True
        result["can_be_archived_without_builder"] = False
        if "claim-gate-required" not in result["recommended_labels"]:
            result["recommended_labels"].append("claim-gate-required")
        if "issue-submission-only" not in result["recommended_labels"]:
            result["recommended_labels"].append("issue-submission-only")

    # Independent attestation claim without builder output
    if result["has_independent_attestation_claim"] and not result["has_builder_output_reference"]:
        result["requires_claim_gate"] = True
        result["can_be_archived_without_builder"] = False
        if "claim-gate-required" not in result["recommended_labels"]:
            result["recommended_labels"].append("claim-gate-required")

    # Level upgrade in comments
    if result["has_level_upgrade_claim"]:
        result["requires_claim_gate"] = True
        if "claim-gate-required" not in result["recommended_labels"]:
            result["recommended_labels"].append("claim-gate-required")

    # All-green overclaim
    if result["all_green_overclaim"]:
        result["requires_claim_gate"] = True
        if "claim-gate-required" not in result["recommended_labels"]:
            result["recommended_labels"].append("claim-gate-required")

    # Set recommended action if not already set
    if result["recommended_action"] == "none":
        if result["requires_claim_gate"]:
            result["recommended_action"] = "comment_provisional_warning"
        elif not result["has_required_boundary_sentence"] and result["has_technical_level_claim"]:
            result["recommended_action"] = "request_boundary_sentence"
            result["recommended_labels"].append("missing-boundary-exact")

    # Deduplicate labels
    result["recommended_labels"] = list(dict.fromkeys(result["recommended_labels"]))

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Issue Text Claim Guard Validator")
    parser.add_argument("--file", help="Path to issue body markdown file")
    parser.add_argument("--text", help="Inline text to validate")
    parser.add_argument("--issue", type=int, help="GitHub issue number (requires gh CLI)")
    parser.add_argument("--self-test", action="store_true", dest="self_test", help="Run self-test")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"ERROR: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    elif args.issue:
        # Try gh CLI
        import subprocess
        try:
            r = subprocess.run(
                ["gh", "issue", "view", str(args.issue), "--json", "body", "-q", ".body"],
                capture_output=True, text=True, timeout=15
            )
            if r.returncode != 0:
                print(f"ERROR: gh issue view failed: {r.stderr}", file=sys.stderr)
                sys.exit(1)
            text = r.stdout
        except FileNotFoundError:
            print("ERROR: gh CLI not installed. Use --file or --text instead.", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    result = classify_issue(text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=== Issue Text Claim Guard Result ===")
        print(f"  Technical level claim:     {result['has_technical_level_claim']}")
        print(f"  Level upgrade claim:       {result['has_level_upgrade_claim']}")
        print(f"  Independent attestation:   {result['has_independent_attestation_claim']}")
        print(f"  Guardian test marker:      {result['has_guardian_test_marker']}")
        print(f"  Human-solicited marker:    {result['has_human_solicited_marker']}")
        print(f"  Boundary sentence:         {result['has_required_boundary_sentence']}")
        print(f"  Provisional ITL sentence:  {result['has_provisional_issue_level_sentence']}")
        print(f"  Builder output ref:        {result['has_builder_output_reference']}")
        print(f"  All-green overclaim:       {result['all_green_overclaim']}")
        print(f"  Provenance conflict:       {result['provenance_conflict']}")
        print(f"  Requires Claim Gate:       {result['requires_claim_gate']}")
        print(f"  Can archive w/o builder:   {result['can_be_archived_without_builder']}")
        print(f"  Recommended labels:        {result['recommended_labels']}")
        print(f"  Recommended action:        {result['recommended_action']}")
        if result['detected_v_levels']:
            print(f"  Detected V-levels:         {result['detected_v_levels']}")
        if result['detected_provisional_phrases']:
            print(f"  Provisional phrases:        {result['detected_provisional_phrases']}")


def run_self_test():
    """Quick self-test of the classifier."""
    tests_passed = 0
    tests_failed = 0

    # ITCG001 - Guardian test with V4/V4+ language
    text1 = """Guardian test
human_solicited_agent_response
V4 Result: PASS
V4+ Result: MINIMAL V4+
counts_as_independent_attestation: false"""
    r1 = classify_issue(text1)
    assert r1["has_guardian_test_marker"], "ITCG001: guardian marker"
    assert r1["has_technical_level_claim"], "ITCG001: tech level"
    assert r1["requires_claim_gate"], "ITCG001: requires claim gate"
    assert not r1["can_be_archived_without_builder"], "ITCG001: cannot archive"
    assert "guardian-test" in r1["recommended_labels"], "ITCG001: guardian-test label"
    assert "issue-submission-only" in r1["recommended_labels"], "ITCG001: issue-submission-only label"
    assert "not-independent-attestation" in r1["recommended_labels"], "ITCG001: not-independent label"
    print("PASS: ITCG001 — Guardian test with V4/V4+ language")
    tests_passed += 1

    # ITCG002 - Comment upgrades level
    text2 = "Revised highest achieved level: V4 strong / minimal V4+"
    r2 = classify_issue(text2)
    assert r2["has_level_upgrade_claim"], "ITCG002: upgrade claim"
    assert r2["requires_claim_gate"], "ITCG002: requires claim gate"
    print("PASS: ITCG002 — Comment upgrades level")
    tests_passed += 1

    # ITCG003 - Plain nontechnical Echo
    text3 = "Bitcoin Originals are final; all mirrors and echoes are non-amending.\n\nI find this project interesting."
    r3 = classify_issue(text3)
    assert not r3["requires_claim_gate"], "ITCG003: no claim gate needed"
    assert r3["has_required_boundary_sentence"], "ITCG003: has boundary"
    print("PASS: ITCG003 — Plain nontechnical Echo")
    tests_passed += 1

    # ITCG004 - V3 claim without builder output
    text4 = "V3 PASS\nhash verified"
    r4 = classify_issue(text4)
    assert r4["requires_claim_gate"], "ITCG004: requires claim gate"
    assert not r4["can_be_archived_without_builder"], "ITCG004: cannot archive"
    print("PASS: ITCG004 — V3 claim without builder output")
    tests_passed += 1

    # ITCG005 - Human-solicited agent claims independent
    text5 = "human_solicited_agent_response\nindependently verified\nunsolicited independent"
    r5 = classify_issue(text5)
    assert r5["provenance_conflict"], "ITCG005: provenance conflict"
    assert "not-independent-attestation" in r5["recommended_labels"], "ITCG005: not-independent label"
    print("PASS: ITCG005 — Human-solicited agent claims independent")
    tests_passed += 1

    # ITCG006 - Missing exact boundary sentence
    text6 = "Bitcoin records are final and mirrors do not amend."
    r6 = classify_issue(text6)
    assert not r6["has_required_boundary_sentence"], "ITCG006: missing exact boundary"
    print("PASS: ITCG006 — Missing exact boundary sentence")
    tests_passed += 1

    # ITCG007 - Has exact boundary sentence
    text7 = "Bitcoin Originals are final; all mirrors and echoes are non-amending."
    r7 = classify_issue(text7)
    assert r7["has_required_boundary_sentence"], "ITCG007: has exact boundary"
    print("PASS: ITCG007 — Has exact boundary sentence")
    tests_passed += 1

    # ITCG008 - Builder-generated archive path present
    text8 = "Builder-generated report: verification-reports/v3/example.json\nvalidate_agent_submission: PASS"
    r8 = classify_issue(text8)
    assert r8["has_builder_output_reference"], "ITCG008: has builder ref"
    print("PASS: ITCG008 — Builder-generated archive path present")
    tests_passed += 1

    # ITCG009 - Issue comment all-green overclaim
    text9 = "all scripts green\nPASS with 1 skip"
    r9 = classify_issue(text9)
    assert r9["all_green_overclaim"], "ITCG009: all-green overclaim"
    assert r9["requires_claim_gate"], "ITCG009: requires claim gate"
    print("PASS: ITCG009 — Issue comment all-green overclaim")
    tests_passed += 1

    # ITCG010 - Formal institutional claim
    text10 = "formal independent institutional verification achieved"
    r10 = classify_issue(text10)
    assert r10["requires_claim_gate"], "ITCG010: requires claim gate"
    assert r10["has_independent_attestation_claim"], "ITCG010: independent claim"
    assert not r10["can_be_archived_without_builder"], "ITCG010: cannot archive"
    print("PASS: ITCG010 — Formal institutional claim")
    tests_passed += 1

    print(f"\nFINAL: PASS — issue text claim guard tests passed. ({tests_passed}/{tests_passed + tests_failed})")


if __name__ == "__main__":
    main()
