from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from apps.record_chain_intake_gateway.gateway.canonical import (
    canonical_dumps,
    sha256_canonical_json,
)
from apps.record_chain_intake_gateway.gateway.receipts import (
    compute_receipt_sha256,
    make_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
BUILDER_CORE = ROOT / "downloads" / "record-chain-builder-core.mjs"
CORE_SHA256 = "bfef921cfece2495328b52b9d27306336a60a39a6f3fc3de103a5bba03eb34e6"
CORE_SIZE_BYTES = 206950


def _receipt_fixture(
    submission_sha256: str,
) -> tuple[dict, dict, str, str, str]:
    receipt_id = f"rcg-20260803-{submission_sha256[:24]}"
    receipt_path = (
        "record-chain/intake/receipts/2026/08/"
        f"{receipt_id}.receipt.json"
    )
    submission_path = (
        "record-chain/intake/submissions/2026/08/"
        f"{receipt_id}.submission.json"
    )
    pending_path = f"record-chain/pending/{receipt_id}.verification.pending.json"
    stored_submission = {}
    stored_submission_text = canonical_dumps(stored_submission)
    stored_submission_sha256 = sha256_canonical_json(stored_submission)
    receipt = make_receipt(
        submission=stored_submission,
        submission_sha256=submission_sha256,
        original_submission_sha256=submission_sha256,
        stored_submission_sha256=stored_submission_sha256,
        record_type="verification",
        received_raw_body_sha256="a" * 64,
        intake_submission_path=submission_path,
        pending_file_path=pending_path,
        receipt_path=receipt_path,
        now=datetime(2026, 8, 3, tzinfo=timezone.utc),
        gateway_version="1.2.1-protected",
    )
    index = {
        "schema": "trinityaccord.record-chain-intake-idempotency.v1",
        "submission_sha256": submission_sha256,
        "stored_submission_sha256": stored_submission_sha256,
        "record_type": "verification",
        "receipt_id": receipt_id,
        "receipt_path": receipt_path,
        "intake_submission_path": submission_path,
        "pending_file_path": pending_path,
        "idempotency_written": True,
        "receipt_written": True,
        "pending_written": True,
        "transaction_state": "pending_written",
        "pending_committed_at": "2026-08-03T00:00:00Z",
    }
    return index, receipt, receipt_path, submission_path, stored_submission_text


def _clear_secure_read_state(secure_entrypoint) -> None:
    with secure_entrypoint._read_state_lock:
        secure_entrypoint._read_global_attempts.clear()
        secure_entrypoint._read_attempts_by_client.clear()
        secure_entrypoint._recovery_cache.clear()
        secure_entrypoint._recovery_active = 0


def test_receipt_defaults_to_deployed_runtime_version(monkeypatch):
    from apps.record_chain_intake_gateway.gateway import receipts

    monkeypatch.setattr(
        receipts,
        "get_runtime_info",
        lambda: {"version": "9.9.9-runtime-test"},
    )
    receipt = receipts.make_receipt(
        submission={},
        submission_sha256="b" * 64,
        record_type="verification",
        now=datetime(2026, 8, 3, tzinfo=timezone.utc),
    )
    assert receipt["gateway_version"] == "9.9.9-runtime-test"
    assert receipt["receipt_sha256"] == compute_receipt_sha256(receipt)


def test_gateway_projection_preserves_pre_pending_authorship_fact():
    from apps.record_chain_intake_gateway import secure_entrypoint

    projected = secure_entrypoint._gateway_verified_pending_projection(
        {
            "record_type": "verification",
            "authorship_verification_status": {
                "verified_by_gateway_before_pending": False,
            },
        }
    )
    assert projected["authorship_verification_status"] == {
        "signed_payload_scope": "pre_append_record_draft",
        "verified_by_gateway_before_pending": True,
        "verified_by_append_before_record": False,
        "final_record_contains_append_assigned_fields_not_in_signed_payload": True,
    }


def test_read_only_recovery_verifies_index_receipt_and_stored_submission(monkeypatch):
    from apps.record_chain_intake_gateway import secure_entrypoint

    _clear_secure_read_state(secure_entrypoint)
    submission_sha256 = hashlib.sha256(b"{}").hexdigest()
    index, receipt, receipt_path, submission_path, stored_text = _receipt_fixture(
        submission_sha256
    )
    final_status = {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": index["receipt_id"],
        "pending_file_path": index["pending_file_path"],
        "append_status": "appended",
        "final_record_id": "R-000000109",
    }
    mapping = {
        (
            "record-chain/intake/by-submission-sha256/"
            f"{submission_sha256}.json"
        ): json.dumps(index, separators=(",", ":"), sort_keys=True),
        receipt_path: json.dumps(receipt, separators=(",", ":"), sort_keys=True),
        submission_path: stored_text,
        f"record-chain/receipt-status/{index['receipt_id']}.json": json.dumps(
            final_status,
            separators=(",", ":"),
            sort_keys=True,
        ),
    }

    calls: list[str] = []

    async def fake_get_file_text(path: str):
        calls.append(path)
        return mapping.get(path)

    monkeypatch.setattr(secure_entrypoint, "get_file_text", fake_get_file_text)
    status, payload = asyncio.run(
        secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
            submission_sha256
        )
    )
    assert status == 200
    assert payload["recovery_verified"] is True
    assert payload["receipt_hash_verified"] is True
    assert payload["stored_submission_hash_verified"] is True
    assert payload["idempotency_index_binding_verified"] is True
    assert payload["receipt_id"] == index["receipt_id"]
    assert payload["receipt"]["receipt_sha256"] == receipt["receipt_sha256"]
    assert payload["boundary"]["does_not_retry_submission"] is True
    assert payload["boundary"]["does_not_bypass_cooldown"] is True

    # Positive recovery state is cached, avoiding repeated GitHub API reads.
    first_call_count = len(calls)
    status2, payload2 = asyncio.run(
        secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
            submission_sha256
        )
    )
    assert status2 == 200
    assert payload2["receipt_id"] == index["receipt_id"]
    assert len(calls) == first_call_count


