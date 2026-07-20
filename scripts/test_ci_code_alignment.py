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
NO_MUTATING_SITEMAP_WORKFLOWS = CI_WORKFLOWS | {"deploy-pages.yml"}
ARCHIVE_REPAIR_WORKFLOW = "archive-backlog-repair.yml"


class UniqueKeyLoader(yaml.SafeLoader):
    """PyYAML loader that rejects duplicate mapping keys."""


def construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found unhashable key {key!r}",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
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
        package = match.group(1).lower()
        if package in result:
            raise ValueError(f"{path.relative_to(ROOT)}:{lineno} duplicates dependency {package}")
        result[package] = match.group(2)
    return result


def main() -> int:
    errors: list[str] = []
    texts: dict[str, str] = {}
    docs: dict[str, dict[str, Any]] = {}

    workflow_paths = sorted(WORKFLOWS.glob("*.yml"))
    if not workflow_paths:
        errors.append("no GitHub Actions workflows found")

    for path in workflow_paths:
        name = path.name
        texts[name] = path.read_text(encoding="utf-8")
        try:
            docs[name] = load_yaml(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    for name in sorted(CI_WORKFLOWS | {"deploy-pages.yml", ARCHIVE_REPAIR_WORKFLOW}):
        if name not in texts:
            errors.append(f"missing workflow {name}")

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

    for name, text in sorted(texts.items()):
        if "actions/setup-node@" not in text:
            continue
        if "node-version-file:" not in text or ".node-version" not in text:
            errors.append(f"{name}: Node setup is not bound to .node-version")
        if re.search(r"(?m)^\s*node-version:\s*[\"']?\d+", text):
            errors.append(f"{name}: hard-coded Node major competes with .node-version")

    for name in sorted(NO_MUTATING_SITEMAP_WORKFLOWS):
        text = texts.get(name, "")
        for line in text.splitlines():
            if "scripts/generate_sitemap.py" in line and "--check" not in line:
                errors.append(f"{name}: mutates sitemap before checking committed drift: {line.strip()}")

    for name in (
        "repository-integrity.yml",
        "repository-full-integrity.yml",
        "record-chain-gateway-tests.yml",
    ):
        text = texts.get(name, "")
        if "scripts/validate_json_strict.py" not in text:
            errors.append(f"{name}: does not use strict JSON validation")
        if "python3 -m json.tool" in text or "python -m json.tool" in text:
            errors.append(f"{name}: still relies on permissive json.tool validation")

    repository_integrity = texts.get("repository-integrity.yml", "")
    for marker in (
        "scripts/test_ci_code_alignment.py",
        "scripts/test_workflows_do_not_reference_missing_scripts.py",
        "scripts/test_workflow_permissions.py",
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
        if ".github/workflows/archive-backlog-repair.yml" not in pr_paths:
            errors.append(
                "record-chain-write-path-guard.yml: archive backlog writer workflow is not protected"
            )

        guard_text = texts.get("record-chain-write-path-guard.yml", "")
        if "workflow_run:" in guard_text or "github.event.workflow_run.head_sha" in guard_text:
            errors.append(
                "record-chain-write-path-guard.yml: must not treat workflow_run.head_sha as a writer output commit"
            )

        archive_text = texts.get(ARCHIVE_REPAIR_WORKFLOW, "")
        for marker in (
            "validate_exact_archive_commit",
            "git rev-list --count",
            "scripts/check_record_chain_write_path_guard.py",
            '--github-actor "github-actions[bot]"',
            'git push origin HEAD:main',
            "Equivalent archive backlog state already reached main",
        ):
            if marker not in archive_text:
                errors.append(f"{ARCHIVE_REPAIR_WORKFLOW}: missing exact-commit guard marker {marker}")

        push_index = archive_text.find("git push origin HEAD:main")
        function_index = archive_text.find("validate_exact_archive_commit()")
        call_index = archive_text.rfind("validate_exact_archive_commit", 0, push_index)
        if push_index < 0 or function_index < 0 or call_index <= function_index:
            errors.append(
                f"{ARCHIVE_REPAIR_WORKFLOW}: exact archive commit is not validated immediately before push"
            )
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"write-path guard alignment check failed: {exc}")

    if errors:
        print("FAIL: CI/code alignment errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"PASS: {len(texts)} workflows parse strictly and align with runtime versions, locked dependencies, "
        "strict data validation, non-mutating drift checks, and exact writer commit inputs"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
