#!/usr/bin/env python3
"""Contract test: current incremental Arweave archive pipeline.

Asserts:
- current workflow and archive tooling exist
- automated upstream events are dry-run only
- automated live Record-Chain upload is limited to one daily schedule
- human dispatch may explicitly request live mode
- paid payloads route through the incremental builder
- existing crash-safe upload/readback behavior remains available
- repository/API boundary and backlog contracts remain intact
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TERMS = {"ARV5", "LV5", "IVV5", "IPFS"}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    errors: list[str] = []

    # 1. Workflow exists
    wf = ROOT / ".github" / "workflows" / "record-chain-arweave-archive.yml"
    if not wf.exists():
        errors.append("missing .github/workflows/record-chain-arweave-archive.yml")
    else:
        text = wf.read_text(encoding="utf-8")
        if "dry-run" not in text:
            errors.append("arweave-archive workflow missing dry-run default")
        if "ARKEY" not in text:
            errors.append("arweave-archive workflow missing ARKEY reference")
        if "ARWEAVE_WALLET_JWK_B64" in text:
            errors.append("arweave-archive workflow must not use ARWEAVE_WALLET_JWK_B64 (use ARKEY)")
        for forbidden in [
            "echo $ARKEY",
            "echo ${ARKEY}",
            'echo "$ARKEY"',
            "printf $ARKEY",
            "printf ${ARKEY}",
            'printf "$ARKEY"',
            "printenv",
            "env |",
            "set -x",
        ]:
            if forbidden in text:
                errors.append(f"arweave-archive workflow may expose wallet secret: {forbidden}")

        if "detect_record_chain_pipeline_backlog.py" not in text:
            errors.append("arweave-archive workflow missing backlog detector")
        if "arweave_archive_needed" not in text:
            errors.append("arweave-archive workflow missing arweave_archive_needed guard")
        if "ots_matches_chain" not in text:
            errors.append("arweave-archive workflow missing OTS wait guard")

        if "generate_public_home_status.py" in text or "patch_public_home_status_primary.py" in text:
            errors.append("arweave-archive workflow must not regenerate homepage status directly")
        if "api/public-home-status.json" in text or "index.md" in text or "sitemap.xml" in text:
            errors.append("arweave-archive workflow must not commit homepage generated artifacts directly")
        if "api/record-chain-status.json" in text:
            errors.append("arweave-archive workflow must not commit derived record-chain-status directly")

        if "workflow_run" not in text:
            errors.append("arweave-archive workflow missing workflow_run trigger")
        if "Record Chain Head OTS Anchor" not in text:
            errors.append("arweave-archive workflow must listen to OTS anchor workflow")
        if "Automated upstream event is dry-run only" not in text:
            errors.append("automated upstream archive events must be explicitly forced to dry-run")
        if 'cron: "17 7 * * *"' not in text:
            errors.append("arweave-archive workflow must have one daily automated live schedule")
        if "*/30 * * * *" in text:
            errors.append("arweave-archive workflow must not retain the 30-minute paid schedule scanner")
        if 'if [ "$EVENT_NAME" = "schedule" ]; then' not in text or 'mode="live"' not in text:
            errors.append("daily schedule must explicitly resolve to live mode")
        if 'if [ "$EVENT_ACTOR" = "github-actions[bot]" ]; then' not in text:
            errors.append("bot workflow dispatch must be prevented from authorizing paid mode")
        if "run_record_chain_arweave_incremental.py" not in text:
            errors.append("paid archive workflow must route through incremental payload builder")
        if "run_record_chain_arweave_archive.py --mode" in text:
            errors.append("workflow directly invokes full-history runner instead of incremental wrapper")

        if "git fetch origin main --prune" not in text or "git rebase origin/main" not in text:
            errors.append("arweave-archive workflow must fetch origin main and rebase origin/main before push retry")
        first_rebase = text.find("git rebase origin/main")
        push_loop = text.find("for attempt in 1 2 3")
        if first_rebase == -1 or push_loop == -1 or first_rebase > push_loop:
            errors.append("arweave-archive workflow must rebase before entering push retry loop")

    # 2. Scripts exist
    build_script = ROOT / "scripts" / "build_record_chain_arweave_archive.py"
    verify_script = ROOT / "scripts" / "verify_record_chain_arweave_archive.py"
    crash_safe_runner = ROOT / "scripts" / "run_record_chain_arweave_archive.py"
    incremental_builder = ROOT / "scripts" / "record_chain_arweave_incremental.py"
    incremental_runner = ROOT / "scripts" / "run_record_chain_arweave_incremental.py"
    for script in [build_script, verify_script, crash_safe_runner, incremental_builder, incremental_runner]:
        if not script.exists():
            errors.append(f"missing {script.relative_to(ROOT)}")

    if incremental_runner.exists():
        runner_text = incremental_runner.read_text(encoding="utf-8")
        for marker in [
            "import run_record_chain_arweave_archive as runner",
            "build_incremental_payload_json",
            "runner.builder.build_payload_json = build_incremental_payload_json",
            "runner.main()",
        ]:
            if marker not in runner_text:
                errors.append(f"incremental runner missing crash-safe delegation marker: {marker}")

    if incremental_builder.exists():
        delta_text = incremental_builder.read_text(encoding="utf-8")
        for marker in [
            "full_snapshot",
            "incremental_delta",
            "previous_archive_txid",
            "delta_record_count",
            "content_base64",
        ]:
            if marker not in delta_text:
                errors.append(f"incremental builder missing marker: {marker}")

    # 3. API index exists
    api = ROOT / "api" / "record-chain-arweave-index.json"
    if not api.exists():
        errors.append("missing api/record-chain-arweave-index.json")
    else:
        data = json.loads(api.read_text(encoding="utf-8"))
        if data.get("schema") != "trinityaccord.record-chain-arweave-index.v1":
            errors.append("arweave-index.json wrong schema")
        if "live_upload_implemented" not in data:
            errors.append("arweave-index.json missing live_upload_implemented field")
        boundary = data.get("boundary", {})
        for key in [
            "arweave_archive_is_mirror_only",
            "arweave_archive_is_not_authority",
            "arweave_archive_is_not_amendment",
            "bitcoin_originals_prevail",
        ]:
            if not boundary.get(key):
                errors.append(f"arweave-index.json boundary missing: {key}")
        api_text = api.read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if term in api_text:
                errors.append(f"forbidden term '{term}' in arweave-index.json")

    # 4. Arweave archives directory
    archives_dir = ROOT / "record-chain" / "arweave-archives"
    if not archives_dir.exists():
        gitkeep = archives_dir / ".gitkeep"
        if not gitkeep.exists():
            errors.append("record-chain/arweave-archives/.gitkeep missing")

    # 5. Complete manifest builder remains deterministic and idempotent.
    if build_script.exists():
        text = build_script.read_text(encoding="utf-8")
        if "No new Arweave archive needed" not in text:
            errors.append("build script missing idempotency check message")
        if "archive_manifest_sha256" not in text:
            errors.append("build script missing archive_manifest_sha256 computation")
        if "not_authority" not in text:
            errors.append("build script missing boundary fields")

    # 6. Verify script retains boundary and terminology checks.
    if verify_script.exists():
        text = verify_script.read_text(encoding="utf-8")
        if "FORBIDDEN_TERMS" not in text and "ARV5" not in text:
            errors.append("verify script missing forbidden terminology check")
        if "not_authority" not in text:
            errors.append("verify script missing boundary check")

    # 7. Backlog detector exists
    detector = ROOT / "scripts" / "detect_record_chain_pipeline_backlog.py"
    if not detector.exists():
        errors.append("missing scripts/detect_record_chain_pipeline_backlog.py")

    # 8. Homepage sync workflow must exist and listen to Arweave
    home_sync = ROOT / ".github" / "workflows" / "homepage-status-sync.yml"
    if not home_sync.exists():
        errors.append("missing centralized homepage-status-sync.yml")
    else:
        home_text = home_sync.read_text(encoding="utf-8")
        if "Record Chain Arweave Archive" not in home_text:
            errors.append("homepage-status-sync.yml must listen to Record Chain Arweave Archive")
        if "scripts/update_public_generated_artifacts.py" not in home_text:
            errors.append("homepage-status-sync.yml must run centralized generated artifact updater")

    if errors:
        print("Arweave archive contract tests FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("Arweave archive contract tests PASSED.")


if __name__ == "__main__":
    main()
