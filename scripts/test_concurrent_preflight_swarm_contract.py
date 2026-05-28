#!/usr/bin/env python3
"""Concurrent preflight swarm must remain preflight-only and live-site scoped."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "smoke_external_agent_concurrent_preflight_swarm.py"
RUN_CI = ROOT / "scripts" / "run_ci_group.py"

def main() -> int:
    errors: list[str] = []
    text = SCRIPT.read_text(encoding="utf-8")
    run_ci = RUN_CI.read_text(encoding="utf-8")

    for required in [
        "/gateway/preflight",
        "preflight_only",
        "not_formal_submission",
        "not_archive",
        "not_verification",
        "not_guardian_status",
        "ThreadPoolExecutor",
    ]:
        if required not in text:
            errors.append(f"swarm script missing {required}")

    if "smoke_external_agent_concurrent_preflight_swarm.py" not in run_ci:
        errors.append("run_ci_group.py must include swarm in live-site group")

    p0_section = run_ci.split('"p0-main"', 1)[-1].split('"live-site"', 1)[0]
    if "smoke_external_agent_concurrent_preflight_swarm.py" in p0_section:
        errors.append("p0-main must not run live concurrent preflight swarm")

    if errors:
        print("FAIL: concurrent preflight swarm contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: concurrent preflight swarm contract is valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
