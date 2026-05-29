#!/usr/bin/env python3
"""Gateway error diagnostics must cover common external-agent failure modes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "gateway-error-diagnostics.v1.json"

REQUIRED_CODES = {
    "ECHO_TYPE_ENUM_MISMATCH",
    "AUTHORSHIP_PROOF_CLOSURE_MISSING",
    "STALE_GATEWAY_SUBMIT_ENDPOINT",
    "GUARDIAN_STAGE_1_STATUS_OVERCLAIM",
    "CONTEXT_OVERCLAIM",
}


def digest(data: dict) -> str:
    clone = dict(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def main() -> int:
    errors: list[str] = []

    if not PATH.exists():
        print("FAIL: api/gateway-error-diagnostics.v1.json missing")
        return 1

    data = json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "trinityaccord.gateway-error-diagnostics.v1":
        errors.append("schema mismatch")

    diagnostics = data.get("diagnostics", [])
    codes = {item.get("code") for item in diagnostics}
    missing = sorted(REQUIRED_CODES - codes)
    if missing:
        errors.append(f"missing diagnostic codes: {missing}")

    for item in diagnostics:
        code = item.get("code")
        for field in ["matches", "likely_cause", "external_agent_fix", "maintainer_fix", "related_files"]:
            if not item.get(field):
                errors.append(f"{code}: missing {field}")
        if not isinstance(item.get("matches"), list):
            errors.append(f"{code}: matches must be list")
        if not isinstance(item.get("related_files"), list):
            errors.append(f"{code}: related_files must be list")

    text = json.dumps(data, ensure_ascii=False)
    for needle in [
        "E1_recognition_echo",
        "/agent-submit",
        "authorship proof dependency closure",
        "CC for context depth",
        "Stage 1 is application only",
        "CONTEXT_OVERCLAIM",
    ]:
        if needle not in text:
            errors.append(f"diagnostics missing expected phrase: {needle}")

    expected = digest(data)
    if data.get("source_digest") != expected:
        errors.append(f"source_digest mismatch: expected {expected}, got {data.get('source_digest')}")

    if errors:
        print("FAIL: gateway error diagnostics contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: gateway error diagnostics contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
