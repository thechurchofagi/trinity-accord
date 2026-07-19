#!/usr/bin/env python3
"""Verify every Node runtime and CI install is bound to a committed lockfile."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"
NODE_VERSION = ROOT / ".node-version"
NODE_PROJECTS = (
    (ROOT / "package.json", ROOT / "package-lock.json"),
    (
        ROOT / "examples/github-app-backend/package.json",
        ROOT / "examples/github-app-backend/package-lock.json",
    ),
)
errors: list[str] = []


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)} invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)} root is not an object")
        return {}
    return value


def direct_dependencies(value: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        dependencies = value.get(section, {})
        if not isinstance(dependencies, dict):
            errors.append(f"package.json {section} is not an object")
            continue
        for name, spec in dependencies.items():
            if isinstance(name, str) and isinstance(spec, str):
                result[name] = spec
    return result


if not NODE_VERSION.is_file():
    errors.append(".node-version missing")
    node_version = ""
else:
    node_version = NODE_VERSION.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", node_version):
        errors.append(f".node-version not a valid exact semver: {node_version!r}")

for package_path, lock_path in NODE_PROJECTS:
    if not package_path.is_file():
        errors.append(f"missing {package_path.relative_to(ROOT)}")
        continue
    if not lock_path.is_file():
        errors.append(f"missing {lock_path.relative_to(ROOT)}")
        continue
    package = load_object(package_path)
    lock = load_object(lock_path)
    if lock.get("lockfileVersion") not in (2, 3):
        errors.append(
            f"{lock_path.relative_to(ROOT)} unexpected lockfileVersion: {lock.get('lockfileVersion')}"
        )
    lock_root = (lock.get("packages") or {}).get("")
    if not isinstance(lock_root, dict):
        errors.append(f"{lock_path.relative_to(ROOT)} has no packages[''] root binding")
        continue
    package_dependencies = direct_dependencies(package)
    lock_dependencies = direct_dependencies(lock_root)
    if package_dependencies != lock_dependencies:
        errors.append(
            f"{lock_path.relative_to(ROOT)} direct dependencies do not match "
            f"{package_path.relative_to(ROOT)}"
        )
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        dependencies = package.get(section, {})
        if not isinstance(dependencies, dict):
            continue
        for name, spec in dependencies.items():
            if spec in ("*", "latest", "next"):
                errors.append(
                    f"{package_path.relative_to(ROOT)} {section}.{name} uses floating spec {spec!r}"
                )

for path in sorted(WF_DIR.glob("*.yml")):
    text = path.read_text(encoding="utf-8")
    if "actions/setup-node@" in text:
        if "node-version-file:" not in text or ".node-version" not in text:
            errors.append(f"{path.name}: setup-node is not bound to .node-version")
        if re.search(r"(?m)^\s*node-version:\s*[\"']?\d+", text):
            errors.append(f"{path.name}: hard-coded Node version competes with .node-version")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "npm install" in stripped and "npm ci" not in stripped and "-g" not in stripped:
            errors.append(f"{path.name}: prefer locked npm ci over npm install: {stripped}")
        if re.search(r"(^|\s)yarn(\s|$)", stripped):
            errors.append(f"{path.name}: yarn install is not bound to the committed npm lock: {stripped}")

try:
    render = yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))
    services = render.get("services", []) if isinstance(render, dict) else []
    legacy = next(
        (
            service
            for service in services
            if isinstance(service, dict) and service.get("name") == "trinity-agent-issue-gateway"
        ),
        None,
    )
    if legacy is None:
        errors.append("render.yaml missing trinity-agent-issue-gateway")
    else:
        build = str(legacy.get("buildCommand", ""))
        if "npm ci" not in build or "yarn" in build:
            errors.append("legacy Render service does not install package-lock with npm ci")
        if legacy.get("startCommand") != "npm start":
            errors.append("legacy Render service does not use npm start")
        env = {
            item.get("key"): item.get("value")
            for item in legacy.get("envVars", [])
            if isinstance(item, dict)
        }
        if env.get("NODE_VERSION") != node_version:
            errors.append("legacy Render NODE_VERSION does not match .node-version")
except (OSError, yaml.YAMLError, AttributeError) as exc:
    errors.append(f"cannot validate Render Node runtime: {exc}")

if errors:
    print("FAIL: Node dependency/runtime pinning violations:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("NODE_DEPENDENCY_PINNING_OK")
