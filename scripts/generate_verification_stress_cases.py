#!/usr/bin/env python3
"""
Generate synthetic JSON files from cases.json for the verification stress suite.
Usage: python3 scripts/generate_verification_stress_cases.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "verification_cases" / "cases.json"
GENERATED_DIR = ROOT / "tests" / "verification_cases" / "generated"


def main():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = manifest.get("cases", [])
    generated = 0

    for case in cases:
        if case.get("input_type") != "synthetic_json":
            continue
        case_id = case["id"]
        payload = case.get("payload", {})
        if not payload:
            continue
        out_path = GENERATED_DIR / f"{case_id}.json"
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        generated += 1

    print(f"Generated {generated} synthetic case files in {GENERATED_DIR.relative_to(ROOT)}")
    print("FINAL: PASS — generated verification stress cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
