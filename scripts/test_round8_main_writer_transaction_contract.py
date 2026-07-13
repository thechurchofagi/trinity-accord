#!/usr/bin/env python3
"""Round 8 contract for active Record-Chain/OTS/wallet main writers."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = [
    ".github/workflows/arweave-wallet-status-update.yml",
    ".github/workflows/record-chain-append.yml",
    ".github/workflows/record-chain-build-batch.yml",
    ".github/workflows/record-chain-anchor.yml",
    ".github/workflows/record-chain-head-ots-anchor.yml",
    ".github/workflows/record-chain-auto-finalize.yml",
    ".github/workflows/record-chain-ots-stamp.yml",
    ".github/workflows/record-chain-ots-upgrade.yml",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def text(path: str) -> str:
    target = ROOT / path
    require(target.exists(), f"missing {path}")
    return target.read_text(encoding="utf-8")


def assert_workflow_syntax_and_transaction(path: str) -> str:
    content = text(path)
    try:
        parsed = yaml.safe_load(content)
    except Exception as exc:
        fail(f"invalid workflow YAML {path}: {exc}")
    require(isinstance(parsed, dict), f"workflow is not a mapping: {path}")

    for marker in [
        "contents: write",
        "group: main-write-lock",
        "queue: max",
        "cancel-in-progress: false",
        "ref: main",
        "git push origin HEAD:main",
        "set -euo pipefail",
        "Record toolchain provenance",
    ]:
        require(marker in content, f"{path} missing transaction marker: {marker}")

    for forbidden in [
        "${GITHUB_REF_NAME",
        "git push --force",
        "git push --force-with-lease",
        "git rebase origin main",
    ]:
        require(forbidden not in content, f"{path} retains unsafe marker: {forbidden}")

    for line in content.splitlines():
        stripped = line.strip()
        require(stripped != "git push", f"{path} retains bare git push")
        require(stripped != "git pull --rebase -X theirs origin main", f"{path} uses conflict-biased generated merge")

    return content


def assert_tip_helper_behavior() -> None:
    helper_path = ROOT / "scripts/check_native_ots_latest_matches_chain_tip.py"
    require(helper_path.exists(), "native OTS current-tip helper missing")

    result = subprocess.run(
        [sys.executable, str(helper_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(result.returncode == 0, "current native OTS projection does not bind current chain tip")

    spec = importlib.util.spec_from_file_location("round8_tip_helper", helper_path)
    require(spec is not None and spec.loader is not None, "could not import native OTS tip helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with tempfile.TemporaryDirectory(prefix="trinity-round8-tip-") as tmp:
        root = Path(tmp)
        (root / "record-chain").mkdir()
        (root / "api").mkdir()
        (root / "evidence").mkdir()

        tip = {
            "latest_record_id": "R-000000123",
            "latest_record_sha256": "a" * 64,
            "native_record_count": 123,
        }
        latest = {
            "schema": "trinityaccord.native-record-chain-ots-latest.v1",
            "chain_id": "trinity-accord-public-reception-ledger",
            "latest_record_id": tip["latest_record_id"],
            "latest_record_sha256": tip["latest_record_sha256"],
            "native_record_count": tip["native_record_count"],
            "legacy_main_chain_jsonl_is_not_source": True,
            "latest_anchored_file": "evidence/commitment.json",
            "latest_anchor_file": "evidence/anchor.json",
            "latest_ots_file": "evidence/anchor.json.ots",
        }
        (root / "record-chain/chain-tip.json").write_text(json.dumps(tip), encoding="utf-8")
        (root / "api/record-chain-native-ots-latest.json").write_text(json.dumps(latest), encoding="utf-8")
        (root / "evidence/commitment.json").write_text('{"source":"native"}', encoding="utf-8")
        (root / "evidence/anchor.json").write_text("{}", encoding="utf-8")
        (root / "evidence/anchor.json.ots").write_bytes(b"proof")

        old_root, old_tip, old_latest = module.ROOT, module.TIP, module.LATEST
        try:
            module.ROOT = root
            module.TIP = root / "record-chain/chain-tip.json"
            module.LATEST = root / "api/record-chain-native-ots-latest.json"
            module.check()

            latest["latest_record_sha256"] = "b" * 64
            module.LATEST.write_text(json.dumps(latest), encoding="utf-8")
            try:
                module.check()
            except SystemExit as exc:
                require("no longer binds" in str(exc), "stale native OTS projection failed for the wrong reason")
            else:
                fail("stale native OTS projection was accepted")
        finally:
            module.ROOT, module.TIP, module.LATEST = old_root, old_tip, old_latest


def main() -> int:
    contents = {path: assert_workflow_syntax_and_transaction(path) for path in WORKFLOWS}

    for path in [
        ".github/workflows/record-chain-anchor.yml",
        ".github/workflows/record-chain-head-ots-anchor.yml",
    ]:
        require("head_branch == 'main'" in contents[path], f"{path} accepts workflow_run from non-main")
        require("Authorize manual write actor" in contents[path], f"{path} lacks manual actor gate")

    for path in [
        ".github/workflows/record-chain-ots-stamp.yml",
        ".github/workflows/record-chain-ots-upgrade.yml",
    ]:
        content = contents[path]
        require("requirements-ots.txt" in content, f"{path} uses unpinned OTS installation")
        require("git add record-chain/" in content, f"{path} does not stage new proof files")
        require(
            content.find("git add record-chain/") < content.find("git diff --cached --quiet"),
            f"{path} checks for changes before staging untracked proofs",
        )

    head = contents[".github/workflows/record-chain-head-ots-anchor.yml"]
    require(
        head.count("check_native_ots_latest_matches_chain_tip.py") >= 2,
        "native head OTS workflow does not revalidate after rebase",
    )
    require("Dispatching Record Chain Arweave Archive in live mode" in head, "native OTS archive dispatch missing")

    auto = contents[".github/workflows/record-chain-auto-finalize.yml"]
    require("without rerunning finalization" in auto, "auto-finalize retry may repeat a finalization side effect")
    require("verify_record_chain_integrity.py" in auto, "auto-finalize lacks post-rebase integrity verification")

    wallet = contents[".github/workflows/arweave-wallet-status-update.yml"]
    require("generate_arweave_wallet_status.py --check" in wallet, "wallet status update lacks generated-state verification")
    require('case "${{ github.actor }}"' not in wallet, "wallet actor gate uses the github-actions[bot] case-pattern trap")

    build_batch = contents[".github/workflows/record-chain-build-batch.yml"]
    require(
        build_batch.find("git rebase origin/main") < build_batch.find("rebuild_batch_outputs", build_batch.find("for attempt")),
        "batch workflow does not rebuild after its push-time rebase",
    )

    assert_tip_helper_behavior()
    print("PASS: Round 8 main-writer transactions are main-bound, serialized, and revalidated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
