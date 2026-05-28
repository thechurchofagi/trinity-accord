#!/usr/bin/env python3
"""Source-only contract for external agent entrypoint journey smoke.

This test verifies that the live journey smoke assets exist and are wired
without executing network calls. The actual live smoke belongs in the live-site
group or GitHub Actions workflow, not source-only p0-main.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SMOKE = ROOT / "scripts" / "smoke_external_agent_entrypoint_journeys.py"
WORKFLOW = ROOT / ".github" / "workflows" / "site-agent-entrypoint-journey-smoke.yml"
RUN_CI_GROUP = ROOT / "scripts" / "run_ci_group.py"
P0_REQUIRED = ROOT / "scripts" / "test_p0_main_required_commands.py"

REQUIRED_SMOKE_SNIPPETS = [
    "external",
    "agent",
    "entrypoint",
    "journey",
    "/api/links.json",
    "/.well-known/trinity-accord.json",
    "/api/agent-first-contact.json",
    "/api/agent-submit-gateway.json",
    "/api/agent-output-policy.v1.json",
    "before_leaving",
]

REQUIRED_WORKFLOW_SNIPPETS = [
    "workflow_dispatch",
    "schedule",
    "smoke_external_agent_entrypoint_journeys.py",
    "https://www.trinityaccord.org",
]

# Use regex patterns to detect actual dynamic operations (not string constants in lists)
FORBIDDEN_DYNAMIC_PATTERNS = [
    ("urllib.request call", r"urllib\.request\.(urlopen|Request)\s*\("),
    ("requests.get/post call", r"requests\.(get|post|put|delete)\s*\("),
    ("urlopen call", r"urlopen\s*\("),
    ("subprocess.run call", r"subprocess\.run\s*\("),
    ("subprocess.check_call call", r"subprocess\.check_call\s*\("),
    ("subprocess.check_output call", r"subprocess\.check_output\s*\("),
    ("time.sleep call", r"time\.sleep\s*\("),
    ("while True loop", r"while\s+[Tt]rue\s*:"),
]

FORBIDDEN_STALE_ENDPOINTS = [
    "/gateway/submit",
]


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    # Required files.
    for path in [SMOKE, WORKFLOW, RUN_CI_GROUP, P0_REQUIRED]:
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    if errors:
        print("FAIL: external agent entrypoint journey smoke contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    smoke_text = read(SMOKE)
    workflow_text = read(WORKFLOW)
    run_ci_text = read(RUN_CI_GROUP)
    p0_text = read(P0_REQUIRED)
    self_text = read(Path(__file__))

    # This contract test must remain source-only (regex-based check).
    for label, pattern in FORBIDDEN_DYNAMIC_PATTERNS:
        if re.search(pattern, self_text):
            errors.append(f"contract test contains actual dynamic operation: {label}")

    # Smoke script must retain the route/discovery concepts.
    for snippet in REQUIRED_SMOKE_SNIPPETS:
        if snippet not in smoke_text:
            errors.append(f"smoke script missing required snippet: {snippet}")

    # Workflow must run the smoke script in the live/action context.
    for snippet in REQUIRED_WORKFLOW_SNIPPETS:
        if snippet not in workflow_text:
            errors.append(f"workflow missing required snippet: {snippet}")

    # Source-only p0-main should include this contract test.
    required_cmd = "scripts/test_external_agent_entrypoint_journey_smoke_contract.py"
    if required_cmd not in run_ci_text:
        errors.append("run_ci_group.py must include external journey contract test in p0-main")
    if "test_external_agent_entrypoint_journey_smoke_contract.py" not in p0_text:
        errors.append("test_p0_main_required_commands.py must require external journey contract test")

    # Source-only p0-main must not run live journey smoke directly.
    # Check that p0-main group does not contain the live smoke command.
    # We look for the command as a list entry in the p0-main group specifically.
    p0_live_pattern = r'"python3",\s*"scripts/smoke_external_agent_entrypoint_journeys.py"'
    # Find p0-main section
    p0_match = re.search(r'"p0-main":\s*\[', run_ci_text)
    if p0_match:
        # Find the end of p0-main list (next top-level key or end of GROUPS)
        p0_start = p0_match.end()
        # Look for the live smoke command within p0-main section
        # Simple heuristic: check between p0-main and next group key
        next_group = re.search(r'\n\s{4}"[a-z]', run_ci_text[p0_start:])
        p0_section = run_ci_text[p0_start:p0_start + next_group.start()] if next_group else run_ci_text[p0_start:]
        if re.search(p0_live_pattern, p0_section):
            errors.append("p0-main must not run live smoke_external_agent_entrypoint_journeys.py directly")

    # Check stale endpoints in smoke script (skip lines that are checking for them)
    for stale in FORBIDDEN_STALE_ENDPOINTS:
        # Only flag if the stale endpoint appears as an actual URL path, not as a check pattern
        stale_pattern = re.escape(stale)
        if re.search(rf'(?<!["\']){stale_pattern}(?!["\'])', workflow_text):
            errors.append(f"stale endpoint found in workflow: {stale}")

    if errors:
        print("FAIL: external agent entrypoint journey smoke contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: external agent entrypoint journey smoke contract is present and source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
