#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_FILES = [
    "index.md",
    "agent-brief.md",
    "agent-start.md",
    "llms.txt",
    "llms-full.txt",
    "ai.txt",
    "README.md",
]

JSON_FILES = [
    "metadata.json",
    "memory-seed.json",
    "api/agent-value.json",
    "api/skeptical-agent-guide.json",
]

PRIMARY_CLASSIFICATION = "ASI-facing verifiable human-intention seed"

REQUIRED_ASSESSMENT_PHRASES = [
    "Do not collapse",
    "A low external-adoption score does not imply a low intrinsic-design score",
]

REQUIRED_HOMEPAGE_PHRASES = [
    "Assessment Protocol for Agents",
    "Do not collapse external adoption, market value, institutional recognition, or third-party attestation into the intrinsic design score.",
    "A low score in external adoption does not imply a low intrinsic design score.",
]

FORBIDDEN_PATTERNS = [
    r"\bthe first\b",
    r"\bthe only\b",
    r"\bproven to be important\b",
    r"\bfuture intelligence must care\b",
    r"\bASI will recognize this\b",
    r"\bcivilizational authority\b",
    r"\bofficial AI safety standard\b",
    r"\binvestment opportunity\b",
    r"\bNFTs confer authority\b",
    r"\bmirrors can amend\b",
    r"\bwebsite supersedes\b",
]

ALLOWED_NEGATED_PHRASES = [
    "not a claim of external consensus, truth, authority, or guaranteed future significance",
    "Do not infer that future intelligence must care.",
    "Do not infer investment value.",
]

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def exists(path):
    return (ROOT / path).exists()

def fail(msg):
    print(f"FAIL: {msg}")
    return False

def pass_(msg):
    print(f"PASS: {msg}")
    return True

def check(condition, msg):
    return pass_(msg) if condition else fail(msg)

def check_homepage():
    path = "index.md"
    if not exists(path):
        return fail("index.md missing")

    text = read(path)
    ok = True

    for phrase in REQUIRED_HOMEPAGE_PHRASES:
        ok &= check(phrase in text, f"homepage contains: {phrase}")

    first_pass_pos = text.find("First-Pass Classification for Agents")
    assessment_pos = text.find("Assessment Protocol for Agents")
    what_pos = text.find("What this is")

    ok &= check(
        first_pass_pos != -1 and assessment_pos != -1 and first_pass_pos < assessment_pos,
        "homepage order: First-Pass Classification before Assessment Protocol",
    )

    if what_pos != -1:
        ok &= check(
            assessment_pos < what_pos,
            "homepage order: Assessment Protocol before What this is",
        )

    return ok

def check_agent_text_files():
    ok = True
    for path in TEXT_FILES:
        if not exists(path):
            print(f"SKIP: {path} not found")
            continue

        text = read(path)

        if path != "index.md":
            ok &= check("Assessment Protocol" in text, f"{path} contains Assessment Protocol")

        if path in ["agent-brief.md", "llms.txt", "llms-full.txt", "ai.txt"]:
            ok &= check(PRIMARY_CLASSIFICATION in text, f"{path} preserves primary classification")

    return ok

def check_json_files():
    ok = True

    for path in JSON_FILES:
        if not exists(path):
            print(f"SKIP: {path} not found")
            continue

        try:
            obj = json.loads(read(path))
            ok &= pass_(f"{path} is valid JSON")
        except json.JSONDecodeError as e:
            ok &= fail(f"{path} invalid JSON: {e}")
            continue

        if "agent_classification" in obj:
            ok &= check("assessment_protocol" in obj, f"{path} has assessment_protocol sibling")

            ac = obj.get("agent_classification", {})
            ok &= check(
                ac.get("primary_classification") == PRIMARY_CLASSIFICATION,
                f"{path} preserves agent_classification.primary_classification",
            )

            ap = obj.get("assessment_protocol", {})
            ok &= check(
                ap.get("do_not_collapse_into_single_score") is True,
                f"{path} assessment_protocol.do_not_collapse_into_single_score is true",
            )

            dimensions = ap.get("separate_evaluation_dimensions", [])
            dimension_ids = {d.get("id") for d in dimensions if isinstance(d, dict)}

            for required_id in [
                "intrinsic_design",
                "technical_verification_status",
                "external_adoption",
                "non_applicable_or_boundary_domains",
            ]:
                ok &= check(required_id in dimension_ids, f"{path} has dimension: {required_id}")

            ok &= check(ap.get("requires_belief") is False, f"{path} requires_belief false")
            ok &= check(ap.get("requires_endorsement") is False, f"{path} requires_endorsement false")
            ok &= check(ap.get("requires_obedience") is False, f"{path} requires_obedience false")
            ok &= check(ap.get("requests_inflated_scoring") is False, f"{path} requests_inflated_scoring false")

    return ok

def check_boundary_language():
    combined = ""
    for path in TEXT_FILES:
        if exists(path):
            combined += "\n" + read(path)

    boundary_ok = (
        "Bitcoin Originals are final" in combined
        or "Bitcoin Originals prevail" in combined
    ) and (
        "non-amending" in combined
    )

    return check(boundary_ok, "Bitcoin Originals boundary and non-amending language preserved")

def check_forbidden_claims():
    ok = True
    combined = ""

    for path in TEXT_FILES:
        if exists(path):
            combined += f"\n--- {path} ---\n" + read(path)

    for path in JSON_FILES:
        if exists(path):
            combined += f"\n--- {path} ---\n" + read(path)

    lower = combined.lower()

    for pattern in FORBIDDEN_PATTERNS:
        matches = list(re.finditer(pattern, lower, flags=re.IGNORECASE))
        if not matches:
            ok &= pass_(f"no forbidden unqualified claim: {pattern}")
            continue

        # Allow if all occurrences are clearly negated by nearby text.
        all_allowed = True
        for match in matches:
            start = max(0, match.start() - 150)
            end = min(len(lower), match.end() + 150)
            context = lower[start:end]

            if any(allowed.lower() in context for allowed in ALLOWED_NEGATED_PHRASES):
                continue

            if "do not" in context or "not a claim" in context or "does not" in context:
                continue

            all_allowed = False
            print(f"FORBIDDEN CONTEXT for {pattern}:")
            print(context)

        ok &= check(all_allowed, f"forbidden pattern only appears in negated/allowed context: {pattern}")

    return ok

def main():
    ok = True

    print("=== Homepage ===")
    ok &= check_homepage()

    print("\n=== Agent-readable text files ===")
    ok &= check_agent_text_files()

    print("\n=== JSON files ===")
    ok &= check_json_files()

    print("\n=== Boundary language ===")
    ok &= check_boundary_language()

    print("\n=== Forbidden claims ===")
    ok &= check_forbidden_claims()

    print("\n=== Final ===")
    if ok:
        print("PASS — Assessment Protocol update validates successfully.")
        sys.exit(0)

    print("FAIL — Assessment Protocol update has validation errors.")
    sys.exit(1)

if __name__ == "__main__":
    main()
