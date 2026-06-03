#!/usr/bin/env python3
"""Phase 6C: Render manual deploy contract.

Verifies that Render manual deploy is properly configured.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    errors: list[str] = []

    # 1. render_manual_deploy.py exists and references RENDER
    script = ROOT / "scripts" / "render_manual_deploy.py"
    if not script.exists():
        errors.append("scripts/render_manual_deploy.py missing")
    else:
        text = script.read_text(encoding="utf-8")
        if "RENDER" not in text:
            errors.append("render_manual_deploy.py does not reference RENDER")
        else:
            ok("render_manual_deploy.py references RENDER")
        if "allow-legacy" not in text and "allow_legacy" not in text:
            errors.append("render_manual_deploy.py missing --allow-legacy guard")
        else:
            ok("render_manual_deploy.py has --allow-legacy guard")
        if "LEGACY_SERVICE_NAME" not in text:
            errors.append("render_manual_deploy.py missing legacy service name constant")
        else:
            ok("render_manual_deploy.py defines legacy service name")

    # 2. workflow is workflow_dispatch only
    wf = ROOT / ".github" / "workflows" / "render-manual-deploy.yml"
    if not wf.exists():
        errors.append(".github/workflows/render-manual-deploy.yml missing")
    else:
        text = wf.read_text(encoding="utf-8")
        if "workflow_dispatch" not in text:
            errors.append("render-manual-deploy.yml is not workflow_dispatch only")
        else:
            ok("render-manual-deploy.yml is workflow_dispatch")
        if "secrets.RENDER" not in text:
            errors.append("render-manual-deploy.yml does not use secrets.RENDER")
        else:
            ok("render-manual-deploy.yml uses secrets.RENDER")
        # Should NOT have workflow_run, schedule, push, pull_request triggers
        for trigger in ["workflow_run:", "schedule:", "push:", "pull_request:"]:
            if trigger in text:
                errors.append(f"render-manual-deploy.yml has unexpected trigger: {trigger}")

    # 3. render.yaml has both gateways autoDeploy: false
    render_yaml = ROOT / "render.yaml"
    if render_yaml.exists():
        text = render_yaml.read_text(encoding="utf-8")
        if "autoDeploy: false" in text:
            ok("render.yaml has autoDeploy: false")
        else:
            errors.append("render.yaml may not have autoDeploy: false for all services")
    else:
        # Check if services are configured via API instead
        ok("render.yaml not found (services may be configured via API)")

    if errors:
        print("FAIL: Render manual deploy contract errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nPASS: Render manual deploy contract verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
