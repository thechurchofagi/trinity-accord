#!/usr/bin/env python3
"""Apply the reviewed deep-audit production protection patch exactly once."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one exact patch target, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return value


def write_json(path: str, value: dict) -> None:
    (ROOT / path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def patch_app() -> None:
    path = "apps/record_chain_intake_gateway/app.py"
    replace_once(path, '    version="1.0.0",\n', '    version="1.1.0",\n')

    replace_once(
        path,
        '''def _check_config() -> None:\n    """Ensure required env vars are set."""\n    missing = []\n    required = ["TRINITY_REPO_FULL_NAME", "TRINITY_TARGET_BRANCH"]\n    if _WRITE_MODE == "github_contents_pending":\n        required.append("TRINITY_GITHUB_TOKEN")\n    for var in required:\n        if not os.environ.get(var):\n            missing.append(var)\n    if missing:\n        raise HTTPException(status_code=503, detail=f"Missing required config: {', '.join(missing)}")\n\n\n''',
        '''def _protection_layer_required() -> bool:\n    """Return whether this runtime must reject an unwrapped core application."""\n    return os.environ.get("TRINITY_ENFORCE_PROTECTION_LAYER", "").strip().lower() in {\n        "1", "true", "yes", "on"\n    }\n\n\ndef _protection_layer_ready() -> bool:\n    info = get_runtime_info()\n    return bool(not _protection_layer_required() or info["protection_layer_active"])\n\n\ndef _protection_unavailable_payload(*, preflight: bool) -> dict[str, Any]:\n    payload: dict[str, Any] = {\n        "accepted": False,\n        "submitted": False,\n        "preflight": preflight,\n        "diagnostic_code": "PROTECTION_LAYER_INACTIVE",\n        "diagnostics": [{\n            "code": "PROTECTION_LAYER_INACTIVE",\n            "severity": "error",\n            "field": None,\n            "message": "The production protection layer is required but is not active.",\n            "meaning": (\n                "The core Gateway refuses public validation and persistence when the "\n                "secure ASGI wrapper has not been loaded."\n            ),\n            "suggested_fix": "Retry later after the protected production entrypoint is restored.",\n            "retry_allowed": True,\n        }],\n        "boundary": {\n            "not_authority": True,\n            "not_attestation": True,\n            "not_amendment": True,\n        },\n        "gateway_runtime": _build_gateway_runtime(),\n        "gateway_schema": _GATEWAY_SCHEMA,\n    }\n    return payload\n\n\ndef _check_config() -> None:\n    """Ensure required env vars and the production wrapper are active."""\n    if not _protection_layer_ready():\n        raise HTTPException(\n            status_code=503,\n            detail={\n                "code": "PROTECTION_LAYER_INACTIVE",\n                "message": (\n                    "The production protection layer is required but is not active; "\n                    "refusing a public write."\n                ),\n            },\n        )\n\n    missing = []\n    required = ["TRINITY_REPO_FULL_NAME", "TRINITY_TARGET_BRANCH"]\n    if _WRITE_MODE == "github_contents_pending":\n        required.append("TRINITY_GITHUB_TOKEN")\n    for var in required:\n        if not os.environ.get(var):\n            missing.append(var)\n    if missing:\n        raise HTTPException(status_code=503, detail=f"Missing required config: {', '.join(missing)}")\n\n\n''',
    )

    replace_once(
        path,
        '        "protection_layer_active": info["protection_layer_active"],\n        "protection_entrypoint": info["protection_entrypoint"],\n',
        '        "protection_layer_active": info["protection_layer_active"],\n        "protection_required": _protection_layer_required(),\n        "protection_entrypoint": info["protection_entrypoint"],\n',
    )

    replace_once(
        path,
        '''@app.get("/healthz")\nasync def healthz() -> dict[str, Any]:\n    return {"ok": True, "service": "record-chain-intake-gateway"}\n\n\n@app.head("/healthz")\nasync def healthz_head() -> Response:\n    return Response(status_code=200)\n\n\n@app.get("/record-chain/readiness", response_model=ReadinessResponse)\nasync def readiness(response: Response) -> ReadinessResponse:\n    info = get_runtime_info()\n\n    repo_configured = bool(os.environ.get("TRINITY_REPO_FULL_NAME"))\n    branch_configured = bool(os.environ.get("TRINITY_TARGET_BRANCH"))\n    token_configured = bool(os.environ.get("TRINITY_GITHUB_TOKEN"))\n\n    write_requires_github = info["write_mode"] == "github_contents_pending"\n    submit_ready = (\n        repo_configured\n        and branch_configured\n        and (token_configured if write_requires_github else True)\n    )\n\n    if not submit_ready:\n        response.status_code = 503\n\n    return ReadinessResponse(\n        ok=submit_ready,\n        preflight_ready=True,\n        submit_ready=submit_ready,\n        service=info["service"],\n        version=info["version"],\n        repo_configured=repo_configured,\n        branch_configured=branch_configured,\n        token_configured=token_configured,\n        write_mode=info["write_mode"],\n        max_submission_bytes=info["max_submission_bytes"],\n        record_draft_max_bytes=info["record_draft_max_bytes"],\n        max_text_field_chars=info["max_text_field_chars"],\n        protection_layer_active=info["protection_layer_active"],\n        protection_entrypoint=info["protection_entrypoint"],\n        global_acceptance_cooldown_seconds=info["global_acceptance_cooldown_seconds"],\n        oath_gate_mode=os.environ.get("TRINITY_OATH_GATE_MODE", "required"),\n    )\n''',
        '''@app.get("/healthz")\nasync def healthz(response: Response) -> dict[str, Any]:\n    info = get_runtime_info()\n    ready = _protection_layer_ready()\n    if not ready:\n        response.status_code = 503\n    return {\n        "ok": ready,\n        "service": info["service"],\n        "version": info["version"],\n        "protection_required": _protection_layer_required(),\n        "protection_layer_active": info["protection_layer_active"],\n        "protection_entrypoint": info["protection_entrypoint"],\n    }\n\n\n@app.head("/healthz")\nasync def healthz_head() -> Response:\n    return Response(status_code=200 if _protection_layer_ready() else 503)\n\n\n@app.get("/record-chain/readiness", response_model=ReadinessResponse)\nasync def readiness(response: Response) -> ReadinessResponse:\n    info = get_runtime_info()\n\n    repo_configured = bool(os.environ.get("TRINITY_REPO_FULL_NAME"))\n    branch_configured = bool(os.environ.get("TRINITY_TARGET_BRANCH"))\n    token_configured = bool(os.environ.get("TRINITY_GITHUB_TOKEN"))\n    cooldown_secret_configured = bool(\n        os.environ.get("TRINITY_COOLDOWN_SECRET", "").strip()\n        or os.environ.get("TRINITY_GITHUB_TOKEN", "").strip()\n    )\n    protection_required = _protection_layer_required()\n    protection_ready = _protection_layer_ready()\n\n    write_requires_github = info["write_mode"] == "github_contents_pending"\n    submit_ready = bool(\n        protection_ready\n        and repo_configured\n        and branch_configured\n        and (token_configured if write_requires_github else True)\n        and (cooldown_secret_configured if protection_required else True)\n    )\n\n    if not submit_ready:\n        response.status_code = 503\n\n    return ReadinessResponse(\n        ok=submit_ready,\n        preflight_ready=protection_ready,\n        submit_ready=submit_ready,\n        service=info["service"],\n        version=info["version"],\n        repo_configured=repo_configured,\n        branch_configured=branch_configured,\n        token_configured=token_configured,\n        cooldown_secret_configured=cooldown_secret_configured,\n        write_mode=info["write_mode"],\n        max_submission_bytes=info["max_submission_bytes"],\n        record_draft_max_bytes=info["record_draft_max_bytes"],\n        max_text_field_chars=info["max_text_field_chars"],\n        protection_required=protection_required,\n        protection_layer_active=info["protection_layer_active"],\n        protection_entrypoint=info["protection_entrypoint"],\n        global_acceptance_cooldown_seconds=info["global_acceptance_cooldown_seconds"],\n        oath_gate_mode=os.environ.get("TRINITY_OATH_GATE_MODE", "required"),\n    )\n''',
    )

    replace_once(
        path,
        '''async def preflight(request: Request) -> PreflightResponse | JSONResponse:\n    client_key = request.client.host if request.client else "unknown"\n''',
        '''async def preflight(request: Request) -> PreflightResponse | JSONResponse:\n    if not _protection_layer_ready():\n        return JSONResponse(\n            status_code=503,\n            content=_protection_unavailable_payload(preflight=True),\n        )\n\n    client_key = request.client.host if request.client else "unknown"\n''',
    )

    replace_once(
        path,
        '''async def submit(request: Request) -> SubmitResponse | JSONResponse:\n    # Part G: streaming body-size limit\n''',
        '''async def submit(request: Request) -> SubmitResponse | JSONResponse:\n    if not _protection_layer_ready():\n        return JSONResponse(\n            status_code=503,\n            content=_protection_unavailable_payload(preflight=False),\n        )\n\n    # Part G: streaming body-size limit\n''',
    )


def patch_models() -> None:
    replace_once(
        "apps/record_chain_intake_gateway/gateway/models.py",
        '''    token_configured: bool\n    write_mode: str\n''',
        '''    token_configured: bool\n    cooldown_secret_configured: bool = False\n    write_mode: str\n''',
    )
    replace_once(
        "apps/record_chain_intake_gateway/gateway/models.py",
        '''    max_text_field_chars: int\n    protection_layer_active: bool\n''',
        '''    max_text_field_chars: int\n    protection_required: bool = False\n    protection_layer_active: bool\n''',
    )


def patch_secure_entrypoint() -> None:
    replace_once(
        "apps/record_chain_intake_gateway/secure_entrypoint.py",
        '''                "protection_layer_active": info["protection_layer_active"],\n                "protection_entrypoint": info["protection_entrypoint"],\n''',
        '''                "protection_required": True,\n                "protection_layer_active": info["protection_layer_active"],\n                "protection_entrypoint": info["protection_entrypoint"],\n''',
    )


def patch_render_configuration() -> None:
    replace_once(
        "render.yaml",
        '''      - key: TRINITY_GATEWAY_RUNTIME_VERSION\n        value: 1.2.1-protected\n''',
        '''      - key: TRINITY_GATEWAY_RUNTIME_VERSION\n        value: 1.2.1-protected\n      - key: TRINITY_ENFORCE_PROTECTION_LAYER\n        value: "1"\n''',
    )

    path = "scripts/render_manual_deploy.py"
    replace_once(
        path,
        'EXPECTED_GATEWAY_HEALTH_CHECK_PATH = "/readyz"\n',
        'EXPECTED_GATEWAY_HEALTH_CHECK_PATH = "/healthz"\n',
    )
    replace_once(
        path,
        '''    "TRINITY_GATEWAY_RUNTIME_VERSION": "1.2.1-protected",\n''',
        '''    "TRINITY_GATEWAY_RUNTIME_VERSION": "1.2.1-protected",\n    "TRINITY_ENFORCE_PROTECTION_LAYER": "1",\n''',
    )
    replace_once(
        path,
        '''    "protection_layer_active": True,\n    "protection_entrypoint": "apps.record_chain_intake_gateway.secure_entrypoint:app",\n''',
        '''    "protection_required": True,\n    "protection_layer_active": True,\n    "protection_entrypoint": "apps.record_chain_intake_gateway.secure_entrypoint:app",\n''',
    )
    replace_once(
        path,
        '''    if service_health_check_path(service) != EXPECTED_GATEWAY_HEALTH_CHECK_PATH:\n        # healthCheckPath is a web-service field in Render's Update Service API.\n        request(\n            f"/services/{service_id}",\n            token,\n            method="PATCH",\n            body={"healthCheckPath": EXPECTED_GATEWAY_HEALTH_CHECK_PATH},\n        )\n        print("RENDER_CONFIG_UPDATED field=healthCheckPath")\n''',
        '''    observed_health_path = service_health_check_path(service)\n    if observed_health_path != EXPECTED_GATEWAY_HEALTH_CHECK_PATH:\n        fail(\n            "Render healthCheckPath must remain the protected /healthz route; "\n            f"observed {observed_health_path or 'missing'}"\n        )\n''',
    )
    replace_once(
        path,
        '''        "RENDER_CONFIG_ATTESTED secure_entrypoint=true health_check_path=/readyz "\n''',
        '''        "RENDER_CONFIG_ATTESTED secure_entrypoint=true health_check_path=/healthz "\n        "auxiliary_ready_path=/readyz "\n''',
    )

    replace_once(
        path,
        '''    protected_status, protected = _public_json(\n        f"{base_url.rstrip('/')}/readyz?protection_attestation={nonce}"\n    )\n    if protected_status != 200 or protected.get("ok") is not True:\n        raise RuntimeError(f"protected readiness returned HTTP {protected_status}")\n    if protected.get("version") != EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_RUNTIME_VERSION"]:\n        raise RuntimeError("protected readiness runtime version does not match deployed config")\n    if protected.get("protection_layer_active") is not True:\n        raise RuntimeError("protected readiness does not attest the protection layer")\n    if protected.get("protection_entrypoint") != "apps.record_chain_intake_gateway.secure_entrypoint:app":\n        raise RuntimeError("protected readiness does not attest the secure entrypoint")\n''',
        '''    for route in ("/healthz", "/readyz"):\n        protected_status, protected = _public_json(\n            f"{base_url.rstrip('/')}{route}?protection_attestation={nonce}"\n        )\n        if protected_status != 200 or protected.get("ok") is not True:\n            raise RuntimeError(f"protected {route} returned HTTP {protected_status}")\n        if protected.get("version") != EXPECTED_GATEWAY_ENV["TRINITY_GATEWAY_RUNTIME_VERSION"]:\n            raise RuntimeError(f"protected {route} runtime version does not match deployed config")\n        if protected.get("protection_required") is not True:\n            raise RuntimeError(f"protected {route} does not attest required protection")\n        if protected.get("protection_layer_active") is not True:\n            raise RuntimeError(f"protected {route} does not attest the protection layer")\n        if protected.get("protection_entrypoint") != "apps.record_chain_intake_gateway.secure_entrypoint:app":\n            raise RuntimeError(f"protected {route} does not attest the secure entrypoint")\n''',
    )

    replace_once(
        "scripts/render_protected_deploy.py",
        '''    if payload.get("protection_layer_active") is not True:\n        raise RuntimeError(f"protected {route} does not attest the protection layer")\n''',
        '''    if payload.get("protection_required") is not True:\n        raise RuntimeError(f"protected {route} does not attest required protection")\n    if payload.get("protection_layer_active") is not True:\n        raise RuntimeError(f"protected {route} does not attest the protection layer")\n''',
    )


def patch_machine_contracts() -> None:
    gateway = load_json("api/record-chain-intake-gateway.v1.json")
    gateway["updated_at"] = "2026-08-02T14:22:00Z"
    endpoints = gateway["endpoints"]
    endpoints["health"]["description"] = (
        "Protected production health/readiness probe. Returns 200 only when the secure "
        "protection entrypoint is active and required repository, credential, and cooldown "
        "configuration is present; otherwise returns 503."
    )
    endpoints["protected_readiness"] = {
        "description": (
            "Auxiliary protected readiness probe using the same fail-closed checks as /healthz."
        ),
        "method": "GET",
        "path": "/readyz",
        "response_content_type": "application/json",
    }
    endpoints["readiness"]["description"] = (
        "Detailed readiness probe. Returns 200 only when the protection layer is active and "
        "the gateway can accept submissions, 503 otherwise."
    )
    runtime = gateway["runtime_alignment"]
    runtime["production_enforcement_env"] = "TRINITY_ENFORCE_PROTECTION_LAYER=1"
    runtime["core_app_fails_closed_when_protection_required"] = True
    runtime["healthz_and_readyz_require_active_protection"] = True
    runtime["preflight_and_submit_fail_closed_without_required_protection"] = True
    write_json("api/record-chain-intake-gateway.v1.json", gateway)

    policy = load_json("api/gateway-rate-limit-policy.v1.json")
    status = policy["implementation_status"]
    status["production_enforcement_env"] = "TRINITY_ENFORCE_PROTECTION_LAYER=1"
    status["core_app_fails_closed_when_protection_required"] = True
    status["preflight_and_submit_fail_closed_without_required_protection"] = True
    write_json("api/gateway-rate-limit-policy.v1.json", policy)

    discovery = load_json(".well-known/trinity-accord.json")
    discovery["updated_at"] = "2026-08-02"
    write_json(".well-known/trinity-accord.json", discovery)


def patch_tests() -> None:
    replace_once(
        "tests/test_render_protected_health_deploy.py",
        '''                "protection_layer_active": True,\n                "protection_entrypoint": "apps.record_chain_intake_gateway.secure_entrypoint:app",\n''',
        '''                "protection_required": True,\n                "protection_layer_active": True,\n                "protection_entrypoint": "apps.record_chain_intake_gateway.secure_entrypoint:app",\n''',
    )
    replace_once(
        "tests/test_render_protected_health_deploy.py",
        '''    assert "healthCheckPath: /healthz" in render\n''',
        '''    assert "healthCheckPath: /healthz" in render\n    assert "TRINITY_ENFORCE_PROTECTION_LAYER" in render\n    assert module.base.EXPECTED_GATEWAY_HEALTH_CHECK_PATH == "/healthz"\n''',
    )

    test_path = ROOT / "tests/test_gateway_production_protection_guard.py"
    test_path.write_text(
        '''from __future__ import annotations\n\nimport os\nimport subprocess\nimport sys\nimport textwrap\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\n\n\ndef _run_isolated(code: str) -> subprocess.CompletedProcess[str]:\n    env = os.environ.copy()\n    env.update({\n        "TRINITY_ENFORCE_PROTECTION_LAYER": "1",\n        "TRINITY_REPO_FULL_NAME": "thechurchofagi/trinity-accord",\n        "TRINITY_TARGET_BRANCH": "main",\n        "TRINITY_GITHUB_TOKEN": "test-token",\n        "TRINITY_COOLDOWN_SECRET": "test-secret",\n        "TRINITY_GATEWAY_RUNTIME_VERSION": "1.2.1-protected",\n    })\n    return subprocess.run(\n        [sys.executable, "-c", textwrap.dedent(code)],\n        cwd=ROOT,\n        env=env,\n        capture_output=True,\n        text=True,\n        check=False,\n    )\n\n\ndef test_direct_core_app_fails_closed_when_protection_is_required() -> None:\n    result = _run_isolated(\n        """\n        from fastapi.testclient import TestClient\n        from apps.record_chain_intake_gateway.app import app\n\n        client = TestClient(app)\n        health = client.get('/healthz')\n        assert health.status_code == 503, health.text\n        assert health.json()['ok'] is False\n        assert health.json()['protection_required'] is True\n        assert health.json()['protection_layer_active'] is False\n\n        readiness = client.get('/record-chain/readiness')\n        assert readiness.status_code == 503, readiness.text\n        data = readiness.json()\n        assert data['submit_ready'] is False\n        assert data['preflight_ready'] is False\n        assert data['protection_required'] is True\n        assert data['protection_layer_active'] is False\n\n        for route in ('/record-chain/preflight', '/record-chain/submit'):\n            response = client.post(route, json={})\n            assert response.status_code == 503, (route, response.text)\n            assert response.json()['diagnostic_code'] == 'PROTECTION_LAYER_INACTIVE'\n        """\n    )\n    assert result.returncode == 0, result.stdout + result.stderr\n\n\ndef test_secure_entrypoint_satisfies_required_protection_contract() -> None:\n    result = _run_isolated(\n        """\n        from fastapi.testclient import TestClient\n        from apps.record_chain_intake_gateway.secure_entrypoint import app\n\n        client = TestClient(app)\n        for route in ('/healthz', '/readyz'):\n            response = client.get(route)\n            assert response.status_code == 200, (route, response.text)\n            data = response.json()\n            assert data['ok'] is True\n            assert data['protection_required'] is True\n            assert data['protection_layer_active'] is True\n\n        readiness = client.get('/record-chain/readiness')\n        assert readiness.status_code == 200, readiness.text\n        data = readiness.json()\n        assert data['submit_ready'] is True\n        assert data['preflight_ready'] is True\n        assert data['protection_required'] is True\n        assert data['protection_layer_active'] is True\n        """\n    )\n    assert result.returncode == 0, result.stdout + result.stderr\n\n\ndef test_machine_contract_describes_layered_fail_closed_health() -> None:\n    import json\n\n    contract = json.loads(\n        (ROOT / 'api/record-chain-intake-gateway.v1.json').read_text(encoding='utf-8')\n    )\n    endpoints = contract['endpoints']\n    assert endpoints['health']['path'] == '/healthz'\n    assert endpoints['protected_readiness']['path'] == '/readyz'\n    runtime = contract['runtime_alignment']\n    assert runtime['core_app_fails_closed_when_protection_required'] is True\n    assert runtime['preflight_and_submit_fail_closed_without_required_protection'] is True\n\n\ndef test_fastapi_metadata_matches_gateway_contract_version() -> None:\n    result = _run_isolated(\n        """\n        from apps.record_chain_intake_gateway.app import app, _GATEWAY_SCHEMA\n        assert app.version == _GATEWAY_SCHEMA['version'] == '1.1.0'\n        """\n    )\n    assert result.returncode == 0, result.stdout + result.stderr\n''',
        encoding="utf-8",
    )


def main() -> int:
    patch_app()
    patch_models()
    patch_secure_entrypoint()
    patch_render_configuration()
    patch_machine_contracts()
    patch_tests()
    print("Applied fail-closed production protection and machine-contract fixes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
