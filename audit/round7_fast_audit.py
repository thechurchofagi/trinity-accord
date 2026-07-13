#!/usr/bin/env python3
"""Bounded Round 7 active-surface audit.

Scans every workflow plus active scripts/apps/public contracts. Historical
records, archive bundles, proofs, and audit logs are intentionally excluded
from this pass because dedicated integrity/secret gates already validate them.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))

from round7_system_audit import (  # noqa: E402
    REPO,
    WORKFLOW_DIR,
    dedupe_findings,
    markdown_report,
    registered_tests,
    scan_contract_strings,
    scan_json,
    scan_python,
    scan_workflows,
    tracked_files,
)


def active_contract_file(repo: Path, path: str) -> bool:
    if path.startswith((".github/workflows/", "scripts/", "apps/", "api/")):
        try:
            return (repo / path).stat().st_size <= 1_500_000
        except OSError:
            return False
    if path in {
        "render.yaml",
        "package.json",
        "requirements-ci.txt",
        "requirements-ots.txt",
        "index.md",
        "agent-start.md",
        "agent-first-contact.md",
    }:
        return True
    if path.startswith("docs/") and path.endswith(".md"):
        try:
            return (repo / path).stat().st_size <= 500_000
        except OSError:
            return False
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    files = tracked_files(repo)
    workflow_files = [
        path
        for path in files
        if path.startswith(WORKFLOW_DIR + "/") and path.endswith((".yml", ".yaml"))
    ]
    python_files = [
        path
        for path in files
        if path.endswith(".py") and path.startswith(("scripts/", "apps/"))
    ]
    json_files = [
        path
        for path in files
        if path.endswith(".json")
        and (
            path.startswith("api/")
            or "/schemas/" in path
            or path in {"package.json"}
        )
        and active_contract_file(repo, path)
    ]
    contract_files = [path for path in files if active_contract_file(repo, path)]

    findings = []
    writers = scan_workflows(repo, workflow_files, findings)
    scan_python(repo, python_files, findings)
    parsed_json, schema_ids = scan_json(repo, json_files, findings)
    contract_hits = scan_contract_strings(repo, contract_files, findings)
    test_registry = registered_tests(repo, files, findings)

    findings = dedupe_findings(findings)
    counts: dict[str, int] = defaultdict(int)
    for item in findings:
        counts[item.severity] += 1

    report = {
        "schema": "trinityaccord.audit.round7.active-surfaces.v1",
        "repository": REPO,
        "scope": {
            "included": [
                "all tracked GitHub Actions workflows",
                "active scripts/ and apps/ Python",
                "public api/ JSON and application schemas",
                "bounded docs/current route and protocol strings",
                "complete test registration inventory",
            ],
            "excluded": [
                "historical record and archive payload bodies",
                "OTS and Arweave proof bundles",
                "audit logs and generated historical evidence",
                "third-party/minified front-end assets",
                "dynamic gates already executed by official CI",
            ],
        },
        "inventory": {
            "tracked_files": len(files),
            "workflows_total": len(workflow_files),
            "python_active_scanned": len(python_files),
            "public_json_scanned": len(json_files),
            "active_contract_files_scanned": len(contract_files),
            "python_files_total": sum(1 for path in files if path.endswith(".py")),
            "json_files_total": sum(1 for path in files if path.endswith(".json")),
        },
        "finding_counts": dict(counts),
        "findings": [asdict(item) for item in findings],
        "dynamic_results": [],
        "live_checks": [],
        "workflow_writers": writers,
        "schema_ids": schema_ids,
        "contract_hits": contract_hits,
        "test_registry": test_registry,
        "parsed_json_count": len(parsed_json),
    }

    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output / "report.md").write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps({"finding_counts": dict(counts), "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
