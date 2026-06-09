#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    p = ROOT / path
    require(p.exists(), f"missing {path}")
    return p.read_text(encoding="utf-8")


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def git(cmd: list[str], cwd: Path) -> str:
    return run(["git", *cmd], cwd=cwd).stdout.strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def check_guard(
    repo: Path,
    base: str,
    head: str,
    mode: str = "push",
    actor: str = "github-actions[bot]",
    gateway_actors: str = "",
) -> subprocess.CompletedProcess[str]:
    return run(
        [
            sys.executable,
            "scripts/check_record_chain_write_path_guard.py",
            "--mode",
            mode,
            "--base",
            base,
            "--head",
            head,
            "--github-actor",
            actor,
            "--gateway-actors",
            gateway_actors,
        ],
        cwd=repo,
        check=False,
    )


def commit(repo: Path, message: str) -> str:
    run(["git", "add", "."], cwd=repo)
    run(["git", "commit", "-m", message], cwd=repo)
    return git(["rev-parse", "HEAD"], cwd=repo)


def main() -> None:
    guard_script = read("scripts/check_record_chain_write_path_guard.py")
    guard_workflow = read(".github/workflows/record-chain-write-path-guard.yml")
    auto_finalize = read(".github/workflows/record-chain-auto-finalize.yml")
    ots_workflow = read(".github/workflows/record-chain-head-ots-anchor.yml")
    arweave_workflow = read(".github/workflows/record-chain-arweave-archive.yml")
    runner = read("scripts/run_current_system_tests.py")

    ast.parse(guard_script)

    for needle in [
        "INTAKE_IMMUTABLE_PREFIXES",
        "PENDING_PREFIXES",
        "AUTO_FINALIZE_PREFIXES",
        "AUTO_FINALIZE_FILES",
        "OTS_PREFIXES",
        "OTS_FILES",
        "ARWEAVE_PREFIXES",
        "ARWEAVE_FILES",
        "PUBLIC_GENERATED_FILES",
        "MAINTENANCE_OVERRIDE_TOKEN",
        "APPROVED_ACTIONS_ACTOR",
        "RECORD_CHAIN_GATEWAY_ACTORS",
        "api/record-chain-status.json",
        "record-chain/maintenance-overrides/",
        "record-chain: auto-finalize accepted submissions",
        "Append record-chain entries from Render intake",
        "APPROVED_APPEND_MESSAGE",
        "append workflow",
        "anchor: stamp native record-chain head with OTS",
        "archive: update native record-chain Arweave archive metadata",
        "intake: submission ",
        "intake: pending ",
        "intake: receipt ",
        "protected runtime data changed across multiple commits",
        "gateway intake actor allow-list is not configured",
        "github-actor",
        "gateway-actors",
    ]:
        require(needle in guard_script or needle in guard_workflow, f"guard missing {needle}")

    for protected_path in [
        "record-chain/records/",
        "record-chain/indexes/",
        "record-chain/processed/",
        "record-chain/rejected/",
        "record-chain/pending/",
        "record-chain/chain-tip.json",
        "record-chain/hash-chain/main.chain.jsonl",
        "api/record-chain-head.json",
    ]:
        require(protected_path in guard_script, f"guard script does not classify {protected_path}")

    require("pull_request:" in guard_workflow, "write-path guard must run on pull_request")
    require("push:" in guard_workflow, "write-path guard must run on push")
    require("permissions:" in guard_workflow and "contents: read" in guard_workflow, "write-path guard must be read-only")
    require("scripts/check_record_chain_write_path_guard.py" in guard_workflow, "workflow must invoke guard script")
    require("--mode pull-request" in guard_workflow, "workflow must check PR mode")
    require("--mode push" in guard_workflow, "workflow must check push mode")
    require("--github-actor" in guard_workflow, "workflow must pass github.actor to guard")
    require("--gateway-actors" in guard_workflow, "workflow must pass configured gateway actors")
    require("vars.RECORD_CHAIN_GATEWAY_ACTORS" in guard_workflow, "workflow must use gateway actor repo variable")
    require("fetch-depth: 0" in guard_workflow, "workflow must fetch history for diffs")

    for path in [
        "record-chain/pending",
        "record-chain/processed",
        "record-chain/rejected",
        "record-chain/records",
        "record-chain/chain-tip.json",
        "record-chain/indexes",
    ]:
        require(path in auto_finalize, f"auto-finalize workflow must commit {path}")
    require("git add -A" in auto_finalize, "auto-finalize must use git add -A for moves/deletions")
    require("record-chain: auto-finalize accepted submissions" in auto_finalize, "auto-finalize commit message must remain stable")

    require("Record Chain Auto Finalize" in ots_workflow, "OTS must remain chained to Auto Finalize")
    require("Append Record Chain Entries" in ots_workflow, "OTS must listen to Append Record Chain Entries")
    require("workflow_dispatch:" in ots_workflow, "OTS manual repair dispatch must remain available")
    require("record-chain/records/**" not in ots_workflow, "OTS must not accept arbitrary records push trigger")
    require("push:" not in ots_workflow or "record-chain/chain-tip.json" not in ots_workflow.split("push:")[1].split("workflow_run:")[0] if "push:" in ots_workflow else True, "OTS must not accept arbitrary chain-tip push trigger")

    require('workflows: ["Record Chain Head OTS Anchor"]' in arweave_workflow, "Arweave must remain chained to OTS")
    require("workflow_dispatch:" in arweave_workflow, "Arweave manual repair dispatch must remain available")

    require("test_record_chain_write_path_guard_contract.py" in runner, "current system tests must run write-path guard contract")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
        run(["git", "config", "user.name", "Write Path Guard Test"], cwd=repo)
        write(repo / "scripts/check_record_chain_write_path_guard.py", guard_script)
        base = commit(repo, "init")

        write(repo / "index.md", "hello\n")
        public_head = commit(repo, "docs: update public page")
        result = check_guard(repo, base, public_head)
        require(result.returncode == 0, f"public generated-only change should pass:\n{result.stdout}\n{result.stderr}")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
        run(["git", "config", "user.name", "Write Path Guard Test"], cwd=repo)
        write(repo / "scripts/check_record_chain_write_path_guard.py", guard_script)
        base = commit(repo, "init")

        write(repo / "record-chain/records/R-999999999.json", "{}\n")
        head = commit(repo, "manual record write")
        result = check_guard(repo, base, head, actor="human-user")
        require(result.returncode != 0, "unauthorized direct record write must fail")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
        run(["git", "config", "user.name", "Write Path Guard Test"], cwd=repo)
        write(repo / "scripts/check_record_chain_write_path_guard.py", guard_script)
        base = commit(repo, "init")

        write(repo / "record-chain/records/R-999999999.json", "{}\n")
        head = commit(repo, "record-chain: auto-finalize accepted submissions")
        result = check_guard(repo, base, head, actor="human-user")
        require(result.returncode != 0, "human actor spoofing auto-finalize message must fail")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
        run(["git", "config", "user.name", "Write Path Guard Test"], cwd=repo)
        write(repo / "scripts/check_record_chain_write_path_guard.py", guard_script)
        write(repo / "record-chain/pending/pending.json", "{}\n")
        base = commit(repo, "init")

        run(["git", "rm", "record-chain/pending/pending.json"], cwd=repo)
        write(repo / "record-chain/records/R-000000001.json", "{}\n")
        write(repo / "record-chain/chain-tip.json", "{}\n")
        write(repo / "record-chain/indexes/record-index.json", "{}\n")
        write(repo / "record-chain/processed/pending.json", "{}\n")
        head = commit(repo, "record-chain: auto-finalize accepted submissions")
        result = check_guard(repo, base, head, actor="github-actions[bot]")
        require(result.returncode == 0, f"approved auto-finalize write should pass:\n{result.stdout}\n{result.stderr}")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
        run(["git", "config", "user.name", "Write Path Guard Test"], cwd=repo)
        write(repo / "scripts/check_record_chain_write_path_guard.py", guard_script)
        base = commit(repo, "init")

        write(repo / "record-chain/pending/rcg-test.echo.pending.json", "{}\n")
        head = commit(repo, "intake: pending rcg-test (echo)")
        result = check_guard(repo, base, head, actor="gateway-runtime", gateway_actors="gateway-runtime")
        require(result.returncode == 0, f"allowed gateway pending commit should pass:\n{result.stdout}\n{result.stderr}")

        result = check_guard(repo, base, head, actor="human-user", gateway_actors="gateway-runtime")
        require(result.returncode != 0, "disallowed actor spoofing gateway pending commit must fail")

        result = check_guard(repo, base, head, actor="gateway-runtime", gateway_actors="")
        require(result.returncode != 0, "gateway pending commit must fail when gateway actor allow-list is unset")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
        run(["git", "config", "user.name", "Write Path Guard Test"], cwd=repo)
        write(repo / "scripts/check_record_chain_write_path_guard.py", guard_script)
        base = commit(repo, "init")

        write(repo / "record-chain/records/R-999999999.json", "{}\n")
        write(repo / "record-chain/chain-tip.json", "{}\n")
        write(repo / "record-chain/indexes/record-index.json", "{}\n")
        write(repo / "api/record-chain-status.json", "{}\n")
        write(repo / "api/public-home-status.json", "{}\n")
        write(repo / "index.md", "status\n")
        write(repo / "sitemap.xml", "<urlset />\n")
        head = commit(repo, "Append record-chain entries from Render intake")
        result = check_guard(repo, base, head, actor="github-actions[bot]")
        require(result.returncode == 0, f"append workflow with status/public generated should pass:\n{result.stdout}\n{result.stderr}")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
        run(["git", "config", "user.name", "Write Path Guard Test"], cwd=repo)
        write(repo / "scripts/check_record_chain_write_path_guard.py", guard_script)
        base = commit(repo, "init")

        write(repo / "record-chain/arweave-archives/archive.json", "{}\n")
        write(repo / "api/record-chain-arweave-index.json", "{}\n")
        write(repo / "api/record-chain-status.json", "{}\n")
        write(repo / "api/public-home-status.json", "{}\n")
        write(repo / "index.md", "archive\n")
        write(repo / "sitemap.xml", "<xml />\n")
        head = commit(repo, "archive: update native record-chain Arweave archive metadata")
        result = check_guard(repo, base, head, actor="github-actions[bot]")
        require(result.returncode == 0, f"approved Arweave archive write should pass:\n{result.stdout}\n{result.stderr}")

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "test@example.invalid"], cwd=repo)
        run(["git", "config", "user.name", "Write Path Guard Test"], cwd=repo)
        write(repo / "scripts/check_record_chain_write_path_guard.py", guard_script)
        base = commit(repo, "init")

        write(repo / "record-chain/records/R-1.json", "{}\n")
        commit(repo, "record-chain: auto-finalize accepted submissions")
        write(repo / "record-chain/records/R-2.json", "{}\n")
        head = commit(repo, "record-chain: auto-finalize accepted submissions")
        result = check_guard(repo, base, head, actor="github-actions[bot]")
        require(result.returncode != 0, "multi-commit protected push must fail")

    print("Record-chain write-path guard contract PASSED.")


if __name__ == "__main__":
    main()

