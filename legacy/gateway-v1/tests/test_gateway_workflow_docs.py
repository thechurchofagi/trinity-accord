#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def must_contain(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [n for n in needles if n not in text]
    if missing:
        raise AssertionError(f"{path} missing: {missing}")

def main() -> None:
    must_contain("gateway-workflows.md", [
        "permalink: /gateway-workflows/",
        "Workflow 1 — Pure Echo",
        "Workflow 2 — V0–V5 agent-declared verification archive",
        "Workflow 3 — V6+ strict evidence",
        "Workflow 4 — Verification Echo (strict evidence, legacy E2)",
        "Workflow 5 — Guardian Stage 1 application",
        "Workflow 6 — Guardian Stage 2 listing",
        "Workflow 7 — Guardian-signed Echo",
        "Common artifact custody",
        "Do not patch signed JSON",
        "agent_readback_sha256",
        "guardian_presence_proof",
        "Success criteria",
        "<a id=\"workflow-pure-echo\"></a>",
        "<a id=\"workflow-v0-v5-agent-declared-archive\"></a>",
        "<a id=\"workflow-v6-plus-strict-evidence\"></a>",
        "<a id=\"workflow-e2-verification-echo\"></a>",
        "<a id=\"workflow-guardian-stage-1-application\"></a>",
        "<a id=\"workflow-guardian-stage-2-listing\"></a>",
        "<a id=\"workflow-guardian-signed-echo\"></a>",
    ])

    must_contain("agent-start.md", [
        "/gateway-workflows/",
        "/api/gateway-workflows.v1.json",
        "/api/gateway-artifact-custody.v1.json",
        "#workflow-pure-echo",
        "#workflow-guardian-signed-echo",
    ])

    must_contain("agent-submit.md", [
        "/gateway-workflows/",
        "/api/gateway-workflows.v1.json",
        "/api/gateway-artifact-custody.v1.json",
    ])

    must_contain("external-agent-quickstart.md", [
        "/gateway-workflows/",
        "/api/gateway-workflows.v1.json",
    ])

    must_contain("llms.txt", [
        "/gateway-workflows/",
        "/api/gateway-workflows.v1.json",
        "/api/gateway-artifact-custody.v1.json",
    ])

    print("PASS: test_gateway_workflow_docs")

if __name__ == "__main__":
    main()
