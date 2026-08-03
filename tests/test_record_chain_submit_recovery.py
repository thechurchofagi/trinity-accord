from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import AsyncMock

from starlette.requests import Request

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"


def _request(payload: dict) -> Request:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    delivered = False

    async def receive():
        nonlocal delivered
        if not delivered:
            delivered = True
            return {"type": "http.request", "body": raw, "more_body": False}
        return {"type": "http.disconnect"}

    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/record-chain/submit",
            "headers": [(b"content-type", b"application/json")],
            "client": ("127.0.0.1", 12345),
        },
        receive,
    )


def test_gateway_receipt_version_and_authorship_stage_are_persisted(monkeypatch):
    from apps.record_chain_intake_gateway import app as gateway

    body = {
        "record_type": "verification",
        "record_draft": {"record_type": "verification"},
        "authorship_proof": {"schema": "test-proof"},
    }
    receipt_kwargs = {}
    atomic_files = {}

    monkeypatch.setattr(gateway, "_protection_layer_ready", lambda: True)
    monkeypatch.setattr(gateway, "_check_config", lambda: None)
    monkeypatch.setattr(gateway, "validate_submission", lambda value: [])
    monkeypatch.setattr(gateway, "detect_route", lambda value: "verification")
    monkeypatch.setattr(gateway, "check_rate_limit", lambda value: None)
    monkeypatch.setattr(gateway, "redact_transient_oath_readback", lambda value: value)
    monkeypatch.setattr(gateway, "extract_guardian_application_identity", lambda value: None)
    monkeypatch.setattr(gateway, "_has_linked_guardian_request", lambda value: False)
    monkeypatch.setattr(gateway, "_WRITE_MODE", "github_contents_pending")
    monkeypatch.setattr(gateway, "_DISPATCH_APPEND_WORKFLOW", True)
    monkeypatch.setattr(gateway, "_cache_receipt", lambda *args, **kwargs: None)
    monkeypatch.setattr(gateway, "get_runtime_info", lambda: {"version": "9.9.9-test"})

    async def none_index(*args, **kwargs):
        return None

    async def no_diagnostics(*args, **kwargs):
        return []

    async def no_file(*args, **kwargs):
        return None

    async def capture_atomic(files, message):
        atomic_files.update(files)
        return {"commit": {"sha": "a" * 40}}

    async def no_dispatch(*args, **kwargs):
        return None

    monkeypatch.setattr(gateway, "_read_idempotency_index", none_index)
    monkeypatch.setattr(gateway, "_guardian_retirement_target_diagnostics", no_diagnostics)
    monkeypatch.setattr(gateway, "_record_target_diagnostics", no_diagnostics)
    monkeypatch.setattr(gateway, "_guardian_application_uniqueness_diagnostics", no_diagnostics)
    monkeypatch.setattr(gateway, "_find_existing_matching_receipt", none_index)
    monkeypatch.setattr(gateway, "get_file_sha", no_file)
    monkeypatch.setattr(gateway, "create_files_atomic", capture_atomic)
    monkeypatch.setattr(gateway, "dispatch_workflow", no_dispatch)

    def fake_receipt(**kwargs):
        receipt_kwargs.update(kwargs)
        receipt_id = gateway.make_receipt_id(kwargs["submission_sha256"], kwargs["now"])
        accepted_at = kwargs["now"].isoformat().replace("+00:00", "Z")
        return {
            "server_receipt_id": receipt_id,
            "service": "record-chain-intake-gateway",
            "gateway_version": kwargs["gateway_version"],
            "record_type": kwargs["record_type"],
            "submission_sha256": kwargs["submission_sha256"],
            "original_submission_sha256": kwargs["original_submission_sha256"],
            "stored_submission_sha256": kwargs["stored_submission_sha256"],
            "received_raw_body_sha256": kwargs["received_raw_body_sha256"],
            "accepted_at": accepted_at,
            "intake_submission_path": kwargs["intake_submission_path"],
            "pending_file_path": kwargs["pending_file_path"],
            "receipt_path": kwargs["receipt_path"],
            "raw_readback_redacted": True,
            "receipt_is_not_final_chain_record": True,
            "receipt_sha256": "0" * 64,
        }

    monkeypatch.setattr(gateway, "make_receipt", fake_receipt)

    response = asyncio.run(gateway.submit(_request(body)))
    assert response.accepted is True
    assert receipt_kwargs["gateway_version"] == "9.9.9-test"

    pending_paths = [path for path in atomic_files if path.endswith(".pending.json")]
    assert len(pending_paths) == 1
    pending = json.loads(atomic_files[pending_paths[0]])
    assert pending["authorship_verification_status"] == {
        "signed_payload_scope": "pre_append_record_draft",
        "verified_by_gateway_before_pending": True,
        "verified_by_append_before_record": False,
        "final_record_contains_append_assigned_fields_not_in_signed_payload": True,
    }
    assert pending["authorship_proof"] == body["authorship_proof"]


