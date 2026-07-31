#!/usr/bin/env python3
"""One-time reviewed patch for PR #825; removed by its applying workflow."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]

# Move the current archive contract from a daily paid cadence to one weekly
# paid continuity bundle containing heartbeat + OTS evidence.
path = root / "scripts/test_record_chain_data_arweave_archive_contract.py"
text = path.read_text(encoding="utf-8")
text = text.replace('cron: "17 7 * * *"', 'cron: "17 7 * * 3"')
text = text.replace(
    '"previous archive is missing a verified Arweave transaction id",\n',
    '"previous archive is missing a verified Arweave transaction id",\n'
    '        "trinityaccord.weekly-continuity-bundle.v1",\n'
    '        "trinityaccord.weekly-heartbeat-summary.v1",\n'
    '        "trinityaccord.weekly-native-ots-evidence.v1",\n',
)
text = text.replace(
    "current incremental native Arweave route remains authoritative",
    "current weekly incremental native Arweave continuity route remains authoritative",
)
path.write_text(text, encoding="utf-8")

# The active daily Native OTS route is now strictly no-cost. Paid proof
# publication belongs only to the weekly Record-Chain continuity bundle.
(root / "scripts/test_native_ots_upgrade_workflow_contract.py").write_text(
    '''#!/usr/bin/env python3
"""Contract: daily Native OTS lifecycle is no-cost and weekly archival owns publication."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label} marker: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"forbidden {label} marker found: {needle}")


def main() -> None:
    workflow = (ROOT / ".github/workflows/native-ots-upgrade-watch.yml").read_text(encoding="utf-8")
    orchestrator = (ROOT / "scripts/run_native_ots_workflow_once.py").read_text(encoding="utf-8")
    runner = (ROOT / "scripts/run_native_ots_upgrade_verify.py").read_text(encoding="utf-8")
    reconciler = (ROOT / "scripts/reconcile_native_ots_generated_state.py").read_text(encoding="utf-8")
    archive_workflow = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text(encoding="utf-8")
    weekly_builder = (ROOT / "scripts/record_chain_arweave_incremental.py").read_text(encoding="utf-8")

    for marker in [
        "workflow_dispatch:",
        'cron: "42 6 * * *"',
        "contents: write",
        "group: main-write-lock",
        "queue: max",
        "timeout-minutes: 45",
        "fetch-depth: 0",
        "ref: main",
        "verify_only",
        "upgrade_only",
        "Run Native OTS workflow contract tests",
        "scripts/test_native_ots_upgrade_workflow_contract.py",
        "scripts/test_native_ots_complete_staging_contract.py",
        "run_native_ots_workflow_once.py",
        "record-chain/audit/native-ots/",
    ]:
        require(workflow, marker, "daily no-cost workflow")

    for marker in [
        "ARKEY",
        "ARWEAVE_JWK",
        "arweave_runtime_spend_guard.mjs",
        "ARWEAVE_MINIMUM_REMAINING_AR",
        "--enable-paid-upload",
        "--confirm-paid-upload",
        "actions/setup-node",
    ]:
        forbid(workflow, marker, "daily workflow paid capability")

    for marker in [
        '{"verify_only", "upgrade_only"}',
        "scripts/run_native_ots_upgrade_verify.py",
        'command.append("--verify-only")',
        "scripts/reconcile_native_ots_generated_state.py",
        "scripts/restore_json_if_only_volatile_changes.py",
        "api/record-chain-native-ots-latest.json",
        "record-chain/ots/native-anchors/",
        'run("git", "fetch", "origin", "main", "--prune")',
        'run("git", "rebase", "origin/main"',
        'run("git", "push", "origin", "HEAD:main"',
    ]:
        require(orchestrator, marker, "no-cost orchestrator")
    for marker in [
        "evaluate_daily_spend",
        "--enable-paid-upload",
        "--confirm-paid-upload",
        "ARWEAVE_JWK_PATH",
        "I_UNDERSTAND_THIS_UPLOADS",
    ]:
        forbid(orchestrator, marker, "no-cost orchestrator paid capability")

    retry = orchestrator.split("def push_metadata_only", 1)[-1].split("def main", 1)[0]
    forbid(retry, "run_native_ots_upgrade_verify.py", "metadata retry lifecycle repeat")
    require(retry, "reconcile_and_stage()", "metadata retry reconciliation")

    for marker in [
        "trinityaccord.native-record-chain-ots-latest.v1",
        "trinityaccord.native-record-chain-ots-anchor.v1",
        "ots_upgrade_and_verify",
        "bitcoin_attestation_embedded",
        "strict_bitcoin_verified",
    ]:
        require(runner, marker, "local OTS lifecycle")

    for marker in [
        "never upgrades an OTS proof and never uploads to Arweave",
        "sync_native_latest_from_anchor",
        "validate_native_registry",
        "scripts/detect_archive_backlog.py",
        '"paid_upload_performed": False',
    ]:
        require(reconciler, marker, "derived-state reconciler")

    require(archive_workflow, 'cron: "17 7 * * 3"', "weekly paid archive schedule")
    require(archive_workflow, "ARKEY", "weekly archive wallet boundary")
    require(archive_workflow, "Automated upstream event is dry-run only", "upstream dry-run boundary")
    for marker in [
        "trinityaccord.weekly-continuity-bundle.v1",
        "trinityaccord.weekly-native-ots-evidence.v1",
        'latest.get("latest_ots_file")',
        "proof_files_embedded_in_this_payload",
    ]:
        require(weekly_builder, marker, "weekly embedded OTS evidence")

    print("PASS: daily Native OTS is no-cost; weekly continuity archive owns paid publication")


