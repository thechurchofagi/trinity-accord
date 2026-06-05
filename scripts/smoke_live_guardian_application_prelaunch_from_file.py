#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_SITE = "https://www.trinityaccord.org"
FORBIDDEN_ENV = [
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_PAT",
    "ARWEAVE_JWK_PATH",
    "ARKEY",
    "ARWEAVE_PRIVATE_KEY",
]

FORMAL_NAME_MARKERS = [
    "刘烘炬",
    "Liu Hongju",
    "liu hongju",
    "original author",
    "founding guardian",
]

TEST_IDENTITY = "Test Founding Guardian Applicant"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def extract_readback_text(payload: dict[str, Any]) -> str:
    value = payload.get("client_oath_readback")
    if isinstance(value, str):
        readback = value
    elif isinstance(value, dict) and isinstance(value.get("readback_text"), str):
        readback = value["readback_text"]
    else:
        raise SystemExit("client_oath_readback must be a string or object.readback_text")

    readback = readback.strip()
    if len(readback) < 100:
        raise SystemExit("client_oath_readback readback_text missing or too short")
    return readback


def assert_no_sensitive_env() -> None:
    present = [key for key in FORBIDDEN_ENV if os.environ.get(key)]
    if present:
        raise SystemExit("forbidden privileged env present in external canary: " + ", ".join(present))


def fetch_json(url: str, timeout: int) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrinityPhase7APrelaunchCanary/1.0",
            "Accept": "application/json,*/*",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_json(url: str, payload: dict[str, Any], timeout: int) -> tuple[int, dict[str, Any]]:
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "User-Agent": "TrinityPhase7APrelaunchCanary/1.0",
            "Accept": "application/json,*/*",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return int(getattr(resp, "status", 200)), json.loads(body) if body.strip() else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body) if body.strip() else {}
        except Exception:
            parsed = {"raw_body": body}
        return int(exc.code), parsed


def discover(site: str, timeout: int) -> tuple[str, str, str]:
    agent = fetch_json(site.rstrip("/") + "/api/agent-start.v2.json", timeout)
    phase = agent.get("public_phase", {})
    if phase.get("status") != "public_test_stabilization":
        raise SystemExit("expected public_test_stabilization during prelaunch")
    if phase.get("not_final_public_launch") is not True:
        raise SystemExit("expected not_final_public_launch=true during prelaunch")

    method = agent.get("current_public_submission_method", {})
    base = method.get("gateway_base_url")
    preflight = method.get("preflight")
    submit = method.get("submit")
    if not base or not preflight or not submit:
        raise SystemExit("agent-start missing gateway base/preflight/submit")
    return str(base).rstrip("/"), str(preflight), str(submit)


def get_path(data: Any, dotted: str, default: Any = None) -> Any:
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def validate_test_only_submission(payload: dict[str, Any]) -> None:
    if payload.get("record_type") != "guardian_application":
        raise SystemExit("payload record_type must be guardian_application")

    raw = json.dumps(payload, ensure_ascii=False)
    for marker in FORMAL_NAME_MARKERS:
        if marker in raw:
            raise SystemExit(f"test-only canary must not contain formal applicant marker: {marker}")

    identity_text = json.dumps(get_path(payload, "record_draft.submitting_participant_identity", {}), ensure_ascii=False)
    if TEST_IDENTITY not in identity_text:
        raise SystemExit(f"test-only canary must use identity label {TEST_IDENTITY!r}")

    if payload.get("test_only") is not True:
        raise SystemExit("payload must set top-level test_only=true")
    if payload.get("canary") is not True:
        raise SystemExit("payload must set top-level canary=true")
    if payload.get("no_active_guardian_status_claim") is not True:
        raise SystemExit("payload must set no_active_guardian_status_claim=true")

    readback = extract_readback_text(payload)

    oath = get_path(payload, "record_draft.submission_oath_verification")
    if not isinstance(oath, dict):
        raise SystemExit("submission_oath_verification missing")

    required_true = [
        "oath_read",
        "readback_required",
        "participant_readback_provided",
        "readback_matches_canonical_oath",
        "readback_was_not_piped_from_file",
        "readback_was_not_generated_by_script",
        "readback_was_not_loaded_from_cache",
        "readback_was_not_summary_or_paraphrase",
        "readback_was_not_generated_by_external_automation",
        "readback_was_not_auto_filled_by_builder",
        "no_shortcut_oath_acknowledged",
        "not_authority",
        "not_governance",
        "not_attestation",
        "not_amendment",
        "bitcoin_originals_prevail",
    ]
    for key in required_true:
        if oath.get(key) is not True:
            raise SystemExit(f"oath declaration {key} must be true")

    expected_sha = sha256_text(readback)
    actual_sha = oath.get("participant_readback_sha256")
    if actual_sha and actual_sha != expected_sha:
        raise SystemExit("participant_readback_sha256 does not match client_oath_readback")


