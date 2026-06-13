#!/usr/bin/env python3
"""Scan public agent JSON entrypoints for retired gateway references.

Checks the core public agent entrypoint JSON files that agents actually
use for discovery and submission routing.  These files must point to the
current Record-Chain Intake Gateway, not the retired Issue Gateway.

Other JSON files in api/ may contain historical references to old routes
(documentation, legacy status, audit reports) — those are scanned by the
broader grep/CI contract tests, not this entrypoint scanner.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# Core entrypoint files that MUST NOT reference old gateway paths in active context.
# These are the files agents discover and use for routing.
CORE_ENTRYPOINTS: frozenset[str] = frozenset({
    "gateway-config.json",
    "external-agent-quickstart.json",
    "gateway-workflows.v1.json",
    "formal-builder-bundles.v1.json",
    "record-chain-intake-gateway.v1.json",
    "agent-first-contact.json",
    "agent-start.v2.json",
    "links.json",
})

FORBIDDEN = [
    "/agent-submit",
    "/gateway/preflight",
    "trinity-agent-issue-gateway",
    "/api/gateway-builder-route-map.v1.json",
    "/api/gateway-workflows.v1.json",
]

REQUIRED_HISTORICAL_FIELDS = [
    "status",
    "do_not_use_for_new_public_submissions",
    "replacement",
]

# Keys whose values are allowed to contain forbidden strings
# (retirement/legacy metadata sections)
ALLOWED_CONTEXT_KEYS: frozenset[str] = frozenset({
    "retired_gateway_v1",
    "retired_replacement",
    "legacy_prerequisites_retired",
    "legacy_registry_is_historical_archive_only",
    "legacy_warning",
    "retired",
    "do_not_use",
    "do_not_use_for_new_public_submissions",
    "never_do",
    "legacy_machine",
    "deprecated_for_new_records",
})

errors: list[str] = []


def is_json_path(path: Path) -> bool:
    return path.is_file() and path.suffix == ".json"


def iter_json_files(root: Path) -> list[Path]:
    if is_json_path(root):
        return [root]
    if root.is_dir():
        return sorted(p for p in root.rglob("*.json") if p.is_file())
    return []


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_historical(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and data.get("status") == "historical_archive_only"
        and data.get("do_not_use_for_new_public_submissions") is True
        and isinstance(data.get("replacement"), str)
        and data.get("replacement")
    )


def first_forbidden_index(text: str) -> int | None:
    hits = [text.find(token) for token in FORBIDDEN if token in text]
    hits = [idx for idx in hits if idx >= 0]
    return min(hits) if hits else None


def _find_forbidden_in_active_contexts(obj: Any, path: str = "") -> list[str]:
    """Recursively find forbidden strings outside allowed retirement contexts."""
    issues: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            if key in ALLOWED_CONTEXT_KEYS:
                continue
            if isinstance(value, str):
                for token in FORBIDDEN:
                    if token in value:
                        issues.append(f"{current_path}: contains '{token}'")
            else:
                issues.extend(_find_forbidden_in_active_contexts(value, current_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                for token in FORBIDDEN:
                    if token in item:
                        issues.append(f"{path}[{i}]: contains '{token}'")
            else:
                issues.extend(_find_forbidden_in_active_contexts(item, f"{path}[{i}]"))
    return issues


def check_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN if token in text]
    if not hits:
        return

    # Only strictly check core entrypoint files
    if path.name not in CORE_ENTRYPOINTS:
        return

    try:
        data = load_json(path)
    except Exception as exc:
        errors.append(f"{path}: invalid JSON while checking public agent entrypoints: {exc}")
        return

    if is_historical(data):
        # Fail-closed ordering: historical status must appear before old executable paths.
        status_idx = text.find('"status"')
        forbidden_idx = first_forbidden_index(text)
        if forbidden_idx is not None and (status_idx < 0 or status_idx > forbidden_idx):
            errors.append(
                f"{path}: historical status must appear before retired gateway references"
            )
        for field in REQUIRED_HISTORICAL_FIELDS:
            if field not in data:
                errors.append(f"{path}: historical JSON missing top-level {field}")
        return

    # Non-historical core entrypoint: check for forbidden strings in active contexts
    active_issues = _find_forbidden_in_active_contexts(data)
    if active_issues:
        errors.append(
            f"{path}: non-historical core entrypoint contains retired gateway references in active context: "
            + "; ".join(active_issues[:5])
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public agent JSON entrypoints")
    parser.add_argument("paths", nargs="+", help="Directories or files to scan")
    args = parser.parse_args()

    files: list[Path] = []
    for raw in args.paths:
        files.extend(iter_json_files(Path(raw)))

    for path in files:
        check_file(path)

    if errors:
        raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))

    print(f"public agent entrypoints OK ({len(files)} JSON files checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
