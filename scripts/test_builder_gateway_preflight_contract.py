#!/usr/bin/env python3
"""Smoke test: Gateway app can be imported and basic endpoints respond.

This is a minimal smoke harness for PR-01. Full response-schema E2E tests
belong in PR-02. This test only verifies the app starts and returns JSON
on health/readiness endpoints — it does NOT assert response schema validity
against public schemas (that's PR-02).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def test_gateway_app_importable():
    """Verify the FastAPI app can be imported without errors."""
    sys.path.insert(0, str(ROOT / "apps" / "record_chain_intake_gateway"))
    try:
        import app as gateway_app  # noqa: F401
        require(hasattr(gateway_app, "app"), "gateway app module must export 'app' object")
        print("  ✅ Gateway app importable")
    except ImportError as exc:
        # If deps aren't installed, skip gracefully
        print(f"  ⚠️  Gateway app import skipped (missing deps): {exc}")
    finally:
        sys.path.pop(0)


def test_gateway_healthz():
    """Verify /healthz or /record-chain/readiness returns a JSON response."""
    sys.path.insert(0, str(ROOT / "apps" / "record_chain_intake_gateway"))
    try:
        from app import app as fastapi_app
        from fastapi.testclient import TestClient

        client = TestClient(fastapi_app)

        # Try healthz
        resp = client.get("/healthz")
        require(resp.status_code == 200, f"/healthz returned {resp.status_code}")
        require(isinstance(resp.json(), dict), "/healthz must return JSON dict")
        print("  ✅ /healthz responds with JSON")

        # Try readiness
        resp = client.get("/record-chain/readiness")
        require(resp.status_code in (200, 503), f"/record-chain/readiness returned {resp.status_code}")
        require(isinstance(resp.json(), dict), "/record-chain/readiness must return JSON dict")
        print("  ✅ /record-chain/readiness responds with JSON")

    except ImportError as exc:
        print(f"  ⚠️  Gateway E2E skipped (missing deps): {exc}")
    finally:
        sys.path.pop(0)


def main() -> int:
    print("test_builder_gateway_preflight_contract (smoke harness)")
    test_gateway_app_importable()
    test_gateway_healthz()

    if errors:
        raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))

    print("gateway smoke OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