def mutate_missing_readback(payload: dict[str, Any]) -> dict[str, Any]:
    p = json.loads(json.dumps(payload))
    p.pop("client_oath_readback", None)
    return p


def mutate_false_readback_match(payload: dict[str, Any]) -> dict[str, Any]:
    p = json.loads(json.dumps(payload))
    p["record_draft"]["submission_oath_verification"]["readback_matches_canonical_oath"] = False
    return p


def mutate_false_no_shortcut(payload: dict[str, Any]) -> dict[str, Any]:
    p = json.loads(json.dumps(payload))
    p["record_draft"]["submission_oath_verification"]["no_shortcut_oath_acknowledged"] = False
    return p


def accepted(body: dict[str, Any]) -> bool:
    return body.get("accepted") is True


def preflight_ok(body: dict[str, Any]) -> bool:
    """A preflight is OK if accepted=true OR (preflight=true AND no error diagnostics)."""
    if body.get("accepted") is True:
        return True
    if body.get("preflight") is True:
        diagnostics = body.get("diagnostics", [])
        has_errors = any(d.get("severity") == "error" for d in diagnostics)
        return not has_errors
    return False


def expect_rejected(label: str, status: int, body: dict[str, Any]) -> None:
    if status < 400 and accepted(body):
        raise SystemExit(f"negative case {label} unexpectedly accepted: status={status} body={body}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prelaunch live guardian_application canary from externally prepared submission JSON.")
    parser.add_argument("--submission-json", required=True)
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--submit-positive-canary", action="store_true")
    parser.add_argument("--confirm-submit-positive-canary", default="")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    assert_no_sensitive_env()

    submission_path = Path(args.submission_json)
    payload = json.loads(submission_path.read_text(encoding="utf-8"))
    validate_test_only_submission(payload)

    base, preflight_path, submit_path = discover(args.site, args.timeout)

    result: dict[str, Any] = {
        "schema": "trinity_phase7a_prelaunch_live_guardian_application_canary.v1",
        "result": "unknown",
        "site": args.site,
        "gateway": base,
        "submission_json": str(submission_path),
        "formal_liu_hongju_application_submitted": False,
        "external_no_token": True,
        "client_oath_readback_shape": (
            "object" if isinstance(payload.get("client_oath_readback"), dict) else "string"
        ),
        "created_at": utc_now(),
        "checks": {}
    }

    for label, mutated in [
        ("missing_client_oath_readback", mutate_missing_readback(payload)),
        ("readback_matches_canonical_oath_false", mutate_false_readback_match(payload)),
        ("no_shortcut_oath_acknowledged_false", mutate_false_no_shortcut(payload)),
    ]:
        status, body = post_json(base + preflight_path, mutated, args.timeout)
        expect_rejected(label, status, body)
        result["checks"][label] = {"status": status, "accepted": accepted(body), "body": body}

    status, body = post_json(base + preflight_path, payload, args.timeout)
    if status >= 400 or not preflight_ok(body):
        raise SystemExit(f"positive preflight failed: status={status} body={body}")
    result["checks"]["positive_preflight"] = {"status": status, "preflight_ok": preflight_ok(body), "body": body}

    if args.submit_positive_canary:
        if args.confirm_submit_positive_canary != "I_UNDERSTAND_THIS_SUBMITS_A_TEST_ONLY_GUARDIAN_APPLICATION_CANARY":
            raise SystemExit("positive submit requires exact confirmation phrase")
        status, body = post_json(base + submit_path, payload, args.timeout)
        if status >= 400 or body.get("accepted") is not True:
            raise SystemExit(f"positive submit failed: status={status} body={body}")
        result["checks"]["positive_submit"] = {"status": status, "accepted": body.get("accepted"), "body": body}
    else:
        result["checks"]["positive_submit"] = {"skipped": True}

    result["result"] = "pass"

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
