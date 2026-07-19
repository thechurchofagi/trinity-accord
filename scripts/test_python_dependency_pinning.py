#!/usr/bin/env python3
"""Verify Python dependency files, workflow installs, and production runtime parity."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"
REQUIREMENT_FILES = (
    ROOT / "requirements-ci.txt",
    ROOT / "requirements-ots.txt",
    ROOT / "apps/record_chain_intake_gateway/requirements.txt",
)
errors: list[str] = []


def parse_requirements(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.is_file():
        errors.append(f"{path.relative_to(ROOT)} missing")
        return result
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(
            r"([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_,.-]+\])?==([^\s]+)", line
        )
        if not match:
            errors.append(
                f"{path.relative_to(ROOT)}:{lineno}: dependency is not pinned with ==: {line}"
            )
            continue
        package = match.group(1).lower()
        if package in result:
            errors.append(f"{path.relative_to(ROOT)}:{lineno}: duplicate dependency {package}")
            continue
        result[package] = match.group(2)
    return result


def requirement_refs(text: str) -> Iterable[str]:
    yield from re.findall(r"(?:^|\s)-r\s+([A-Za-z0-9_./-]+\.txt)", text)
    yield from re.findall(r"(?:^|\s)--requirement(?:=|\s+)([A-Za-z0-9_./-]+\.txt)", text)


parsed = {path: parse_requirements(path) for path in REQUIREMENT_FILES}
ci = parsed[ROOT / "requirements-ci.txt"]
gateway = parsed[ROOT / "apps/record_chain_intake_gateway/requirements.txt"]

for required in ("jsonschema", "opentimestamps-client", "pytest", "cryptography"):
    if required not in ci:
        errors.append(f"requirements-ci.txt missing pinned {required}")

for package in sorted(set(ci) & set(gateway)):
    if ci[package] != gateway[package]:
        errors.append(
            f"shared package version drift for {package}: "
            f"requirements-ci={ci[package]} gateway={gateway[package]}"
        )

referenced: set[Path] = set()
for path in sorted(WF_DIR.glob("*.yml")):
    text = path.read_text(encoding="utf-8")
    if "pip install --upgrade pip" in text or "python3 -m pip install --upgrade pip" in text:
        errors.append(f"{path.name}: unpinned pip upgrade")
    for ref in requirement_refs(text):
        req_path = (ROOT / ref).resolve()
        referenced.add(req_path)
        if not req_path.is_file():
            errors.append(f"{path.name}: references missing requirements file {ref}")
        elif req_path not in parsed:
            parsed[req_path] = parse_requirements(req_path)

    for line in text.splitlines():
        stripped = line.strip()
        if "pip install" not in stripped or stripped.startswith("#"):
            continue
        refs = list(requirement_refs(stripped))
        remainder = stripped
        for ref in refs:
            remainder = re.sub(
                rf"(?:-r\s+|--requirement(?:=|\s+)){re.escape(ref)}", "", remainder
            )
        workflow_prefix = r"^(?:-\s+)?(?:run:\s*)?"
        remainder = re.sub(
            workflow_prefix + r"(?:python3?|pip3?)\s+-m\s+pip\s+install\s*",
            "",
            remainder,
        )
        remainder = re.sub(workflow_prefix + r"pip3?\s+install\s*", "", remainder)
        tokens = [
            token
            for token in remainder.split()
            if not token.startswith("-") and token not in {"&&", "\\"}
        ]
        for token in tokens:
            if token.endswith(".txt") or token.startswith("$"):
                continue
            if "==" not in token:
                errors.append(f"{path.name}: unpinned pip install token {token!r}: {stripped}")

for required_path in REQUIREMENT_FILES:
    if required_path.resolve() not in referenced and required_path.name != "requirements-ots.txt":
        errors.append(f"{required_path.relative_to(ROOT)} is not exercised by any workflow")

try:
    render = yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))
    services = render.get("services", []) if isinstance(render, dict) else []
    gateway_service = next(
        (
            service
            for service in services
            if isinstance(service, dict) and service.get("name") == "trinity-record-chain-gateway"
        ),
        None,
    )
    if gateway_service is None:
        errors.append("render.yaml missing trinity-record-chain-gateway")
    else:
        build = str(gateway_service.get("buildCommand", ""))
        if "-r apps/record_chain_intake_gateway/requirements.txt" not in build:
            errors.append("Gateway Render build does not use its committed requirements file")
        env = {
            item.get("key"): item.get("value")
            for item in gateway_service.get("envVars", [])
            if isinstance(item, dict)
        }
        production_python = env.get("PYTHON_VERSION")
        gateway_ci = (WF_DIR / "record-chain-gateway-tests.yml").read_text(encoding="utf-8")
        if not production_python or f'python-version: "{production_python}"' not in gateway_ci:
            errors.append(
                f"Gateway CI does not exercise production Python {production_python!r}"
            )
except (OSError, yaml.YAMLError, AttributeError) as exc:
    errors.append(f"cannot validate Gateway Python runtime: {exc}")

if errors:
    print("FAIL: Python dependency/runtime pinning violations:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print("PYTHON_DEPENDENCY_PINNING_OK")