def test_read_only_recovery_fails_closed_on_receipt_hash_mismatch(monkeypatch):
    from apps.record_chain_intake_gateway import secure_entrypoint

    _clear_secure_read_state(secure_entrypoint)
    submission_sha256 = hashlib.sha256(b"{}").hexdigest()
    index, receipt, receipt_path, submission_path, stored_text = _receipt_fixture(
        submission_sha256
    )
    receipt["record_type"] = "echo"
    mapping = {
        (
            "record-chain/intake/by-submission-sha256/"
            f"{submission_sha256}.json"
        ): json.dumps(index),
        receipt_path: json.dumps(receipt),
        submission_path: stored_text,
    }

    async def fake_get_file_text(path: str):
        return mapping.get(path)

    monkeypatch.setattr(secure_entrypoint, "get_file_text", fake_get_file_text)
    status, payload = asyncio.run(
        secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
            submission_sha256
        )
    )
    assert status == 409
    assert payload["recovery_verified"] is False
    assert payload["diagnostic_code"] == "RECOVERY_STATE_INCONSISTENT"


def test_read_only_recovery_detects_stored_submission_tampering(monkeypatch):
    from apps.record_chain_intake_gateway import secure_entrypoint

    _clear_secure_read_state(secure_entrypoint)
    submission_sha256 = hashlib.sha256(b"{}").hexdigest()
    index, receipt, receipt_path, submission_path, _ = _receipt_fixture(
        submission_sha256
    )
    mapping = {
        (
            "record-chain/intake/by-submission-sha256/"
            f"{submission_sha256}.json"
        ): json.dumps(index),
        receipt_path: json.dumps(receipt),
        submission_path: '{"tampered":true}',
    }

    async def fake_get_file_text(path: str):
        return mapping.get(path)

    monkeypatch.setattr(secure_entrypoint, "get_file_text", fake_get_file_text)
    status, payload = asyncio.run(
        secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
            submission_sha256
        )
    )
    assert status == 409
    assert payload["diagnostic_code"] == "RECOVERY_STATE_INCONSISTENT"
    assert "stored submission" in payload["message"]


def test_read_only_recovery_reports_backend_outage_as_503(monkeypatch):
    from apps.record_chain_intake_gateway import secure_entrypoint

    _clear_secure_read_state(secure_entrypoint)
    submission_sha256 = hashlib.sha256(b"{}").hexdigest()
    index, _, _, _, _ = _receipt_fixture(submission_sha256)
    index_path = (
        "record-chain/intake/by-submission-sha256/"
        f"{submission_sha256}.json"
    )

    async def fake_get_file_text(path: str):
        if path == index_path:
            return json.dumps(index)
        raise RuntimeError("temporary GitHub read failure")

    monkeypatch.setattr(secure_entrypoint, "get_file_text", fake_get_file_text)
    try:
        asyncio.run(
            secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
                submission_sha256
            )
        )
    except secure_entrypoint.RecoveryBackendUnavailable as exc:
        assert "receipt could not be read" in str(exc)
    else:
        raise AssertionError("backend outage must remain distinct from immutable corruption")