if __name__ == "__main__":
    main()
''',
    encoding="utf-8",
)

# Align the cost-boundary regression with the no-cost daily OTS route.
path = root / "tests/test_arweave_cost_boundaries.py"
text = path.read_text(encoding="utf-8")
old = '''def test_native_ots_workflow_uses_single_spend_orchestrator() -> None:
    workflow = (ROOT / ".github/workflows/native-ots-upgrade-watch.yml").read_text()
    orchestrator = (ROOT / "scripts/run_native_ots_workflow_once.py").read_text()
    assert "run_native_ots_workflow_once.py" in workflow
    assert "arweave_runtime_spend_guard.mjs" in workflow
    retry = orchestrator.split("def push_metadata_only", 1)[1].split("def main", 1)[0]
    assert "run_native_ots_upgrade_verify.py" not in retry
'''
new = '''def test_native_ots_daily_workflow_has_no_paid_path() -> None:
    workflow = (ROOT / ".github/workflows/native-ots-upgrade-watch.yml").read_text()
    orchestrator = (ROOT / "scripts/run_native_ots_workflow_once.py").read_text()
    weekly_builder = (ROOT / "scripts/record_chain_arweave_incremental.py").read_text()
    assert "run_native_ots_workflow_once.py" in workflow
    assert "upgrade_only" in workflow
    for forbidden in ["ARKEY", "ARWEAVE_JWK", "arweave_runtime_spend_guard.mjs", "--enable-paid-upload"]:
        assert forbidden not in workflow
    for forbidden in ["evaluate_daily_spend", "--enable-paid-upload", "ARWEAVE_JWK_PATH"]:
        assert forbidden not in orchestrator
    retry = orchestrator.split("def push_metadata_only", 1)[1].split("def main", 1)[0]
    assert "run_native_ots_upgrade_verify.py" not in retry
    assert "trinityaccord.weekly-native-ots-evidence.v1" in weekly_builder
'''
if old not in text:
    raise SystemExit("native OTS cost-boundary test block changed unexpectedly")
path.write_text(text.replace(old, new), encoding="utf-8")

# Daily liveness must no longer say that an individual paid capsule is pending.
# Historical capsules remain readable evidence only.
path = root / "scripts/generate_waiting_heartbeat_status.py"
text = path.read_text(encoding="utf-8")
old = '''    elif final_record_exists and ots_covers_latest:
        daily_alive_status = "success"
        if arweave_verified:
            latest_result = "success"
        elif arweave_deferred:
            latest_result = "operational_alive_arweave_capsule_deferred"
        else:
            latest_result = "operational_alive_arweave_capsule_pending"
        failure_stage = None
'''
new = '''    elif final_record_exists and ots_covers_latest:
        daily_alive_status = "success"
        latest_result = "success"
        failure_stage = None
'''
if old not in text:
    raise SystemExit("waiting heartbeat result block changed unexpectedly")
text = text.replace(old, new)
old = '''        "archive_followup": {
            "arweave_capsule_upload_expected": True,
            "arweave_readback_hash_match_expected": True,
            "does_not_gate_daily_alive_success": True,
        },
'''
new = '''        "archive_followup": {
            "standalone_arweave_capsule_retired": True,
            "arweave_capsule_upload_expected": False,
            "arweave_readback_hash_match_expected": False,
            "weekly_continuity_archive_expected": True,
            "weekly_continuity_archive_does_not_gate_daily_alive_success": True,
            "historical_capsules_remain_verifiable": True,
        },
