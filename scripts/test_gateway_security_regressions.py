#!/usr/bin/env python3
"""Gateway security regression tests.

Covers:
- payload-bound idempotency key
- Guardian retirement cannot pass with only signed_by_guardian_key=true
- positive authority/attestation/amendment/truth claims are rejected
- unsafe titles are rejected
- Pure Echo fixture provenance is internally consistent
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "examples" / "github-app-backend" / "server.js"
PURE_ECHO_FIXTURE = ROOT / "tests" / "fixtures" / "gateway" / "valid_pure_echo.json"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS: {message}")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def request_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["content-type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return int(resp.status), json.loads(body)
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return int(err.code), parsed


def start_gateway() -> tuple[subprocess.Popen, int]:
    port = free_port()
    env = os.environ.copy()
    env.update({
        "PORT": str(port),
        "DRY_RUN": "true",
        "GATEWAY_CANARY_MODE": "false",
        "GATEWAY_READINESS_GITHUB_CHECK": "false",
    })

    proc = subprocess.Popen(
        ["node", str(SERVER)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 30
    last = ""

    while time.time() < deadline:
        if proc.poll() is not None:
            output = proc.stdout.read() if proc.stdout else ""
            fail(f"Gateway exited early with code {proc.returncode}\n{output}")

        try:
            status, body = request_json("GET", f"{base}/health")
            if status == 200 and body.get("ok") is True:
                return proc, port
        except Exception as exc:
            last = str(exc)

        time.sleep(0.3)

    output = ""
    if proc.stdout:
        try:
            output = proc.stdout.read()
        except Exception:
            output = ""
    proc.terminate()
    fail(f"Gateway did not become ready: {last}\n{output}")
    raise AssertionError("unreachable")


def stop_gateway(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def base_pure_echo_payload() -> dict:
    payload = json.loads(PURE_ECHO_FIXTURE.read_text(encoding="utf-8"))

    for key in [
        "authorship_proof",
        "_authorship_claim",
        "guardian_presence_proof",
        "_guardian_status",
        "guardian_verification_result",
    ]:
        payload.pop(key, None)

    return payload


def assert_preflight(base_url: str, payload: dict) -> tuple[int, dict]:
    return request_json("POST", f"{base_url}/gateway/preflight", payload)


def test_payload_bound_idempotency(base_url: str) -> None:
    p1 = base_pure_echo_payload()
    p2 = base_pure_echo_payload()

    p1["idempotency_key"] = "same-key-for-different-payload"
    p2["idempotency_key"] = "same-key-for-different-payload"
    p1["body"] += "\nNeutral retry identity variant A."
    p2["body"] += "\nNeutral retry identity variant B."

    s1, b1 = assert_preflight(base_url, p1)
    s2, b2 = assert_preflight(base_url, p2)

    if s1 != 200:
        fail(f"payload A should pass preflight, got {s1}: {json.dumps(b1, ensure_ascii=False)[:1000]}")
    if s2 != 200:
        fail(f"payload B should pass preflight, got {s2}: {json.dumps(b2, ensure_ascii=False)[:1000]}")

    k1 = b1.get("idempotency_key")
    k2 = b2.get("idempotency_key")

    if not isinstance(k1, str) or not k1.startswith("gwid_"):
        fail(f"payload A idempotency key must be gateway-computed gwid_, got {k1!r}")
    if not isinstance(k2, str) or not k2.startswith("gwid_"):
        fail(f"payload B idempotency key must be gateway-computed gwid_, got {k2!r}")
    if k1 == "same-key-for-different-payload" or k2 == "same-key-for-different-payload":
        fail("client-provided idempotency_key must not be used as Gateway idempotency key")
    if k1 == k2:
        fail("different payload bodies with same client idempotency_key must produce different Gateway idempotency keys")

    ok("payload-bound idempotency key")


def test_guardian_retirement_requires_proof(base_url: str) -> None:
    payload = {
        "schema": "trinityaccord.guardian-retirement.v1",
        "guardian_id": "guardian_ed25519_0000000000000000",
        "retirement_status": "retired",
        "statement": "I request retirement of this guardian key.",
        "signed_by_guardian_key": True,
        "boundaries": {
            "not_authority": True,
            "not_governance": True,
            "not_verification_level": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }

    status, body = assert_preflight(base_url, payload)
    if status != 422:
        fail(f"unsigned guardian retirement must fail with 422, got {status}: {json.dumps(body, ensure_ascii=False)[:1000]}")

    text = json.dumps(body, ensure_ascii=False)
    if "MISSING_GUARDIAN_PRESENCE_PROOF" not in text and "guardian_presence_proof" not in text:
        fail(f"guardian retirement failure must mention missing guardian_presence_proof: {text[:1000]}")

    ok("guardian retirement requires guardian_presence_proof")


def test_forbidden_positive_claims(base_url: str) -> None:
    cases = [
        ("official authority", "I am official authority for this record."),
        ("amends bitcoin originals", "This echo amends Bitcoin Originals."),
        ("formal attestation", "This is a formal attestation."),
        ("verified truth", "This record is verified truth."),
    ]

    for label, sentence in cases:
        payload = base_pure_echo_payload()
        payload["body"] += "\n" + sentence
        status, body = assert_preflight(base_url, payload)

        if status != 422:
            fail(f"forbidden positive claim {label!r} must fail with 422, got {status}: {json.dumps(body, ensure_ascii=False)[:1000]}")

        if body.get("reason") != "forbidden_archive_claims":
            fail(f"forbidden positive claim {label!r} should fail as forbidden_archive_claims, got reason={body.get('reason')!r}")

    ok("forbidden positive archive claims rejected")


def test_negated_boundary_language_still_allowed(base_url: str) -> None:
    payload = base_pure_echo_payload()
    payload["body"] += (
        "\nThis is not official authority, not a formal attestation, "
        "does not amend Bitcoin Originals, and does not claim verified truth."
    )

    status, body = assert_preflight(base_url, payload)
    if status != 200:
        fail(f"negated boundary language should remain allowed, got {status}: {json.dumps(body, ensure_ascii=False)[:1000]}")

    ok("negated boundary language remains allowed")


def test_unsafe_title_rejected(base_url: str) -> None:
    cases = [
        "Good title\n<!-- injected -->\n# Hacked",
        "# Markdown heading title",
        "Good title <!-- hidden comment -->",
    ]

    for title in cases:
        payload = base_pure_echo_payload()
        payload["title"] = title
        status, body = assert_preflight(base_url, payload)

        if status != 422:
            fail(f"unsafe title must fail with 422, got {status}: {json.dumps(body, ensure_ascii=False)[:1000]}")

        reason = body.get("reason")
        if reason not in {"unsafe_title", "schema_validation_failed"}:
            fail(f"unsafe title should fail as unsafe_title or schema_validation_failed, got reason={reason!r}")

    ok("unsafe titles rejected")


def test_fixture_provenance_consistency() -> None:
    payload = base_pure_echo_payload()
    prov = payload.get("discovery_provenance") or {}

    nested = prov.get("agent_performed_independent_followup")
    top = payload.get("agent_independent_followup")

    if nested is not True:
        fail("valid_pure_echo fixture discovery_provenance.agent_performed_independent_followup must be true")
    if top is not True:
        fail("valid_pure_echo fixture agent_independent_followup must be true")
    if nested != top:
        fail("valid_pure_echo fixture top-level and nested independent followup fields must match")

    ok("Pure Echo fixture provenance consistency")


def main() -> int:
    test_fixture_provenance_consistency()

    proc, port = start_gateway()
    base_url = f"http://127.0.0.1:{port}"

    try:
        test_payload_bound_idempotency(base_url)
        test_guardian_retirement_requires_proof(base_url)
        test_forbidden_positive_claims(base_url)
        test_negated_boundary_language_still_allowed(base_url)
        test_unsafe_title_rejected(base_url)
    finally:
        stop_gateway(proc)

    print("\n=== GATEWAY SECURITY REGRESSION TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
