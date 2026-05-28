#!/usr/bin/env python3
"""Source-only contract for site-agent-entrypoint-journey-smoke workflow."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:
    print(f"FAIL: PyYAML is required for this test: {exc}")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "site-agent-entrypoint-journey-smoke.yml"


def main() -> int:
    if not WORKFLOW.exists():
        print("FAIL: .github/workflows/site-agent-entrypoint-journey-smoke.yml missing")
        return 1

    text = WORKFLOW.read_text(encoding="utf-8")
    errors: list[str] = []

    try:
        data = yaml.safe_load(text)
    except Exception as exc:
        print(f"FAIL: workflow YAML is not valid: {exc}")
        return 1

    if not isinstance(data, dict):
        errors.append("workflow YAML root must be a mapping")

    if not data.get("name"):
        errors.append("workflow must have a name")

    on = data.get("on", data.get(True, {}))
    if "workflow_dispatch" not in on:
        errors.append("workflow must have workflow_dispatch trigger")
    if "schedule" not in on:
        errors.append("workflow must have schedule trigger")

    jobs = data.get("jobs", {})
    if "smoke" not in jobs:
        errors.append("workflow must define jobs.smoke")

    smoke = jobs.get("smoke", {}) if isinstance(jobs, dict) else {}
    if smoke.get("runs-on") not in ("ubuntu-24.04", "ubuntu-latest"):
        errors.append("smoke job runs-on must be ubuntu-24.04 or ubuntu-latest")

    required_text = [
        "smoke_external_agent_entrypoint_journeys.py",
        "https://www.trinityaccord.org",
    ]
    for snippet in required_text:
        if snippet not in text:
            errors.append(f"workflow missing required text: {snippet}")

    if errors:
        print("FAIL: site-agent-entrypoint-journey-smoke workflow contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: site-agent-entrypoint-journey-smoke workflow contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
