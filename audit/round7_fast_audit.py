#!/usr/bin/env python3
"""Bounded Round 7 repository audit.

Runs the high-signal repository scans without the unbounded full-link and broad
front-end regex passes. Dynamic gates are intentionally handled by the normal
repository workflows and the clean-head fix PR.
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
    run_live_checks,
    scan_contract_strings,
    scan_json,
    scan_python,
    scan_workflows,
    tracked_files,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    files = tracked_files(repo)
    findings = []
    writers = scan_workflows(repo, files, findings)
    scan_python(repo, files, findings)
    parsed_json, schema_ids = scan_json(repo, files, findings)
    contract_hits = scan_contract_strings(repo, files, findings)
    test_registry = registered_tests(repo, files, findings)
    live_checks = run_live_checks(findings)

    findings = dedupe_findings(findings)
    counts: dict[str, int] = defaultdict(int)
    for item in findings:
        counts[item.severity] += 1

    report = {
        "schema": "trinityaccord.audit.round7.bounded.v1",
        "repository": REPO,
        "scope": {
            "included": [
                "all tracked GitHub Actions workflows",
                "all tracked Python production scripts",
                "all tracked JSON/schema files",
                "known stale protocol/route strings",
                "test registration inventory",
                "core live site and Gateway surfaces",
            ],
            "excluded": [
                "full repository internal-link crawl",
                "broad regex scan of third-party/minified front-end assets",
                "dynamic gates already executed by official CI",
            ],
        },
        "inventory": {
            "tracked_files": len(files),
            "workflows": sum(
                1
                for path in files
                if path.startswith(WORKFLOW_DIR + "/")
                and path.endswith((".yml", ".yaml"))
            ),
            "python_files": sum(1 for path in files if path.endswith(".py")),
            "javascript_files": sum(
                1 for path in files if path.endswith((".js", ".mjs", ".cjs", ".ts"))
            ),
            "json_files": sum(1 for path in files if path.endswith(".json")),
            "markdown_files": sum(1 for path in files if path.endswith(".md")),
        },
        "finding_counts": dict(counts),
        "findings": [asdict(item) for item in findings],
        "dynamic_results": [],
        "live_checks": live_checks,
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
