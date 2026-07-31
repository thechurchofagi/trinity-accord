#!/usr/bin/env python3
"""Behavioral regression for archive backlog dry-run/live routing."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PROCESSOR = SCRIPTS / "process_archive_backlog.py"
BACKLOGS = [
    ROOT / "record-chain/arweave-backlog.json",
    ROOT / "api/record-chain-arweave-backlog.json",
    ROOT / "record-chain/ots/native-ots-backlog.json",
    ROOT / "api/record-chain-native-ots-backlog.json",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module():
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("process_archive_backlog_under_test", PROCESSOR)
    require(spec is not None and spec.loader is not None, "could not load processor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoke_main(module, argv: list[str]) -> tuple[int, str]:
    old_argv = sys.argv
    stream = io.StringIO()
    try:
        sys.argv = [str(PROCESSOR), *argv]
        with contextlib.redirect_stdout(stream):
            result = module.main()
    finally:
        sys.argv = old_argv
    return int(result), stream.getvalue()


def test_synthetic_dry_run_never_routes_to_mutators() -> None:
    module = load_module()
    module.build_docs = lambda: (
        {
            "items": [
                {
                    "key": "rc-key",
                    "archive_status": "pending_upload",
                    "next_action": "upload_record_chain_archive",
                }
            ]
        },
        {
            "items": [
                {
                    "key": "ots-upgrade",
                    "archive_status": "upgrade_due",
                    "next_action": "upgrade_native_ots_anchor",
                },
                {
                    "key": "ots-upload",
                    "archive_status": "pending_upload",
                    "next_action": "upload_native_ots_bundle",
                },
            ]
        },
    )

    def forbidden(*_args, **_kwargs):
        raise AssertionError("dry-run reached a mutating function")

    module.run_detector_write = forbidden
    module.process_record_chain = forbidden
    module.process_native_ots = forbidden
    module.update_item = forbidden

    code, output = invoke_main(
        module,
        ["--kind", "record_chain_arweave", "--max-items", "1", "--mode", "dry-run"],
    )
    require(code == 0, "record-chain dry-run failed")
    data = json.loads(output)
    require(data.get("dry_run") is True, "record-chain preview lacks dry_run=true")
    require(data.get("repository_mutation") is False, "record-chain preview claims mutation")
    require(data.get("subprocess_execution") is False, "record-chain preview claims subprocess")
    require(data["candidates"][0]["would_increment_retry_count"] is False, "dry-run would increment retry count")

    code, output = invoke_main(
        module,
        [
            "--kind",
            "native_ots_bundle",
            "--max-items",
            "2",
            "--mode",
            "dry-run",
            "--enable-paid-upload",
        ],
    )
    require(code == 0, "native OTS dry-run failed")
    data = json.loads(output)
    require(data.get("candidate_count") == 2, "native OTS preview omitted candidates")
    require(
        [item["would_attempt"] for item in data["candidates"]]
        == ["upgrade_native_ots_anchor", "upload_native_ots_bundle"],
        "native OTS preview planned wrong actions",
    )


def test_real_cli_dry_run_preserves_backlog_bytes() -> None:
    before = {path: sha(path) for path in BACKLOGS}
    commands = [
        [
            sys.executable,
            str(PROCESSOR),
            "--kind",
            "record_chain_arweave",
            "--max-items",
            "2",
            "--mode",
            "dry-run",
        ],
        [
            sys.executable,
            str(PROCESSOR),
            "--kind",
            "native_ots_bundle",
            "--max-items",
            "2",
            "--mode",
            "dry-run",
            "--enable-paid-upload",
        ],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, f"real dry-run failed: {result.stderr}\n{result.stdout}")
        data = json.loads(result.stdout)
        require(data.get("repository_mutation") is False, "real dry-run did not declare read-only")
    after = {path: sha(path) for path in BACKLOGS}
    require(before == after, "real dry-run changed backlog bytes")


def test_live_mode_is_explicit_and_routed() -> None:
    """Manual processor live mode remains explicit for operator-only repair."""
    module = load_module()
    calls: list[object] = []
    module.run_detector_write = lambda: calls.append("detector")
    module.process_record_chain = lambda max_items: calls.append(("record", max_items)) or 17
    module.process_native_ots = (
        lambda max_items, paid: calls.append(("native", max_items, paid)) or 23
    )

    code, _output = invoke_main(
        module,
        ["--kind", "record_chain_arweave", "--max-items", "3", "--mode", "live"],
    )
    require(code == 17, "record-chain live route did not return processor result")
    require(calls == ["detector", ("record", 3)], f"wrong record-chain live routing: {calls}")

    calls.clear()
    code, _output = invoke_main(
        module,
        [
            "--kind",
            "native_ots_bundle",
            "--max-items",
            "2",
            "--mode",
            "live",
            "--enable-paid-upload",
        ],
    )
    require(code == 23, "native live route did not return processor result")
    require(calls == ["detector", ("native", 2, True)], f"wrong native live routing: {calls}")


def test_scheduled_workflow_is_strictly_read_only() -> None:
    text = (ROOT / ".github/workflows/archive-backlog-repair.yml").read_text(encoding="utf-8")
    for marker in [
        "timeout-minutes: 15",
        "ref: main",
        "contents: read",
        "--kind record_chain_arweave",
        "--kind native_ots_bundle",
        "--mode dry-run",
        "This scheduled workflow never uploads to Arweave",
        "Paid repair requires an explicit human dispatch",
    ]:
        require(marker in text, f"read-only backlog workflow missing marker: {marker}")
    for forbidden in [
        "--mode live",
        "--enable-paid-upload",
        "secrets.ARKEY",
        "vars.ARKEY",
        "ARWEAVE_JWK",
        "contents: write",
        "git push",
        "git commit",
        "git add",
        "regenerate_and_stage",
    ]:
        require(forbidden not in text, f"scheduled backlog scan retains paid/write capability: {forbidden}")


def main() -> int:
    test_synthetic_dry_run_never_routes_to_mutators()
    test_real_cli_dry_run_preserves_backlog_bytes()
    test_live_mode_is_explicit_and_routed()
    test_scheduled_workflow_is_strictly_read_only()
    print("PASS: archive backlog dry-run is read-only; live repair remains explicit and unscheduled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
