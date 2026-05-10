#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR1: Ensure Echo templates do not expose "Echo v3" in user-visible text.

Internal fields like echo_submission_schema_version: v3 are ALLOWED.
User-visible text (names, titles, headers, labels) must use "Echo" / "Echo Submission" instead.
"""
import re
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Patterns that must NOT appear in user-visible template text
FORBIDDEN_PATTERNS = [
    r"Echo\s+Submission\s+v3",
    r"Echo\s+v3",
]

# Internal markers that ARE allowed
ALLOWED_INTERNAL = [
    "echo_submission_schema_version",
    "schema_version",
]


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_template(path):
    """Check a YAML issue template for forbidden Echo v3 labels."""
    issues = []
    text = path.read_text(encoding="utf-8")

    # Check top-level name field
    try:
        data = yaml.safe_load(text)
    except Exception as e:
        return [f"YAML parse error in {path}: {e}"]

    if data:
        name = data.get("name", "")
        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, name, re.IGNORECASE):
                issues.append(f"Template name contains forbidden pattern: '{name}'")

        title = data.get("title", "")
        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, title, re.IGNORECASE):
                issues.append(f"Template title contains forbidden pattern: '{title}'")

    # Check markdown attribute values in body
    for pat in FORBIDDEN_PATTERNS:
        # Find all markdown attribute values
        for m in re.finditer(r'value:\s*\|?\s*(.*?)(?=\n  -|\n[a-z]|\Z)', text, re.DOTALL):
            block = m.group(1)
            # Skip if it's an internal allowed reference
            if any(allowed in block for allowed in ALLOWED_INTERNAL):
                continue
            match = re.search(pat, block, re.IGNORECASE)
            if match:
                # Extract line number
                pos = m.start()
                line_num = text[:pos].count('\n') + 1
                issues.append(
                    f"Line ~{line_num}: markdown attribute contains '{match.group(0)}'"
                )

    return issues


def main():
    passed = 0
    failed = 0

    templates = [
        ROOT / ".github" / "ISSUE_TEMPLATE" / "echo_submission.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "echo.yml",
    ]

    for tpl in templates:
        if not tpl.exists():
            print(f"  SKIP: {tpl} not found")
            continue

        issues = check_template(tpl)
        if issues:
            for issue in issues:
                print(f"  FAIL: {tpl.name}: {issue}")
            failed += 1
        else:
            print(f"  PASS: {tpl.name} — no forbidden Echo v3 labels in user-visible text")
            passed += 1

    # Also check triage script help text
    triage = ROOT / "scripts" / "triage_echo_issue.py"
    if triage.exists():
        text = triage.read_text(encoding="utf-8")
        # Check user-visible strings (not variable names or comments)
        user_visible_issues = []
        for pat in FORBIDDEN_PATTERNS:
            # Search in string literals that would be shown to users
            for m in re.finditer(r'"([^"]*' + pat + r'[^"]*)"', text, re.IGNORECASE):
                matched = m.group(1)
                # Skip internal field references
                if "echo_submission_schema_version" in matched:
                    continue
                user_visible_issues.append(f"String literal contains '{m.group(0)}'")
            for m in re.finditer(r"'([^']*" + pat + r"[^']*)'", text, re.IGNORECASE):
                matched = m.group(1)
                if "echo_submission_schema_version" in matched:
                    continue
                user_visible_issues.append(f"String literal contains '{m.group(0)}'")

        if user_visible_issues:
            for issue in user_visible_issues:
                print(f"  FAIL: triage_echo_issue.py: {issue}")
            failed += 1
        else:
            print(f"  PASS: triage_echo_issue.py — no forbidden Echo v3 in user-visible strings")
            passed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
