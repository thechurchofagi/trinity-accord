#!/usr/bin/env python3
"""Static regression tests for Gateway production readiness hardening."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path):
    return json.loads(read(path))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    server = read("examples/github-app-backend/server.js")
    schema = load_json("api/agent-issue-gateway-payload-schema.v1.json")
    integrity = read(".github/workflows/repository-integrity.yml")

    require('app.get("/healthz"' in server, "server.js missing /healthz")
    require('app.get("/readiness"' in server, "server.js missing /readiness")
    require('app.get("/gateway/readiness"' in server, "server.js missing /gateway/readiness")

    require("GATEWAY_CANARY_MODE" in server, "server.js missing GATEWAY_CANARY_MODE")
    require("GATEWAY_READINESS_GITHUB_CHECK" in server, "server.js missing GATEWAY_READINESS_GITHUB_CHECK")
    require("GATEWAY_IDEMPOTENCY_ENABLED" in server, "server.js missing GATEWAY_IDEMPOTENCY_ENABLED")

    require("computeIdempotencyKey" in server, "server.js missing computeIdempotencyKey")
    require("findExistingIssueByIdempotency" in server, "server.js missing findExistingIssueByIdempotency")
    require("trinity-gateway-idempotency" in server, "server.js missing idempotency marker")
    require("best_effort_github_issue_search" in server, "server.js missing best-effort idempotency scope")

    require("request_id" in server, "server.js missing request_id")
    require("retryable" in server, "server.js missing retryable errors")
    require("x-request-id" in server, "server.js missing x-request-id")

    require("DRY_RUN || CANARY_MODE" in server, "server.js must block writes when DRY_RUN or CANARY_MODE")
    require("productionWarnings" in server, "server.js must return production partial warnings")

    require("idempotency_key" in schema["properties"], "payload schema missing idempotency_key")

    require((ROOT / "scripts/replay_gateway_fixtures.py").exists(), "missing replay_gateway_fixtures.py")
    require((ROOT / ".github/workflows/production-gateway-smoke.yml").exists(), "missing production smoke workflow")

    require("test_production_readiness_contract.py" in integrity, "repository-integrity.yml must run production readiness contract test")

    require("guardian_registry_number" in server, "server.js missing guardian_registry_number")
    require("guardianRegistryNumberFromEntry" in server, "server.js missing guardianRegistryNumberFromEntry")

    print("PRODUCTION_READINESS_CONTRACT_OK")


if __name__ == "__main__":
    main()
