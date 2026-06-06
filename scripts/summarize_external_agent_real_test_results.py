#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_RECORDS = [
    "echo",
    "verification-v0",
    "verification-v1",
    "verification-v2",
    "verification-v3",
    "guardian-application",
]

FORBIDDEN_MARKERS = [
    "github_pat",
    "ghp_",
    "github token",
    "clone",
    "git clone",
    "arweave key",
    "arweave jwk",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize external agent real test results."
    )
    parser.add_argument("--dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    results_dir = Path(args.dir)
    if not results_dir.is_dir():
        raise SystemExit(f"results directory missing: {results_dir}")

    missing_records = []
    records_found = []
    forbidden_found = []

    for record_name in REQUIRED_RECORDS:
        submission_file = results_dir / f"{record_name}.submission.json"
        receipt_file = results_dir / f"{record_name}.receipt.json"

        if not submission_file.exists():
            missing_records.append(f"{record_name}.submission.json")
            continue
        if not receipt_file.exists():
            missing_records.append(f"{record_name}.receipt.json")
            continue

        try:
            submission = read_json(submission_file)
        except Exception as e:
            missing_records.append(f"{record_name}.submission.json (invalid: {e})")
            continue

        try:
            receipt = read_json(receipt_file)
        except Exception as e:
            missing_records.append(f"{record_name}.receipt.json (invalid: {e})")
            continue

        # Check for forbidden markers in submission text
        submission_text = json.dumps(submission, ensure_ascii=False).lower()
        for marker in FORBIDDEN_MARKERS:
            if marker in submission_text:
                forbidden_found.append(f"{record_name}: {marker}")

        records_found.append({
            "record_name": record_name,
            "record_type": submission.get("record_type"),
            "receipt_id": receipt.get("receipt_id"),
            "accepted": receipt.get("accepted", receipt.get("result") == "accepted"),
            "oath_policy_sha256": submission.get("oath_policy_sha256"),
            "participant_readback_sha256": submission.get("participant_readback_sha256"),
        })

    result = "pass" if not missing_records and not forbidden_found else "fail"

    summary = {
        "result": result,
        "records_found": records_found,
        "missing_required_records": missing_records,
        "forbidden_markers_found": forbidden_found,
        "total_records": len(records_found),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))

    if result != "pass":
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
