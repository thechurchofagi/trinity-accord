#!/usr/bin/env python3
"""Phase 2: Agent Entrypoint Audit.

Validates agent entrypoint files for context depth, boundary declarations,
and machine-readable constraints.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTDIR = ROOT / "audit" / "redteam" / "e2e-agent-echo-verification"


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTDIR))
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    findings = []
    total_checks = 0
    total_passed = 0
    total_failed = 0

    # Check agent entrypoint files exist and contain key constraints
    entrypoints = {
        "/agent-first-contact": ["boundary", "not authority", "verify"],
        "/agent-start": ["boundary", "canonical", "bitcoin"],
        "/agent-brief": ["classification", "boundary", "not religion"],
        "/agent-verify": ["claim gate", "verification level", "limitation"],
        "/agent-echo": ["echo", "not amendment", "boundary"],
        "/agent-submit": ["submission", "issue", "gateway"],
    }

    for path_suffix, required_keywords in entrypoints.items():
        md_path = ROOT / f"{path_suffix.lstrip('/')}.md"
        total_checks += 1
        if not md_path.exists():
            total_failed += 1
            findings.append({
                "severity": "high",
                "title": f"Missing entrypoint: {path_suffix}",
                "file": f"{path_suffix}.md",
            })
            continue

        text = md_path.read_text(encoding="utf-8").lower()
        total_passed += 1

        for kw in required_keywords:
            total_checks += 1
            if kw.lower() in text:
                total_passed += 1
            else:
                total_failed += 1
                findings.append({
                    "severity": "medium",
                    "title": f"Entrypoint missing keyword: '{kw}'",
                    "file": f"{path_suffix}.md",
                    "description": f"Expected keyword '{kw}' not found in {path_suffix}",
                })

    # Check JSON entrypoints
    json_entrypoints = [
        "/api/agent-entry-protocol.json",
        "/api/agent-required-reading.json",
        "/api/agent-first-contact.json",
    ]

    for path_suffix in json_entrypoints:
        json_path = ROOT / path_suffix.lstrip("/")
        total_checks += 1
        if not json_path.exists():
            total_failed += 1
            findings.append({"severity": "high", "title": f"Missing JSON entrypoint: {path_suffix}", "file": path_suffix})
            continue

        try:
            data = json.loads(json_path.read_text())
            total_passed += 1
        except json.JSONDecodeError:
            total_failed += 1
            findings.append({"severity": "high", "title": f"Invalid JSON: {path_suffix}", "file": path_suffix})
            continue

        # Check for recommended_sequence or context_depth
        total_checks += 1
        text = json.dumps(data).lower()
        if "recommended_sequence" in text or "context_depth" in text or "required_reading" in text:
            total_passed += 1
        else:
            total_failed += 1
            findings.append({
                "severity": "medium",
                "title": f"Entrypoint JSON missing guidance: {path_suffix}",
                "file": path_suffix,
                "description": "Expected recommended_sequence, context_depth, or required_reading",
            })

    # Check llms.txt and ai.txt
    for fname in ["llms.txt", "ai.txt", ".well-known/agent.json"]:
        fpath = ROOT / fname
        total_checks += 1
        if fpath.exists():
            total_passed += 1
        else:
            total_failed += 1
            findings.append({"severity": "low", "title": f"Missing optional entrypoint: {fname}", "file": fname})

    result = {
        "phase": "entrypoints",
        "checks": total_checks,
        "passed": total_passed,
        "failed": total_failed,
        "warnings": 0,
        "findings": findings,
    }
    (outdir / "entrypoints_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"Entrypoint Audit: {total_checks} checks, {total_passed} passed, {total_failed} failed")
    for f in findings:
        print(f"  [{f['severity'].upper()}] {f['title']}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
