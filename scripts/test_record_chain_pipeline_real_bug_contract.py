#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
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


def main() -> None:
    auto_finalize = read("scripts/auto_finalize_accepted_submissions.py")
    ots_workflow = read(".github/workflows/record-chain-head-ots-anchor.yml")
    auto_finalize_workflow = read(".github/workflows/record-chain-auto-finalize.yml")
    chain = read("scripts/trinity_record_chain.py")
    finalizer = read("scripts/finalize_mainnet_prelaunch_record_from_submission.py")
    build_indexes = read("scripts/build_record_chain_indexes.py")

    for label, text in [
        ("scripts/auto_finalize_accepted_submissions.py", auto_finalize),
        ("scripts/trinity_record_chain.py", chain),
        ("scripts/finalize_mainnet_prelaunch_record_from_submission.py", finalizer),
        ("scripts/build_record_chain_indexes.py", build_indexes),
    ]:
        try:
            ast.parse(text)
        except SyntaxError as exc:
            fail(f"{label} has syntax error: {exc}")

    # P0: auto-finalize must skip receipts already handled by native pending path.
    require(
        "def native_pending_artifact_status" in auto_finalize,
        "auto-finalize must define native_pending_artifact_status",
    )
    for needle in [
        '"pending"',
        '"processed"',
        '"rejected"',
        "native_pending_{native_state}",
        "pending_file_path",
    ]:
        require(needle in auto_finalize, f"auto-finalize missing native pending skip contract: {needle}")

    # P1: OTS schedule must not be blocked by job-level if.
    require("schedule:" in ots_workflow, "OTS workflow must still declare schedule")
    require(
        "github.event_name != 'workflow_run' || github.event.workflow_run.conclusion == 'success'" in ots_workflow,
        "OTS workflow job if must allow schedule and workflow_dispatch while gating workflow_run success",
    )
    require(
        "github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success'" not in ots_workflow,
        "old OTS job if blocks schedule and must not remain",
    )

    # P1: auto-finalize must stage actual generated legacy index files.
    for required in [
        "api/record-chain-index.all.json",
        "api/record-chain-index.manifest.json",
        "api/record-chain-index.*.json",
    ]:
        require(
            required in auto_finalize_workflow,
            f"auto-finalize workflow must git add generated index file/glob: {required}",
        )

    # P1: append must fail closed for non-canonical pending files.
    require(
        "TRINITY_ALLOW_LOCAL_FINALIZER_PENDING" in chain,
        "trinity_record_chain.py must gate finalizer-local pending with env var",
    )
    require(
        "def allow_local_finalizer_pending" in chain,
        "trinity_record_chain.py must define allow_local_finalizer_pending",
    )
    require(
        "def require_pending_file_is_appendable" in chain,
        "trinity_record_chain.py must define require_pending_file_is_appendable",
    )
    require(
        "refusing non-canonical pending file outside finalizer-local mode" in chain,
        "trinity_record_chain.py must fail closed on stray pending files",
    )
    require(
        "require_pending_file_is_appendable(path)" in chain,
        "append_records must call require_pending_file_is_appendable(path)",
    )

    # P1 companion: finalizer must set env var only for its local append.
    require("import os" in finalizer, "finalizer must import os")
    require(
        'append_env["TRINITY_ALLOW_LOCAL_FINALIZER_PENDING"] = "1"' in finalizer,
        "finalizer must explicitly enable local pending append only for its append call",
    )
    require("env=append_env" in finalizer, "finalizer append call must pass append_env")

    # P2: manifest authority must retain fail-closed wording and not be overwritten.
    require(
        "legacy hash-chain derived indexes; not current native Record-Chain authority" in build_indexes,
        "manifest must retain fail-closed legacy authority wording",
    )
    require(
        build_indexes.count('"authority": "derived indexes; main.chain.jsonl is authoritative"') == 0,
        "duplicate overwritten manifest authority must be removed",
    )

    print("PASS: record-chain pipeline real-bug contract")


if __name__ == "__main__":
    main()
