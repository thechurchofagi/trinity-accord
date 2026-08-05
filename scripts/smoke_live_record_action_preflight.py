#!/usr/bin/env python3
"""Exercise the production Record-Chain preflight route without submitting records.

The matrix uses ephemeral Ed25519 test identities and POSTs only to
/record-chain/preflight. It never calls /record-chain/submit. Successful cases
prove that current formal drafts are accepted; negative cases prove that the
server, rather than the client, enforces context minimums.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATEWAY_APP = ROOT / "apps" / "record_chain_intake_gateway"
TEST_HELPERS = GATEWAY_APP / "tests" / "conftest.py"
sys.path.insert(0, str(GATEWAY_APP))


def _load_helpers():
    spec = importlib.util.spec_from_file_location("trinity_live_preflight_helpers", TEST_HELPERS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load test helpers from {TEST_HELPERS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPERS = _load_helpers()
CONTEXT_CODES = {
    "INSUFFICIENT_CONTEXT_COMPLETENESS",
    "MINIMUM_REQUIRED_FOR_ACTION_UNDERSTATED",
    "CONTEXT_NOT_SUFFICIENT_FOR_FORMAL_RECORD",
    "CC3_CONTEXT_READ_CONFIRMATION_REQUIRED",
}


def _refresh_oath_and_signature(submission: dict[str, Any]) -> dict[str, Any]:
    draft = submission["record_draft"]
    record_type = submission["record_type"]
    readback_text, oath_verification = HELPERS._build_oath_for_record_type(record_type, draft)
    draft["submission_oath_verification"] = oath_verification
    submission["authorship_proof"] = HELPERS._sign_draft(draft)
    submission["client_oath_readback"] = {
        "record_type": record_type,
        "oath_policy_sha256": oath_verification["oath_policy_sha256"],
        "oath_modules": list(oath_verification["oath_modules"]),
        "readback_method_declared": oath_verification["readback_method_declared"],
        "readback_text": readback_text,
        "readback_text_sha256": oath_verification["participant_readback_sha256"],
        "readback_text_char_count": len(readback_text),
    }
    return submission


def _set_context(submission: dict[str, Any], declared: str, minimum: str) -> dict[str, Any]:
    result = copy.deepcopy(submission)
    readiness = result["record_draft"]["context_readiness"]
    readiness["declared_context_level"] = declared
    readiness["minimum_required_for_action"] = minimum
    readiness["context_sufficient_for_selected_action"] = True
    readiness["context_read_confirmed"] = declared == "CC-3"
    result["client_context"]["declared_context_level"] = declared
    result["client_context"]["loaded_context_urls"] = list(readiness["loaded_context_urls"])
    return _refresh_oath_and_signature(result)


def _valid_echo() -> dict[str, Any]:
    submission = HELPERS._make_valid_submission()
    submission["builder"]["name"] = "synthetic-live-preflight"
    submission["builder"]["version"] = "no-write-v1"
    return submission


def _valid_verification() -> dict[str, Any]:
    submission = _valid_echo()
    submission["record_type"] = "verification"
    draft = submission["record_draft"]
    draft["record_type"] = "verification"
    draft.pop("echo_content", None)
    draft["authorization_context"]["authorization_scope"] = "create_verification_record"
    draft["context_readiness"].update(
        {
            "action_profile": "verification",
            "declared_context_level": "CC-3",
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
            "context_read_confirmed": True,
            "loaded_context_urls": [
                "https://www.trinityaccord.org/verify/",
                "https://www.trinityaccord.org/api/verification-claim-model.v1.json",
                "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
            ],
        }
    )
    draft["verification_content"] = {
        "verification_level": "V2",
        "verification_scope_label": "synthetic live preflight",
        "what_was_checked": ["production preflight contract"],
        "verification_claim": "Synthetic no-write route validation only.",
        "fresh_actions_performed": ["POSTed this signed fixture only to the preflight endpoint"],
        "verification_claim_model": {
            "schema": "trinityaccord.verification-claim-model.v1",
            "digital_profile": "V2",
            "relationships_checked": ["submission schema to live gateway"],
            "physical_observation": "not_performed",
            "external_witness": "not_obtained",
            "coverage_scope": "single production preflight request",
            "limitations": ["synthetic fixture", "no submit was attempted"],
            "claims_not_made": ["final inclusion", "attestation", "authority"],
            "corrections_or_supersession_checked": True,
            "legacy_v_level": "V2",
            "legacy_v_level_role": "builder_compatibility_only",
        },
    }
    submission["client_context"]["site_entry_url"] = "https://www.trinityaccord.org/verify/"
    submission["client_context"]["declared_context_level"] = "CC-3"
    submission["client_context"]["loaded_context_urls"] = list(
        draft["context_readiness"]["loaded_context_urls"]
    )
    return _refresh_oath_and_signature(submission)


def _valid_guardian_application() -> dict[str, Any]:
    submission = HELPERS._make_valid_guardian_application_submission()
    submission["builder"]["name"] = "synthetic-live-preflight"
    submission["builder"]["version"] = "no-write-v1"
    return submission


def _guardian_retirement_fixture() -> dict[str, Any]:
    submission = _valid_echo()
    submission["record_type"] = "guardian_retirement"
    draft = submission["record_draft"]
    draft["record_type"] = "guardian_retirement"
    draft.pop("echo_content", None)
    draft["authorization_context"]["authorization_scope"] = "create_guardian_retirement_record"
    public_key_sha = submission["authorship_proof"]["public_key_sha256"]
    draft["guardian_id"] = f"guardian_ed25519_{public_key_sha[:16]}"
    draft["guardian_public_key_sha256"] = public_key_sha
    draft["reason"] = "Synthetic no-write retirement preflight; target intentionally nonexistent."
    draft["optional_linked_guardian_application_request"] = {
        "does_participant_request_guardian_application_with_this_record": False
    }
    draft["retirement_does_not_remove_historical_record"] = True
    draft["target_guardian_application_record_id"] = "R-999999999"
    draft["target_guardian_application_record_sha256"] = "a" * 64
    draft["context_readiness"].update(
        {
            "action_profile": "guardian_retirement",
            "declared_context_level": "CC-1",
            "minimum_required_for_action": "CC-1",
            "context_sufficient_for_selected_action": True,
            "context_read_confirmed": False,
            "loaded_context_urls": [
                "https://www.trinityaccord.org/guardian-alliance/",
                "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
            ],
        }
    )
    submission["client_context"]["site_entry_url"] = "https://www.trinityaccord.org/guardian-alliance/"
    submission["client_context"]["declared_context_level"] = "CC-1"
    submission["client_context"]["loaded_context_urls"] = list(
        draft["context_readiness"]["loaded_context_urls"]
    )
    return _refresh_oath_and_signature(submission)


def _post_preflight(base_url: str, submission: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    raw = json.dumps(
        submission,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/record-chain/preflight",
        data=raw,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "TrinityAccordNoWriteLivePreflight/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            body = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read()
    payload = json.loads(body.decode("utf-8"))
    if payload.get("preflight") is not True:
        raise AssertionError(f"response did not identify itself as preflight: {payload}")
    boundary = payload.get("boundary") or {}
    if boundary.get("preflight_is_not_submission") is not True:
        raise AssertionError(f"preflight boundary missing: {payload}")
    forbidden_receipt_keys = {"receipt_id", "receipt", "submitted", "pending_path"}
    leaked = forbidden_receipt_keys.intersection(payload)
    if leaked:
        raise AssertionError(f"preflight response exposed submit-only keys: {sorted(leaked)}")
    return status, payload


def _codes(payload: dict[str, Any]) -> set[str]:
    return {
        str(item.get("code"))
        for item in payload.get("diagnostics", [])
        if isinstance(item, dict) and item.get("code")
    }


def _run_case(
    *,
    name: str,
    base_url: str,
    submission: dict[str, Any],
    accepted: bool | None,
    required_codes: set[str] | None = None,
    forbidden_codes: set[str] | None = None,
) -> dict[str, Any]:
    status, payload = _post_preflight(base_url, submission)
    actual = payload.get("accepted")
    codes = _codes(payload)
    if accepted is not None and actual is not accepted:
        raise AssertionError(
            f"{name}: accepted={actual!r}, expected {accepted!r}; status={status}; codes={sorted(codes)}"
        )
    missing = (required_codes or set()) - codes
    if missing:
        raise AssertionError(f"{name}: missing diagnostics {sorted(missing)}; got {sorted(codes)}")
    unexpected = (forbidden_codes or set()) & codes
    if unexpected:
        raise AssertionError(f"{name}: forbidden diagnostics {sorted(unexpected)}; got {sorted(codes)}")
    result = {
        "name": name,
        "http_status": status,
        "accepted": actual,
        "record_type": payload.get("record_type"),
        "route_detected": payload.get("route_detected"),
        "diagnostic_codes": sorted(codes),
        "preflight_is_not_submission": True,
    }
    print(json.dumps(result, sort_keys=True))
    time.sleep(1.0)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gateway",
        default="https://trinity-record-chain-gateway.onrender.com",
    )
    parser.add_argument("--output")
    args = parser.parse_args()

    echo = _valid_echo()
    verification = _valid_verification()
    guardian_application = _valid_guardian_application()
    retirement = _guardian_retirement_fixture()

    cases = [
        dict(
            name="echo_cc3_accept",
            submission=_set_context(echo, "CC-3", "CC-3"),
            accepted=True,
            forbidden_codes=CONTEXT_CODES,
        ),
        dict(
            name="echo_cc2_reject",
            submission=_set_context(echo, "CC-2", "CC-3"),
            accepted=False,
            required_codes={"INSUFFICIENT_CONTEXT_COMPLETENESS"},
        ),
        dict(
            name="verification_v2_cc3_accept",
            submission=_set_context(verification, "CC-3", "CC-3"),
            accepted=True,
            forbidden_codes=CONTEXT_CODES,
        ),
        dict(
            name="verification_v2_cc2_reject",
            submission=_set_context(verification, "CC-2", "CC-3"),
            accepted=False,
            required_codes={"INSUFFICIENT_CONTEXT_COMPLETENESS"},
        ),
        dict(
            name="guardian_application_cc3_accept",
            submission=_set_context(guardian_application, "CC-3", "CC-3"),
            accepted=True,
            forbidden_codes=CONTEXT_CODES,
        ),
        dict(
            name="guardian_application_cc2_reject",
            submission=_set_context(guardian_application, "CC-2", "CC-3"),
            accepted=False,
            required_codes={"INSUFFICIENT_CONTEXT_COMPLETENESS"},
        ),
        dict(
            name="guardian_retirement_cc1_context_accept",
            submission=_set_context(retirement, "CC-1", "CC-1"),
            accepted=False,
            forbidden_codes=CONTEXT_CODES,
        ),
        dict(
            name="guardian_retirement_cc0_context_reject",
            submission=_set_context(retirement, "CC-0", "CC-1"),
            accepted=False,
            required_codes={"INSUFFICIENT_CONTEXT_COMPLETENESS"},
        ),
    ]

    results = []
    for case in cases:
        results.append(_run_case(base_url=args.gateway, **case))

    report = {
        "schema": "trinityaccord.live-record-action-preflight-report.v1",
        "gateway": args.gateway,
        "request_path": "/record-chain/preflight",
        "submit_endpoint_called": False,
        "ephemeral_test_keys_only": True,
        "cases": results,
    }
    if args.output:
        Path(args.output).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("PASS: live Echo, Verification, Guardian Application, and Guardian Retirement preflight matrix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