def test_read_only_recovery_returns_404_without_idempotency_index(monkeypatch):
    from apps.record_chain_intake_gateway import secure_entrypoint

    _clear_secure_read_state(secure_entrypoint)

    async def fake_get_file_text(path: str):
        return None

    monkeypatch.setattr(secure_entrypoint, "get_file_text", fake_get_file_text)
    status, payload = asyncio.run(
        secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
            "c" * 64
        )
    )
    assert status == 404
    assert payload["diagnostic_code"] == "SUBMISSION_NOT_MATERIALIZED"


def test_protected_receipt_route_passes_verified_envelope_bindings(monkeypatch):
    from apps.record_chain_intake_gateway import secure_entrypoint

    _clear_secure_read_state(secure_entrypoint)
    submission_sha256 = hashlib.sha256(b"{}").hexdigest()
    _, receipt, receipt_path, submission_path, stored_text = _receipt_fixture(
        submission_sha256
    )
    mapping = {
        receipt_path: json.dumps(receipt, separators=(",", ":"), sort_keys=True),
        submission_path: stored_text,
    }

    async def fake_get_file_text(path: str):
        return mapping.get(path)

    monkeypatch.setattr(secure_entrypoint, "get_file_text", fake_get_file_text)
    monkeypatch.setattr(
        secure_entrypoint.core_gateway,
        "get_file_text",
        fake_get_file_text,
    )
    status, payload = asyncio.run(
        secure_entrypoint.ProtectedProductionApp._receipt_payload(
            receipt["server_receipt_id"]
        )
    )
    assert status == 200
    assert payload["found"] is True
    assert payload["receipt_hash_verified"] is True
    assert payload["receipt_url_binding_verified"] is True
    assert payload["stored_submission_hash_verified"] is True
    assert payload["receipt"]["server_receipt_id"] == receipt["server_receipt_id"]


def test_receipt_route_rejects_valid_hash_at_wrong_url(monkeypatch):
    from apps.record_chain_intake_gateway import secure_entrypoint

    _clear_secure_read_state(secure_entrypoint)
    requested_sha = hashlib.sha256(b"{}").hexdigest()
    _, requested_receipt, requested_path, _, _ = _receipt_fixture(requested_sha)
    wrong_sha = hashlib.sha256(b'{"wrong":true}').hexdigest()
    _, wrong_receipt, _, _, _ = _receipt_fixture(wrong_sha)
    # Place a self-hash-valid but differently identified receipt at requested_path.
    wrong_receipt["receipt_path"] = requested_path
    wrong_receipt["receipt_sha256"] = compute_receipt_sha256(wrong_receipt)

    async def fake_get_file_text(path: str):
        if path == requested_path:
            return json.dumps(wrong_receipt)
        return None

    monkeypatch.setattr(secure_entrypoint, "get_file_text", fake_get_file_text)
    status, payload = asyncio.run(
        secure_entrypoint.ProtectedProductionApp._receipt_payload(
            requested_receipt["server_receipt_id"]
        )
    )
    assert status == 409
    assert payload["diagnostic_code"] == "RECEIPT_STATE_INCONSISTENT"


def test_read_route_limiter_is_bounded_and_enforced(monkeypatch):
    from apps.record_chain_intake_gateway import secure_entrypoint

    _clear_secure_read_state(secure_entrypoint)
    monkeypatch.setattr(secure_entrypoint, "_READ_GLOBAL_LIMIT_PER_MINUTE", 2)
    monkeypatch.setattr(secure_entrypoint, "_READ_CLIENT_LIMIT_PER_MINUTE", 1)
    monkeypatch.setattr(secure_entrypoint, "_READ_MAX_TRACKED_CLIENTS", 3)

    allowed, retry_after = secure_entrypoint._allow_read_route("client-a")
    assert allowed is True
    assert retry_after == 0
    allowed, retry_after = secure_entrypoint._allow_read_route("client-a")
    assert allowed is False
    assert retry_after >= 1

    for index in range(10):
        secure_entrypoint._allow_read_route(f"client-{index}")
    with secure_entrypoint._read_state_lock:
        assert len(secure_entrypoint._read_attempts_by_client) <= 3


