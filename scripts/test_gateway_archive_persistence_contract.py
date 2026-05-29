#!/usr/bin/env python3
"""Test: gateway-archive-persistence-contract.v1.json satisfies required structure."""
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    path = ROOT / "api" / "gateway-archive-persistence-contract.v1.json"
    if not path.exists():
        print("FAIL: contract file not found")
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))

    checks = [
        (data.get("schema") == "trinityaccord.gateway-archive-persistence-contract.v1",
         "schema is trinityaccord.gateway-archive-persistence-contract.v1"),
        ("archive:agent-declared-echo" in data.get("source_issue_requirements", {}).get("required_labels", []),
         "required labels include archive:agent-declared-echo"),
        ("echo:invalid" in data.get("source_issue_requirements", {}).get("forbidden_labels", []),
         "forbidden labels include echo:invalid"),
        ("not-counted" in data.get("source_issue_requirements", {}).get("forbidden_labels", []),
         "forbidden labels include not-counted"),
        (data.get("workflow_requirements", {}).get("permissions", {}).get("contents") == "write",
         "workflow permissions require contents: write"),
        (data.get("workflow_requirements", {}).get("permissions", {}).get("issues") == "write",
         "workflow permissions require issues: write"),
        (data.get("workflow_requirements", {}).get("must_not_require_issue_open") is True,
         "workflow must not require issue open"),
        (any(r.get("issue") == 304 for r in data.get("known_regressions", [])),
         "known regression #304 is present"),
    ]

    # Verify source_digest
    clone = dict(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    expected_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    checks.append(
        (data.get("source_digest") == expected_digest,
         f"source_digest is correct ({expected_digest})")
    )

    failed = [msg for ok, msg in checks if not ok]
    for ok, msg in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {msg}")

    if failed:
        print(f"\nFAILED: {len(failed)} check(s)")
        return 1

    print("\nPASS: gateway-archive-persistence-contract.v1.json satisfies all checks")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
