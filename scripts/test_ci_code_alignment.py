#!/usr/bin/env python3
"""Fail closed when CI configuration drifts from the code and runtime contract."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
CHECKOUT_REF = "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5"
CI_WORKFLOWS = {
    "repository-integrity.yml",
    "repository-full-integrity.yml",
    "deep-integrity.yml",
    "run-current-tests.yml",
    "record-chain-ci.yml",
    "record-chain-gateway-tests.yml",
    "record-chain-write-path-guard.yml",
}
NODE_WORKFLOWS = {
    "repository-integrity.yml",
    "repository-full-integrity.yml",
    "deep-integrity.yml",
    "run-current-tests.yml",
    "record-chain-gateway-tests.yml",
    "deploy-pages.yml",
}
NO_MUTATING_SITEMAP_WORKFLOWS = CI_WORKFLOWS | {"deploy-pages.yml"}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} YAML root must be a mapping")
    return value


def on_block(data: dict[str, Any]) -> dict[str, Any]:
    # PyYAML 1.1 resolves the unquoted key `on` to boolean True.
    value = data.get("on", data.get(True, {}))
    return value if isinstance(value, dict) else {}


def service_by_name(doc: dict[str, Any], name: str) -> dict[str, Any] | None:
    services = doc.get("services", [])
    if not isinstance(services, list):
        return None
    for service in services:
        if isinstance(service, dict) and service.get("name") == name:
            return service
    return None


def env_map(service: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    env_vars = service.get("envVars", [])
    if not isinstance(env_vars, list):
        return result
    for item in env_vars:
        if not isinstance(item, dict) or not isinstance(item.get("key"), str):
            continue
        result[item["key"]] = item.get("value", {"sync": item.get("sync")})
    return result


def parse_requirements(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_,.-]+\])?==([^\s]+)", line)
        if not match:
            raise ValueError(f"{path.relative_to(ROOT)}:{lineno} is not an exact pin: {line}")
        result[match.group(1).lower()] = match.group(2)
    return result


def main() -> int:
    errors: list[str] = []
    texts: dict[str, str] = {}
    docs: dict[str, dict[str, Any]] = {}

    for name in sorted(CI_WORKFLOWS | {"deploy-pages.yml"}):
        path = WORKFLOWS / name
        if not path.is_file():
            errors.append(f"missing workflow {name}")
            continue
        texts[name] = path.read_text(encoding="utf-8")
        try:
            docs[name] = load_yaml(path)
        except ValueError as exc:
            errors.append(str(exc))

    for name in sorted(CI_WORKFLOWS):
        text = texts.get(name, "")
        if CHECKOUT_REF not in text:
            errors.append(f"{name}: checkout action does not use the reviewed revision")
        if "permissions:" not in text.split("jobs:", 1)[0]:
            errors.append(f"{name}: missing explicit top-level permissions")
        if "runs-on: ubuntu-24.04" not in text:
            errors.append(f"{name}: CI runner is not pinned to ubuntu-24.04")
        if "timeout-minutes:" not in text:
            errors.append(f"{name}: CI jobs have no explicit timeout")

    for name in sorted(NODE_WORKFLOWS):
        text = texts.get(name) or (WORKFLOWS / name).read_text(encoding="utf-8")
        if "actions/setup-node@" not in text:
            continue
        if "node-version-file:" not in text or ".node-version" not in text:
            errors.append(f"{name}: Node setup is not bound to .node-version")
        if re.search(r"(?m)^\s*node-version:\s*[\"']?\d+", text):
            errors.append(f"{name}: hard-coded Node major competes with .node-version")

    for name in sorted(NO_MUTATING_SITEMAP_WORKFLOWS):
        text = texts.get(name) or (WORKFLOWS / name).read_text(encoding="utf-8")
        for line in text.splitlines():
            if "scripts/generate_sitemap.py" in line and "--check" not in line:
                errors.append(f"{name}: mutates sitemap before checking committed drift: {line.strip()}")

    for name in ("repository-integrity.yml", "repository-full-integrity.yml", "record-chain-gateway-tests.yml"):
        text = texts.get(name, "")
        if "scripts/validate_json_strict.py" not in text:
            errors.append(f"{name}: does not use strict JSON validation")
        if "python3 -m json.tool" in text or "python -m json.tool" in text:
            errors.append(f"{name}: still relies on permissive json.tool validation")

    repository_integrity = texts.get("repository-integrity.yml", "")
    for marker in (
        "scripts/test_ci_code_alignment.py",
        "python3 -m compileall",
        "npm ci --ignore-scripts --prefix examples/github-app-backend",
    ):
        if marker not in repository_integrity:
            errors.append(f"repository-integrity.yml: missing required code-coverage marker {marker}")

    deep = texts.get("deep-integrity.yml", "")
    if "npm ci" not in deep:
        errors.append("deep-integrity.yml: Node-based groups run without installing the locked root dependencies")

    try:
        root_render = yaml.safe_load(read("render.yaml"))
        mirror_render = yaml.safe_load(read("apps/record_chain_intake_gateway/render.yaml"))
        if not isinstance(root_render, dict) or not isinstance(mirror_render, dict):
            raise ValueError("Render YAML roots must be mappings")
        root_gateway = service_by_name(root_render, "trinity-record-chain-gateway")
        mirror_gateway = service_by_name(mirror_render, "trinity-record-chain-gateway")
        if root_gateway is None or mirror_gateway is None:
            errors.append("Render gateway service missing from canonical or mirror config")
        else:
            for key in (
                "type",
                "name",
                "runtime",
                "region",
                "plan",
                "autoDeploy",
                "buildCommand",
                "startCommand",
                "healthCheckPath",
            ):
                if root_gateway.get(key) != mirror_gateway.get(key):
                    errors.append(
                        f"Render gateway mirror drift: {key} canonical={root_gateway.get(key)!r} "
                        f"mirror={mirror_gateway.get(key)!r}"
                    )
            if env_map(root_gateway) != env_map(mirror_gateway):
                errors.append("Render gateway mirror envVars differ from canonical root config")

            production_python = str(env_map(root_gateway).get("PYTHON_VERSION", ""))
            gateway_ci = texts.get("record-chain-gateway-tests.yml", "")
            if not production_python or f'python-version: "{production_python}"' not in gateway_ci:
                errors.append(
                    f"record-chain-gateway-tests.yml does not exercise production Python {production_python!r}"
                )

        legacy = service_by_name(root_render, "trinity-agent-issue-gateway")
        node_version = read(".node-version").strip()
        if legacy is None:
            errors.append("legacy Render tombstone service is missing")
        else:
            legacy_env = env_map(legacy)
            if str(legacy_env.get("NODE_VERSION", "")) != node_version:
                errors.append("legacy Render service NODE_VERSION is not aligned with .node-version")
            build = str(legacy.get("buildCommand", ""))
            if "npm ci" not in build or "yarn" in build:
                errors.append("legacy Render service does not install its committed package-lock with npm ci")
            if legacy.get("startCommand") != "npm start":
                errors.append("legacy Render service startCommand is not npm start")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"Render/runtime alignment check failed: {exc}")

    try:
        ci_req = parse_requirements(ROOT / "requirements-ci.txt")
        app_req = parse_requirements(ROOT / "apps/record_chain_intake_gateway/requirements.txt")
        for package in sorted(set(ci_req) & set(app_req)):
            if ci_req[package] != app_req[package]:
                errors.append(
                    f"Python requirement drift for {package}: CI={ci_req[package]} gateway={app_req[package]}"
                )
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

    try:
        guard = docs.get("record-chain-write-path-guard.yml") or load_yaml(
            WORKFLOWS / "record-chain-write-path-guard.yml"
        )
        events = on_block(guard)
        pr_paths = set((events.get("pull_request") or {}).get("paths", []))
        push_paths = set((events.get("push") or {}).get("paths", []))
        if pr_paths != push_paths:
            errors.append(
                "record-chain-write-path-guard.yml: push and pull_request protected path sets differ"
            )
        guard_text = texts.get("record-chain-write-path-guard.yml", "")
        if "github.event.workflow_run.head_sha" not in guard_text:
            errors.append("record-chain-write-path-guard.yml: workflow_run does not audit its exact head SHA")
        for marker in (
            "github.event.workflow_run.conclusion == 'success'",
            "github.event.workflow_run.head_branch == 'main'",
        ):
            if marker not in guard_text:
                errors.append(f"record-chain-write-path-guard.yml: missing workflow_run boundary {marker}")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"write-path guard alignment check failed: {exc}")

    group = read("scripts/run_ci_group.py")
    for command in (
        "scripts/test_ci_code_alignment.py",
        "scripts/validate_json_strict.py",
        "scripts/test_workflows_do_not_reference_missing_scripts.py",
        "scripts/test_workflow_permissions.py",
    ):
        if command not in group:
            errors.append(f"p0-current does not register {command}")

    if errors:
        print("FAIL: CI/code alignment errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"PASS: {len(CI_WORKFLOWS)} CI workflows align with runtime versions, locked dependencies, "
        "strict data validation, non-mutating drift checks, and exact workflow inputs"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