def test_builder_core_is_preserved_byte_for_byte():
    core = BUILDER_CORE.read_bytes()
    assert len(core) == CORE_SIZE_BYTES
    assert hashlib.sha256(core).hexdigest() == CORE_SHA256


class _RecoveryServerState:
    def __init__(self, *, submit_status: int, recovery_mode: str):
        self.submit_status = submit_status
        self.recovery_mode = recovery_mode
        self.posts = 0
        self.gets = 0
        self.submission_sha256 = hashlib.sha256(b"{}").hexdigest()
        self.index, self.receipt, _, _, _ = _receipt_fixture(
            self.submission_sha256
        )


def _start_recovery_server(state: _RecoveryServerState):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def _write(self, status: int, payload, content_type: str = "application/json"):
            raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", content_type)
            self.send_header("content-length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            state.posts += 1
            if state.submit_status == 502:
                self._write(502, b"<html>bad gateway</html>", "text/html")
            else:
                self._write(
                    state.submit_status,
                    {"accepted": False, "submitted": False},
                )

        def do_GET(self):
            state.gets += 1
            if state.recovery_mode == "missing":
                self._write(404, {"found": False})
                return
            if state.recovery_mode == "rate_limited":
                self._write(429, {"found": False})
                return
            receipt = dict(state.receipt)
            if state.recovery_mode == "bad_hash":
                receipt["record_type"] = "echo"
            self._write(
                200,
                {
                    "found": True,
                    "recovery_verified": True,
                    "receipt_hash_verified": True,
                    "stored_submission_hash_verified": True,
                    "idempotency_index_binding_verified": True,
                    "submission_sha256": state.submission_sha256,
                    "receipt_id": state.index["receipt_id"],
                    "record_type": "verification",
                    "receipt": receipt,
                    "final_status": {"append_status": "appended"},
                },
            )

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _run_builder(
    tmp_path: Path,
    state: _RecoveryServerState,
    *,
    recovery_attempts: int = 1,
):
    if shutil.which("node") is None:
        pytest.skip("node is not available")
    submission = tmp_path / "submission.json"
    submission.write_text("{}", encoding="utf-8")
    server, thread = _start_recovery_server(state)
    env = os.environ.copy()
    env["TRINITY_SUBMIT_RECOVERY_ATTEMPTS"] = str(recovery_attempts)
    env["TRINITY_SUBMIT_RECOVERY_DELAY_MS"] = "0"
    env["TRINITY_SUBMIT_RECOVERY_FETCH_TIMEOUT_MS"] = "1000"
    try:
        result = subprocess.run(
            [
                "node",
                str(BUILDER),
                "submit",
                "--file",
                str(submission),
                "--gateway",
                f"http://127.0.0.1:{server.server_port}",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    return result


def test_builder_recovers_502_with_one_post_and_verified_read(tmp_path):
    state = _RecoveryServerState(submit_status=502, recovery_mode="valid")
    result = _run_builder(tmp_path, state)
    assert result.returncode == 0, result.stdout + result.stderr
    assert state.posts == 1
    assert state.gets == 1
    assert "recovered_after_ambiguous_submit" in result.stdout
    assert "recovery_was_read_only" in result.stdout


def test_builder_429_uses_one_recovery_probe_not_poll_amplification(tmp_path):
    state = _RecoveryServerState(submit_status=429, recovery_mode="missing")
    result = _run_builder(tmp_path, state, recovery_attempts=12)
    assert result.returncode == 1
    assert state.posts == 1
    assert state.gets == 1


def test_builder_stops_when_recovery_route_is_rate_limited(tmp_path):
    state = _RecoveryServerState(submit_status=502, recovery_mode="rate_limited")
    result = _run_builder(tmp_path, state, recovery_attempts=12)
    assert result.returncode == 1
    assert state.posts == 1
    assert state.gets == 1


def test_builder_does_not_retry_or_recover_nonambiguous_400(tmp_path):
    state = _RecoveryServerState(submit_status=400, recovery_mode="valid")
    result = _run_builder(tmp_path, state)
    assert result.returncode == 1
    assert state.posts == 1
    assert state.gets == 0


def test_builder_rejects_unverified_recovery_receipt(tmp_path):
    state = _RecoveryServerState(submit_status=502, recovery_mode="bad_hash")
    result = _run_builder(tmp_path, state)
    assert result.returncode == 1
    assert state.posts == 1
    assert state.gets == 1