'''
if old not in text:
    raise SystemExit("waiting heartbeat archive_followup block changed unexpectedly")
text = text.replace(old, new)
text = text.replace(
    '"arweave_capsule_pending_archive_followup": bool(final_record_exists and ots_covers_latest and not arweave_verified and not arweave_deferred),',
    '"arweave_capsule_pending_archive_followup": False,\n'
    '            "standalone_arweave_capsule_retired": True,\n'
    '            "weekly_continuity_archive_is_followup": True,',
)
text = text.replace(
    '"latest_arweave_capsule": latest_capsule,',
    '"latest_arweave_capsule": latest_capsule,\n'
    '        "standalone_capsule_policy": {\n'
    '            "status": "retired",\n'
    '            "historical_results_remain_verifiable": True,\n'
    '            "new_heartbeats_are_mirrored_by_weekly_continuity_archive": True,\n'
    '        },',
)
path.write_text(text, encoding="utf-8")

# A successful upstream dry-run is not evidence that a new weekly archive
# exists. Only the scheduled paid window or a human dispatch may attempt DOI.
path = root / ".github/workflows/weekly-continuity-zenodo.yml"
text = path.read_text(encoding="utf-8")
text = text.replace(
    "if: ${{ github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success' }}",
    "if: ${{ github.event_name == 'workflow_dispatch' || (github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.event == 'schedule') }}",
)
text = text.replace(
    "      - name: Commit preservation package before external publication\n",
    "      - name: Commit preservation package before external publication\n        if: steps.build.outputs.deposit_available == 'true'\n",
)
text = text.replace(
    "      - name: Resolve Zenodo publication availability\n",
    "      - name: Resolve Zenodo publication availability\n        if: steps.build.outputs.deposit_available == 'true'\n",
)
text = text.replace(
    "        if: steps.zenodo.outputs.configured == 'true'\n",
    "        if: steps.build.outputs.deposit_available == 'true' && steps.zenodo.outputs.configured == 'true'\n",
)
text = text.replace(
    "        if: always()\n        uses: actions/upload-artifact",
    "        if: always() && steps.build.outputs.deposit_available == 'true'\n        uses: actions/upload-artifact",
)
path.write_text(text, encoding="utf-8")

# Before the first weekly archive, or when a scheduled archive run has nothing
# new to upload, the DOI mirror must skip cleanly.
path = root / "scripts/build_weekly_continuity_deposit.py"
text = path.read_text(encoding="utf-8")
old = '''    continuity = payload.get("continuity_bundle")
    if not isinstance(continuity, dict) or continuity.get("schema") != "trinityaccord.weekly-continuity-bundle.v1":
        raise SystemExit("latest verified archive is not a weekly continuity bundle")
'''
new = '''    continuity = payload.get("continuity_bundle")
    if not isinstance(continuity, dict) or continuity.get("schema") != "trinityaccord.weekly-continuity-bundle.v1":
        github_output("deposit_available", "false")
        github_output("archive_id", "")
        github_output("deposit_dir", "")
        github_output("deposit_changed", "false")
        print("No verified weekly continuity archive is available; DOI deposit is deferred.")
        return None
'''
if old not in text:
    raise SystemExit("weekly deposit continuity gate changed unexpectedly")
text = text.replace(old, new)
text = text.replace("def build() -> Path:", "def build() -> Path | None:")
text = text.replace(
    '    github_output("archive_id", archive_id)\n',
    '    github_output("deposit_available", "true")\n    github_output("archive_id", archive_id)\n',
)
old = '''    target = build()
    if args.check:
        status = os.system(f"git diff --exit-code -- {target.relative_to(ROOT)} >/dev/null")
        if status != 0:
            raise SystemExit("weekly continuity deposit is not reproducible")
'''
new = '''    target = build()
    if target is None:
        return 0
    if args.check:
        import subprocess

        result = subprocess.run(
            ["git", "diff", "--exit-code", "--", str(target.relative_to(ROOT))],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit("weekly continuity deposit is not reproducible")
'''
if old not in text:
    raise SystemExit("weekly deposit main block changed unexpectedly")
path.write_text(text.replace(old, new), encoding="utf-8")

# Preserve the metadata JSON alongside the deposited bytes as well as applying
# it to the Zenodo record.
path = root / "scripts/publish_weekly_continuity_to_zenodo.py"
text = path.read_text(encoding="utf-8")
text = text.replace(
    '        "deposit-manifest.json",\n        "checksums.sha256",',
    '        "deposit-manifest.json",\n        "zenodo-metadata.json",\n        "checksums.sha256",',
)
path.write_text(text, encoding="utf-8")
