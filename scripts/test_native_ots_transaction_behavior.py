#!/usr/bin/env python3
"""Behavioral regression for the Native OTS write transaction."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RECONCILER = SCRIPTS / "reconcile_native_ots_generated_state.py"
WORKFLOW = ROOT / ".github/workflows/native-ots-upgrade-watch.yml"
RUNNER = SCRIPTS / "run_native_ots_upgrade_verify.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_reconciler():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("native_ots_reconciler_under_test", RECONCILER)
    require(spec is not None and spec.loader is not None, "could not load reconciler")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reconciler_is_derived_only() -> None:
    module = load_reconciler()
    calls: list[object] = []

    module.validate_native_latest_ots = lambda: {
        "latest_anchor_file": "record-chain/ots/native-anchors/current.anchor.json",
        "ots_status": "pending",
    }

    def sync(anchor_rel: str):
        calls.append(("sync", anchor_rel))
        return {"ots_status": "upgraded", "bitcoin_verified": False}

    parity_calls = 0

    def parity():
        nonlocal parity_calls
        parity_calls += 1
        calls.append(("parity", parity_calls))
        return {"entries": [{"tx_id": "historical"}]}

    def fake_run(command, **kwargs):
        calls.append(("run", tuple(command), kwargs))
        class Result:
            returncode = 0
        return Result()

    module.sync_native_latest_from_anchor = sync
    module.require_registry_parity = parity
    result = module.reconcile(run=fake_run)

    require(result.get("paid_upload_performed") is False, "reconciler must never report paid upload")
    require(result.get("ots_upgrade_performed") is False, "reconciler must never report OTS upgrade")
    require(result.get("derived_state_reconciled") is True, "reconciler must declare derived-state reconciliation")
    require(calls[0] == ("sync", "record-chain/ots/native-anchors/current.anchor.json"), "reconciler synced the wrong anchor")
    commands = [entry[1] for entry in calls if isinstance(entry, tuple) and entry and entry[0] == "run"]
    require(
        commands == [
            (sys.executable, "scripts/detect_archive_backlog.py", "--write"),
            (sys.executable, "scripts/generate_arweave_wallet_status.py"),
        ],
        f"reconciler executed unexpected commands: {commands}",
    )
    require(parity_calls == 2, "registry parity must be checked before and after generators")


def test_workflow_transaction_boundary() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    required = [
        "group: main-write-lock",
        "queue: max",
        "fetch-depth: 0",
        "ref: main",
        'actor="${GITHUB_ACTOR:-}"',
        "reconcile_and_stage",
        "scripts/reconcile_native_ots_generated_state.py",
        "record-chain/ots/native-ots-backlog.json",
        "api/record-chain-native-ots-backlog.json",
        "git rebase origin/main",
        "git commit --amend --no-edit",
        "git push origin HEAD:main",
        "done < <(git diff --cached --name-only)",
        "git diff --cached --check",
        "--untracked-files=no",
        "never upgrade or upload again here",
    ]
    for marker in required:
        require(marker in text, f"workflow missing transaction marker: {marker}")

    forbidden = [
        "group: native-ots-upgrade-watch",
        "git stash",
        "if git push; then",
        "${GITHUB_REF_NAME",
    ]
    for marker in forbidden:
        require(marker not in text, f"workflow retains unsafe marker: {marker}")

    rebase = text.index("git rebase origin/main")
    reconcile_after = text.index("reconcile_and_stage", rebase)
    push = text.index("git push origin HEAD:main", reconcile_after)
    require(rebase < reconcile_after < push, "workflow must reconcile after rebase and before push")


def test_backlog_refresh_fails_closed() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    start = text.index("def refresh_native_ots_backlog")
    end = text.index("\n\ndef ", start + 1)
    block = text[start:end]
    require("check=True" in block, "native OTS backlog refresh still ignores detector failure")
    require("check=False" not in block, "native OTS backlog refresh still contains check=False")


def main() -> int:
    test_reconciler_is_derived_only()
    test_workflow_transaction_boundary()
    test_backlog_refresh_fails_closed()
    print("PASS: Native OTS writes are serialized, main-bound, reconciled after rebase, and fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
