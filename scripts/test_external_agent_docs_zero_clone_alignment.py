#!/usr/bin/env python3
"""External-agent docs must align with zero-clone and current Gateway endpoints."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "ai.txt": ROOT / "ai.txt",
    "llms.txt": ROOT / "llms.txt",
    "gateway-workflows.md": ROOT / "gateway-workflows.md",
    "external-agent-quickstart.md": ROOT / "external-agent-quickstart.md",
    "zero-clone-builders.md": ROOT / "zero-clone-builders.md",
    "api/external-agent-operation-examples.v1.json": ROOT / "api" / "external-agent-operation-examples.v1.json",
}

REQUIRED_BY_FILE = {
    "ai.txt": [
        "/external-agent-quickstart/",
        "/zero-clone-builders/",
        "/api/formal-builder-bundles.v1.json",
        "/api/external-agent-operation-examples.v1.json",
        "/gateway/preflight",
        "/agent-submit",
    ],
    "llms.txt": [
        "/external-agent-quickstart/",
        "/zero-clone-builders/",
        "/api/formal-builder-bundles.v1.json",
        "/api/external-agent-operation-examples.v1.json",
        "/gateway/preflight",
        "/agent-submit",
        "zero-clone",
    ],
    "gateway-workflows.md": [
        "/external-agent-quickstart/",
        "/zero-clone-builders/",
        "/api/formal-builder-bundles.v1.json",
        "/api/external-agent-operation-examples.v1.json",
        "/gateway/preflight",
        "/agent-submit",
    ],
    "external-agent-quickstart.md": [
        "without cloning the full repository",
        "download_and_run_builder_bundle.py",
        "/gateway/preflight",
        "/agent-submit",
        "/api/formal-builder-bundles.v1.json",
        "/api/external-agent-operation-examples.v1.json",
    ],
    "zero-clone-builders.md": [
        "without cloning the full repository",
        "canonical builder",
        "/api/formal-builder-bundles.v1.json",
        "/external-agent-quickstart/",
    ],
}

FORBIDDEN_ACTIVE_SNIPPETS = {
    "ai.txt": [
        "/external-agent-quickstart.md",
    ],
    "gateway-workflows.md": [
        "Download individually if full clone is not possible",
    ],
}


def main() -> int:
    errors: list[str] = []

    for label, path in FILES.items():
        if not path.exists():
            errors.append(f"{label}: file missing")
            continue

        text = path.read_text(encoding="utf-8")

        for required in REQUIRED_BY_FILE.get(label, []):
            if required not in text:
                errors.append(f"{label}: missing required docs alignment snippet: {required}")

        for forbidden in FORBIDDEN_ACTIVE_SNIPPETS.get(label, []):
            if forbidden in text:
                errors.append(f"{label}: forbidden stale docs snippet remains: {forbidden}")

    examples_path = FILES["api/external-agent-operation-examples.v1.json"]
    if examples_path.exists():
        data = json.loads(examples_path.read_text(encoding="utf-8"))
        op = data.get("examples", {}).get("operational_canary", {})
        if op.get("formal_submission") is not False:
            errors.append("operation examples: operational_canary.formal_submission must be false")
        if op.get("do_not_present_as_formal_submission") is not True:
            errors.append("operation examples: operational_canary must explicitly not present as formal submission")
        if op.get("zero_clone_formal_builder_route") is not False:
            errors.append("operation examples: operational_canary.zero_clone_formal_builder_route must be false")

    if errors:
        print("FAIL: external-agent docs zero-clone alignment errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: external-agent docs align with zero-clone and Gateway endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
