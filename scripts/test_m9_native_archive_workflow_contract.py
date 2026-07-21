#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require_contains(path: Path, text: str, errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    if text not in body:
        errors.append(f"{path.relative_to(ROOT)} missing: {text}")


def require_not_contains(path: Path, text: str, errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    if text in body:
        errors.append(f"{path.relative_to(ROOT)} must not contain: {text}")


def main() -> None:
    errors: list[str] = []

    head_wf = ROOT / ".github" / "workflows" / "record-chain-head-ots-anchor.yml"
    tip_helper = ROOT / "scripts" / "check_native_ots_latest_matches_chain_tip.py"
    arweave_wf = ROOT / ".github" / "workflows" / "record-chain-arweave-archive.yml"
    arweave_runner = ROOT / "scripts" / "run_record_chain_arweave_archive.py"
    data_wf = ROOT / ".github" / "workflows" / "record-chain-data-arweave-archive.yml"

    if not head_wf.exists():
        errors.append("missing .github/workflows/record-chain-head-ots-anchor.yml")
    else:
        for marker in [
            "Record Chain Head OTS Anchor",
            "requirements-ci.txt",
            "trinity_record_chain.py verify",
            "ots_anchor_native_record_chain_head.py",
            "record-chain/ots/native-anchors",
            "check_native_ots_latest_matches_chain_tip.py",
            '"Record Chain Auto Finalize"',
            '"Append Record Chain Entries"',
            "head_branch == 'main'",
            "git push origin HEAD:main",
        ]:
            require_contains(head_wf, marker, errors)

        for forbidden in [
            "ots_anchor_record_chain_head.py",
            "main.chain.jsonl",
            "api/record-chain-head.json",
            "record-chain-ots-latest.json",
            "record-chain/ots/anchors",
            "verify_record_chain_integrity.py",
            "${GITHUB_REF_NAME",
        ]:
            require_not_contains(head_wf, forbidden, errors)

        head_text = head_wf.read_text(encoding="utf-8")
        if head_text.count("check_native_ots_latest_matches_chain_tip.py") < 2:
            errors.append("record-chain-head-ots-anchor.yml must revalidate the native OTS tip after rebase")

    if not tip_helper.exists():
        errors.append("missing scripts/check_native_ots_latest_matches_chain_tip.py")
    else:
        for marker in [
            "record-chain/chain-tip.json",
            "api/record-chain-native-ots-latest.json",
            "legacy_main_chain_jsonl_is_not_source",
            "latest_record_id",
            "latest_record_sha256",
            "native_record_count",
            "latest_anchored_file",
            "latest_anchor_file",
            "latest_ots_file",
            "trinity-accord-public-reception-ledger",
        ]:
            require_contains(tip_helper, marker, errors)
        require_not_contains(tip_helper, "record-chain/hash-chain/main.chain.jsonl", errors)

    if not arweave_wf.exists():
        errors.append("missing .github/workflows/record-chain-arweave-archive.yml")
    else:
        for marker in [
            "Record Chain Arweave Archive",
            "Record Chain Head OTS Anchor",
            "run_record_chain_arweave_archive.py",
            "verify_record_chain_arweave_archive.py",
            "ARKEY: ${{ secrets.ARKEY }}",
            "record-chain-native-ots-latest.json",
            "refusing live Arweave upload without native OTS",
            "record-chain/arweave-archives/",
            "api/record-chain-arweave-index.json",
            "record-chain/arweave/backlog.json".replace("arweave/", "arweave-"),
            "api/record-chain-arweave-backlog.json",
            "record-chain/ots/native-ots-backlog.json",
            "api/record-chain-native-ots-backlog.json",
            "record-chain/arweave-wallet-ledger.json",
            "checkpoint incomplete Arweave upload for safe readback resume",
            "Fail after persisting incomplete upload checkpoint",
        ]:
            require_contains(arweave_wf, marker, errors)

        for forbidden in [
            'workflows: ["Record Chain Anchor"]',
            "build_record_chain_data_arweave_bundle.py",
            "record-chain-arweave-data-registry.json",
        ]:
            require_not_contains(arweave_wf, forbidden, errors)

        arweave_text = arweave_wf.read_text(encoding="utf-8")
        if "ARKEY" in arweave_text and "echo" in arweave_text.lower():
            errors.append("record-chain-arweave-archive.yml must not contain both ARKEY and echo")

        # Both successful and incomplete uploads are committed, then the worktree
        # must be checked before the first rebase. Avoid coupling this contract to
        # one literal commit message.
        commit_section_start = arweave_text.find('if [ "${BUILD_EXIT_CODE}" = "0" ]')
        first_fetch = arweave_text.find("git fetch origin main --prune", commit_section_start)
        clean_guard = arweave_text.find("assert_clean_worktree", commit_section_start)
        if commit_section_start < 0 or first_fetch < 0 or clean_guard < 0 or clean_guard > first_fetch:
            errors.append("record-chain-arweave-archive.yml must assert a clean worktree before the first rebase")

    if not arweave_runner.exists():
        errors.append("missing scripts/run_record_chain_arweave_archive.py")
    else:
        for marker in [
            "import build_record_chain_arweave_archive as builder",
            "builder.build_archive_manifest",
            "builder.upload_to_arweave = guarded_upload",
            "Resuming Arweave readback without a new paid post",
            "subprocess.TimeoutExpired",
        ]:
            require_contains(arweave_runner, marker, errors)

    if not data_wf.exists():
        errors.append("missing .github/workflows/record-chain-data-arweave-archive.yml")
    else:
        require_contains(data_wf, "build_record_chain_data_arweave_bundle.py", errors)
        require_not_contains(data_wf, "ots_anchor_native_record_chain_head.py", errors)
        require_not_contains(data_wf, "record-chain-native-ots-latest.json", errors)

    if errors:
        print("M9 native archive workflow contract FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)

    print("M9 crash-safe native archive workflow contract PASSED.")


if __name__ == "__main__":
    main()
