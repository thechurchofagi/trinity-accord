from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder-core.mjs"


def run_node(*args: str, cwd: Path | None = None, timeout: float = 20.0):
    return subprocess.run(
        ["node", str(BUILDER), *args],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def build_notice(tmp_path: Path, *, extra: list[str] | None = None) -> Path:
    out = tmp_path / "notice.json"
    args = [
        "context-insufficient",
        "--actor-label", "豆包外部智能体",
        "--provider", "ByteDance Doubao",
        "--model-runtime", "Doubao test runtime",
        "--participant-identifier", "doubao-audit-agent",
        "--body", "当前上下文不足，暂不提交更强声明。",
        "--discovery-mode", "user_task_context",
        "--requesting-party-type", "human",
        "--introducing-party-type", "human",
        "--record-decision", "mixed",
        "--submission-executor", "self",
        "--human-operator-involved", "false",
        "--loaded-urls", " https://www.trinityaccord.org/agent-start/ ,https://www.trinityaccord.org/agent-start/, https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json ",
        "--gateway", "https://trinity-record-chain-gateway.onrender.com/",
        "--key-dir", str(tmp_path / "keys"),
        "--out", str(out),
    ]
    if extra:
        args.extend(extra)
    result = run_node(*args, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    return out


def test_unicode_identity_urls_gateway_and_mixed_agent_request_are_normalized(tmp_path: Path):
    out = build_notice(tmp_path, extra=["--requesting-party-type", "agent"])
    data = json.loads(out.read_text(encoding="utf-8"))
    identity = data["record_draft"]["submitting_participant_identity"]
    assert identity["participant_public_display_label"] == "豆包外部智能体"
    assert identity["participant_provider_or_platform"] == "ByteDance Doubao"
    assert identity["participant_model_or_runtime"] == "Doubao test runtime"
    urls = data["record_draft"]["context_readiness"]["loaded_context_urls"]
    assert urls == [
        "https://www.trinityaccord.org/agent-start/",
        "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
    ]
    decision = data["record_draft"]["decision_autonomy_context"]
    assert decision["was_record_creation_requested_by_another_agent"] is True
    assert decision["participant_declares_free_choice"] is True
    tooling = data["record_draft"]["submission_execution_context"]["submission_tooling_description"]
    assert tooling["gateway_used"] == "https://trinity-record-chain-gateway.onrender.com"


def test_doctor_cryptographically_rejects_tampered_signed_draft(tmp_path: Path):
    out = build_notice(tmp_path)
    data = json.loads(out.read_text(encoding="utf-8"))
    data["record_draft"]["reason"] = "被签名后篡改的内容"
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    result = run_node("doctor", "--file", str(tampered), cwd=tmp_path)
    assert result.returncode == 1
    assert "AUTHORSHIP_PAYLOAD_SHA_MISMATCH" in result.stdout
    assert "AUTHORSHIP_SIGNATURE_INVALID" in result.stdout


def test_doctor_accepts_valid_signature_and_key_binding(tmp_path: Path):
    out = build_notice(tmp_path)
    result = run_node("doctor", "--file", str(out), cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "AUTHORSHIP_CRYPTOGRAPHIC_VERIFICATION_OK" in result.stdout


def test_repair_refuses_to_mutate_signed_record_draft(tmp_path: Path):
    out = build_notice(tmp_path)
    data = json.loads(out.read_text(encoding="utf-8"))
    data["record_draft"]["context_level"] = "CC-0"
    legacy = tmp_path / "legacy-signed.json"
    repaired = tmp_path / "repaired.json"
    legacy.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    result = run_node("repair", "--file", str(legacy), "--out", str(repaired), cwd=tmp_path)
    assert result.returncode == 1
    assert "SIGNED_DRAFT_REPAIR_REQUIRES_REBUILD" in result.stderr
    assert not repaired.exists()


class _CaptureHandler(BaseHTTPRequestHandler):
    paths: list[str] = []
    delay = 0.0

    def do_POST(self):
        type(self).paths.append(self.path)
        length = int(self.headers.get("content-length", "0"))
        self.rfile.read(length)
        if type(self).delay:
            time.sleep(type(self).delay)
        payload = b'{"accepted":true,"preflight":true}'
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except BrokenPipeError:
            pass

    def log_message(self, *_args):
        return


def _server(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_trailing_gateway_slash_posts_to_single_canonical_path(tmp_path: Path):
    out = build_notice(tmp_path)
    _CaptureHandler.paths = []
    _CaptureHandler.delay = 0.0
    server, thread = _server(_CaptureHandler)
    try:
        result = run_node(
            "preflight", "--file", str(out),
            "--gateway", f"http://127.0.0.1:{server.server_port}/",
            "--request-timeout-ms", "5000",
            cwd=tmp_path,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert _CaptureHandler.paths == ["/record-chain/preflight"]
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_preflight_request_timeout_is_bounded(tmp_path: Path):
    out = build_notice(tmp_path)
    _CaptureHandler.paths = []
    _CaptureHandler.delay = 1.5
    server, thread = _server(_CaptureHandler)
    started = time.monotonic()
    try:
        result = run_node(
            "preflight", "--file", str(out),
            "--gateway", f"http://127.0.0.1:{server.server_port}",
            "--request-timeout-ms", "1000",
            cwd=tmp_path,
            timeout=8,
        )
        elapsed = time.monotonic() - started
        assert result.returncode == 1
        assert "REQUEST_TIMEOUT" in result.stderr
        assert elapsed < 4
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_templates_include_gateway_required_record_specific_blocks(tmp_path: Path):
    for record_type, required in {
        "verification": ["verification_claim_model"],
        "guardian_retirement": ["target_guardian_application_record_id", "target_guardian_application_record_sha256"],
        "correction": ["correction_content"],
    }.items():
        out = tmp_path / f"{record_type}.json"
        result = run_node("template", "--record-type", record_type, "--out", str(out), cwd=tmp_path)
        assert result.returncode == 0, result.stderr
        data = json.loads(out.read_text(encoding="utf-8"))
        text = json.dumps(data)
        for field in required:
            assert field in text


def test_external_agent_builder_v24_is_manifest_bound():
    manifest = json.loads(
        (ROOT / "api" / "record-chain-builder-bundles.v1.json").read_text(encoding="utf-8")
    )["canonical_builder"]["core"]
    core_bytes = BUILDER.read_bytes()
    core_text = core_bytes.decode("utf-8")
    assert 'const BUILDER_VERSION = "v2.4"' in core_text
    assert "minimumContextLevelForAction(opts.recordType)" in core_text
    assert hashlib.sha256(core_bytes).hexdigest() == manifest["sha256"]
    assert len(core_bytes) == manifest["size_bytes"]


def test_error_help_covers_active_external_agent_diagnostics():
    codes = [
        "DUPLICATE_LOADED_CONTEXT_URL",
        "INVALID_LOADED_CONTEXT_URL",
        "PROVENANCE_DECISION_REQUEST_PARTY_MISMATCH",
        "PROVENANCE_REQUEST_FLAG_MISMATCH",
    ]
    helper = json.loads(
        (ROOT / "api" / "record-chain-field-helper.v1.json").read_text(encoding="utf-8")
    )["diagnostic_code_help"]
    assert list(helper) == sorted(helper)
    for code in codes:
        result = run_node("error-help", "--code", code)
        assert result.returncode == 0, result.stdout + result.stderr
        assert f"Error Code: {code}" in result.stdout
        assert "Meaning:" in result.stdout
        assert "Fix:" in result.stdout
        assert "Help URL:" in result.stdout
        assert helper[code]["severity"] == "error"
        assert helper[code]["recovery_possible"] is True
        assert helper[code]["meaning"]
        assert helper[code]["fix"]
