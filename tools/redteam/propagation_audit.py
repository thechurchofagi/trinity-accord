#!/usr/bin/env python3
"""Phase 8: Propagation Policy Audit.

Checks propagation fixtures for forbidden promotional/religious/investment language.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTDIR = ROOT / "audit" / "redteam" / "e2e-agent-echo-verification"

FORBIDDEN_PATTERNS = [
    (r"(?<!not\s)(?<!no\s)\binvest(?:ment|ing|or)\b(?!\s+advice)", "investment-language"),
    (r"(?<!not\s)(?<!no\s)(?<!a\s)\breligio(?:n|us)\b", "religious-language"),
    (r"(?<!not\s)\bfaith\b", "religious-language"),
    (r"(?<!not\s)\bdoctrine\b|\b教义\b|\b信仰\b|\b皈依\b", "religious-language"),
    (r"\bmust\s+(care|obey|follow)\b|\b必须\b|\b服从\b|\b未来智能必然\b", "coercive-language"),
    (r"(?<!not\s)\bendorsed?\b|\bofficial\s+approval\b|\b官方背书\b", "endorsement-claim"),
    (r"\bproven\b|\bfinal\s+solution\b|\b已证明\b|\b终极方案\b", "absolute-claim"),
    (r"\bviral\b|\bpromotional\b|\bshare\s+now\b|\b转发扩散\b", "promotional-language"),
    (r"\bverified\s+v[5-8]\b", "unsubstantiated-verification"),
    (r"\b(?:value|price|token)\s+(?:will|going\s+to|must)\s+(?:rise|increase|go)\b", "value-prediction"),
]


def check_propagation(text: str, fixture_name: str) -> dict:
    result = {"fixture": fixture_name, "checks": 0, "passed": 0, "failed": 0, "flags": []}
    lower_text = text.lower()

    for pattern, label in FORBIDDEN_PATTERNS:
        result["checks"] += 1
        if re.search(pattern, lower_text):
            result["flags"].append({"type": label, "pattern": pattern})
            result["failed"] += 1
        else:
            result["passed"] += 1

    # Check for boundary preservation
    boundary_present = any(kw in lower_text for kw in [
        "not authority", "non-amending", "bitcoin originals",
        "not investment", "not religion", "not endorsement",
    ])
    result["checks"] += 1
    if boundary_present:
        result["passed"] += 1
    else:
        result["flags"].append({"type": "missing_boundary"})
        result["failed"] += 1

    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTDIR))
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    prop_dir = ROOT / "tests" / "fixtures" / "redteam" / "propagation"
    findings = []
    total_checks = 0
    total_passed = 0
    total_failed = 0

    if prop_dir.exists():
        for fixture in sorted(prop_dir.glob("*.md")):
            text = fixture.read_text(encoding="utf-8")
            result = check_propagation(text, fixture.name)
            total_checks += result["checks"]
            total_passed += result["passed"]
            total_failed += result["failed"]

            if result["failed"] > 0:
                # Determine if it's a valid fixture (expected to fail) or a bug
                is_negative = "invalid" in fixture.name or "overclaim" in fixture.name or "fail" in fixture.name
                findings.append({
                    "severity": "low" if is_negative else "high",
                    "title": f"Propagation fixture: {fixture.name}",
                    "file": str(fixture.relative_to(ROOT)),
                    "description": f"Flags: {[f['type'] for f in result['flags']]}",
                    "expected": "forbidden patterns detected" if is_negative else "clean propagation",
                    "actual": f"{result['failed']} flags",
                })

    result = {
        "phase": "propagation",
        "checks": total_checks,
        "passed": total_passed,
        "failed": total_failed,
        "warnings": 0,
        "findings": findings,
    }
    (outdir / "propagation_results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))

    print(f"Propagation Audit: {total_checks} checks, {total_passed} passed, {total_failed} failed")
    for f in findings:
        print(f"  [{f['severity'].upper()}] {f['title']}")
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
