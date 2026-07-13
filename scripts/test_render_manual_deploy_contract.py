#!/usr/bin/env python3
"""Phase 6C: Render manual deploy and Round 8 production-surface contracts.

Verifies that Render manual deploy is properly configured and cannot report a
suspended or unconfirmed deployment as triggered. Also registers public writer
and NFT backup capability boundaries because those workflows can publish
production-facing artifacts or Release assets.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def run_contract(path: Path, label: str, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"{label} is missing")
        return
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append(f"{label} failed: " + (result.stderr or result.stdout)[-8000:])
    else:
        ok(f"{label} passes")


def main() -> int:
    errors: list[str] = []

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
        if "service_is_suspended" not in text or "no deployment was created" not in text:
            errors.append("render_manual_deploy.py does not fail closed for suspended services")
        else:
            ok("render_manual_deploy.py fails closed for suspended services")
        if "deploy_id_from_response" not in text or "deployment is unconfirmed" not in text:
            errors.append("render_manual_deploy.py does not require a confirmed deploy ID")
        else:
            ok("render_manual_deploy.py requires a confirmed deploy ID")

    run_contract(
        ROOT / "scripts/test_render_manual_deploy_behavior.py",
        "Render deployment behavior regression",
        errors,
    )

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
        for trigger in ["workflow_run:", "schedule:", "push:", "pull_request:"]:
            if trigger in text:
                errors.append(f"render-manual-deploy.yml has unexpected trigger: {trigger}")
        for marker in [
            "github.ref == 'refs/heads/main'",
            "Authorize production deployment actor and ref",
            "ref: main",
            "contents: read",
        ]:
            if marker not in text:
                errors.append(f"render-manual-deploy.yml missing main-only secret boundary: {marker}")

    render_yaml = ROOT / "render.yaml"
    if render_yaml.exists():
        text = render_yaml.read_text(encoding="utf-8")
        if "autoDeploy: false" in text:
            ok("render.yaml has autoDeploy: false")
        else:
            errors.append("render.yaml may not have autoDeploy: false for all services")
    else:
        ok("render.yaml not found (services may be configured via API)")

    run_contract(
        ROOT / "scripts/test_round8_public_writer_transaction_contract.py",
        "Round 8 public writer transaction contract",
        errors,
    )
    run_contract(
        ROOT / "scripts/test_round8_nft_backup_contract.py",
        "Round 8 NFT backup capability contract",
        errors,
    )

    if errors:
        print("FAIL: Render/manual-public-surface contract errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nPASS: Render manual deploy and Round 8 production-surface contracts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