def _run_middleware(monkeypatch, *, materialized: bool):
    from apps.record_chain_intake_gateway import protected_app

    app_called = []
    sent = []

    async def downstream(scope, receive, send):
        app_called.append(True)
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"{}", "more_body": False})

    middleware = protected_app.IntakeProtectionMiddleware(downstream)
    monkeypatch.setattr(
        middleware,
        "_materialized_exact_retry",
        AsyncMock(return_value=materialized),
    )
    reject = AsyncMock(return_value=True)
    monkeypatch.setattr(middleware, "_reject_if_blocked", reject)

    body = b"{}"
    delivered = False

    async def receive():
        nonlocal delivered
        if not delivered:
            delivered = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/record-chain/submit",
        "headers": [
            (b"content-type", b"application/json"),
            (b"x-trinity-exact-retry", b"1"),
        ],
        "client": ("127.0.0.1", 12345),
    }
    asyncio.run(middleware(scope, receive, send))
    return app_called, reject, sent


def test_materialized_exact_retry_bypasses_cooldown(monkeypatch):
    app_called, reject, _ = _run_middleware(monkeypatch, materialized=True)
    assert app_called == [True]
    reject.assert_not_awaited()


def test_unmaterialized_retry_header_does_not_bypass_cooldown(monkeypatch):
    app_called, reject, _ = _run_middleware(monkeypatch, materialized=False)
    assert app_called == []
    reject.assert_awaited_once()


class _ServerState:
    def __init__(self, *, receipt_visible: bool, second_submit_success: bool):
        self.receipt_visible = receipt_visible
        self.second_submit_success = second_submit_success
        self.posts = 0
        self.gets = 0
        self.retry_header = None
        self.submission_sha256 = hashlib.sha256(b"{}").hexdigest()


def _builder_server(state: _ServerState):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def _write(self, status: int, payload, content_type="application/json"):
            raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", content_type)
            self.send_header("content-length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            state.gets += 1
            receipt_id = self.path.rsplit("/", 1)[-1]
            if state.receipt_visible:
                self._write(200, {
                    "found": True,
                    "receipt_id": receipt_id,
                    "receipt": {
                        "server_receipt_id": receipt_id,
                        "submission_sha256": state.submission_sha256,
                        "record_type": "verification",
                    },
                    "final_status": {"append_status": "appended"},
                })
            else:
                self._write(404, {"found": False})

        def do_POST(self):
            state.posts += 1
            if state.posts == 1:
                self._write(502, b"<html>bad gateway</html>", "text/html")
                return
            state.retry_header = self.headers.get("X-Trinity-Exact-Retry")
            if state.second_submit_success:
                self._write(200, {
                    "accepted": True,
                    "submitted": True,
                    "duplicate": True,
                    "receipt_id": "rcg-20260803-" + state.submission_sha256[:24],
                    "submission_sha256": state.submission_sha256,
                })
            else:
                self._write(503, {"accepted": False, "submitted": False})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _run_builder(tmp_path: Path, state: _ServerState):
    server, thread = _builder_server(state)
    submission = tmp_path / "submission.json"
    submission.write_text("{}", encoding="utf-8")
    env = os.environ.copy()
    env["TRINITY_SUBMIT_AMBIGUOUS_RETRY_DELAY_MS"] = "0"
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
            timeout=20,
            check=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    return result


def test_builder_recovers_visible_receipt_without_second_submit(tmp_path):
    state = _ServerState(receipt_visible=True, second_submit_success=False)
    result = _run_builder(tmp_path, state)
    assert result.returncode == 0, result.stdout + result.stderr
    assert state.posts == 1
    assert state.gets >= 1
    assert "recovered_after_ambiguous_submit" in result.stdout


def test_builder_marks_only_one_exact_recovery_retry(tmp_path):
    state = _ServerState(receipt_visible=False, second_submit_success=True)
    result = _run_builder(tmp_path, state)
    assert result.returncode == 0, result.stdout + result.stderr
    assert state.posts == 2
    assert state.retry_header == "1"


def test_builder_does_not_retry_non_ambiguous_client_error(tmp_path):
    class Handler(BaseHTTPRequestHandler):
        posts = 0

        def log_message(self, fmt, *args):
            return

        def do_POST(self):
            type(self).posts += 1
            raw = b'{"accepted":false,"submitted":false}'
            self.send_response(400)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    submission = tmp_path / "submission.json"
    submission.write_text("{}", encoding="utf-8")
    try:
        result = subprocess.run(
            ["node", str(BUILDER), "submit", "--file", str(submission), "--gateway", f"http://127.0.0.1:{server.server_port}"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert result.returncode == 1
    assert Handler.posts == 1
