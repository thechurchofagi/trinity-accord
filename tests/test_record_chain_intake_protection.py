from __future__ import annotations

import asyncio
import json
from typing import Any

from apps.record_chain_intake_gateway.protected_app import (
    IntakeProtectionMiddleware,
    cooldown_seconds_for_commit,
    validate_resource_limits,
)


def _submission(record_type: str = "echo", text: str = "concise") -> dict[str, Any]:
    return {
        "record_type": record_type,
        "record_draft": {
            "record_type": record_type,
            "echo_content" if record_type == "echo" else "verification_content": {
                "statement": text,
            },
        },
    }


def _run_asgi(app: Any, body: bytes, headers: list[tuple[bytes, bytes]] | None = None):
    messages = [{"type": "http.request", "body": body, "more_body": False}]
    sent: list[dict[str, Any]] = []

    async def receive():
        if messages:
            return messages.pop(0)
        return {"type": "http.disconnect"}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/record-chain/submit",
        "headers": headers or [],
        "client": ("203.0.113.9", 12345),
    }
    asyncio.run(app(scope, receive, send))
    status = next(message["status"] for message in sent if message["type"] == "http.response.start")
    response_body = b"".join(message.get("body", b"") for message in sent if message["type"] == "http.response.body")
    return status, json.loads(response_body)


def test_cooldown_interval_is_deterministic_and_bounded():
    first = cooldown_seconds_for_commit("a" * 40)
    second = cooldown_seconds_for_commit("a" * 40)
    other = cooldown_seconds_for_commit("b" * 40)
    assert first == second
    assert 3600 <= first <= 7200
    assert 3600 <= other <= 7200
    assert first != other


def test_echo_total_text_limit_is_enforced():
    diagnostics = validate_resource_limits(_submission("echo", "x" * 8001))
    codes = {item["code"] for item in diagnostics}
    assert "RECORD_TEXT_FIELD_TOO_LONG" in codes
    assert "RECORD_TOTAL_TEXT_TOO_LONG" in codes


def test_verification_has_larger_but_bounded_total_limit():
    body = _submission("verification", "x" * 3900)
    body["record_draft"]["verification_content"] = {
        "finding": "a" * 3900,
        "method": "b" * 3900,
        "limitations": "c" * 3900,
    }
    diagnostics = validate_resource_limits(body)
    assert not any(item["code"] == "RECORD_TOTAL_TEXT_TOO_LONG" for item in diagnostics)

    # Add another individually bounded field so only the aggregate 12,000-char
    # verification budget is crossed.
    body["record_draft"]["verification_content"]["additional_context"] = "z" * 400
    diagnostics = validate_resource_limits(body)
    assert any(item["code"] == "RECORD_TOTAL_TEXT_TOO_LONG" for item in diagnostics)


def test_inline_data_and_oversized_reference_lists_are_rejected():
    body = _submission()
    body["record_draft"]["references"] = [
        {"url": f"https://example.invalid/{index}"} for index in range(17)
    ]
    body["record_draft"]["attachment"] = "data:application/octet-stream;base64,AAAA"
    diagnostics = validate_resource_limits(body)
    codes = {item["code"] for item in diagnostics}
    assert "RECORD_ARRAY_TOO_LONG" in codes
    assert "INLINE_DATA_URL_FORBIDDEN" in codes


def test_first_and_second_cooldown_gates_block_before_core_app():
    calls = {"core": 0, "cooldown": 0}

    async def core(scope, receive, send):
        calls["core"] += 1
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"{}"})

    middleware = IntakeProtectionMiddleware(core)

    async def blocked(*, force: bool):
        calls["cooldown"] += 1
        return {"blocked": True}

    middleware._cooldown_state = blocked  # type: ignore[method-assign]
    status, payload = _run_asgi(middleware, json.dumps(_submission()).encode())
    assert status == 429
    assert payload["diagnostic_code"] == "GLOBAL_ACCEPTANCE_COOLDOWN"
    assert calls["core"] == 0
    assert calls["cooldown"] == 1

    calls = {"core": 0, "cooldown": 0}
    middleware = IntakeProtectionMiddleware(core)

    async def open_then_blocked(*, force: bool):
        calls["cooldown"] += 1
        return {"blocked": force}

    middleware._cooldown_state = open_then_blocked  # type: ignore[method-assign]
    status, payload = _run_asgi(middleware, json.dumps(_submission()).encode())
    assert status == 429
    assert payload["diagnostic_code"] == "GLOBAL_ACCEPTANCE_COOLDOWN"
    assert calls["core"] == 0
    assert calls["cooldown"] == 2


def test_repeated_blocked_attempts_escalate_without_accusing_first_request():
    middleware = IntakeProtectionMiddleware(lambda *_args: None)
    first = middleware._cooldown_payload(1)
    repeated = middleware._cooldown_payload(6)

    assert first["diagnostic_code"] == "GLOBAL_ACCEPTANCE_COOLDOWN"
    assert first["requires_human_or_operator_review"] is False
    assert repeated["diagnostic_code"] == "REPEATED_RESOURCE_PRESSURE_WARNING"
    assert repeated["requires_human_or_operator_review"] is True
    assert "may indicate" in repeated["diagnostics"][0]["meaning"]
    assert "civilizational" in repeated["diagnostics"][0]["meaning"]


def test_oversized_content_length_is_rejected_before_body_read():
    calls = {"core": 0, "cooldown": 0}

    async def core(scope, receive, send):
        calls["core"] += 1

    middleware = IntakeProtectionMiddleware(core)

    async def open_state(*, force: bool):
        calls["cooldown"] += 1
        return {"blocked": False}

    middleware._cooldown_state = open_state  # type: ignore[method-assign]
    status, payload = _run_asgi(
        middleware,
        b"{}",
        headers=[(b"content-length", b"98305")],
    )
    assert status == 413
    assert payload["diagnostic_code"] == "REQUEST_BODY_TOO_LARGE"
    assert calls["core"] == 0
    assert calls["cooldown"] == 0
