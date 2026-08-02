#!/usr/bin/env python3
"""Scan public agent entrypoints for retired gateway references.

Current discovery and submission surfaces must point to the protected
Record-Chain Intake Gateway. Historical files may retain old routes only when
they declare their retired status and current replacement before those routes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# Public JSON surfaces that agents may discover or that have previously been
# presented as a production route. They must either be current and clean or
# explicitly fail closed as historical archive material.
CORE_ENTRYPOINTS: frozenset[str] = frozenset({
    "gateway-config.json",
    "external-agent-quickstart.json",
    "gateway-workflows.v1.json",
    "formal-builder-bundles.v1.json",
    "record-chain-intake-gateway.v1.json",
    "agent-first-contact.json",
    "agent-start.v2.json",
    "links.json",
    "agent-gateway-production-profile.json",
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

# Keys whose values are allowed to contain forbidden strings because the key
# itself makes the retirement boundary machine-readable.
ALLOWED_CONTEXT_KEYS: frozenset[str] = frozenset({
    "retired_gateway_v1",
    "retired_replacement",
    "retired_runtime",
    "retired_backend",
    "retirement_reason",
    "historical_profile",
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

# Human-readable active pages may state that an exact old route is retired.
# The retirement must be explicit on the same line; a bare executable path is
# never accepted merely because another paragraph elsewhere says "legacy".
RETIREMENT_LINE_MARKERS = (
    "retired",
    "historical",
    "legacy",
    "do not use",
    "must not use",
    "not use for new",
    "no longer active",
)

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
        and bool(data.get("replacement"))
    )


def first_forbidden_index(text: str) -> int | None:
    hits = [text.find(token) for token in FORBIDDEN if token in text]
    hits = [idx for idx in hits if idx >= 0]
    return min(hits) if hits else None


def _find_forbidden_in_active_contexts(obj: Any, path: str = "") -> list[str]:
    """Recursively find forbidden strings outside explicit retirement contexts."""
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
        for index, item in enumerate(obj):
            if isinstance(item, str):
                for token in FORBIDDEN:
                    if token in item:
                        issues.append(f"{path}[{index}]: contains '{token}'")
            else:
                issues.extend(_find_forbidden_in_active_contexts(item, f"{path}[{index}]"))
    return issues


def check_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if not any(token in text for token in FORBIDDEN):
        return

    if path.name not in CORE_ENTRYPOINTS:
        return

    try:
        data = load_json(path)
    except Exception as exc:
        errors.append(f"{path}: invalid JSON while checking public agent entrypoints: {exc}")
        return

    if is_historical(data):
        # Fail-closed ordering: historical status must appear before any old
        # executable route or service name.
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

    active_issues = _find_forbidden_in_active_contexts(data)
    if active_issues:
        errors.append(
            f"{path}: non-historical core entrypoint contains retired gateway references in active context: "
            + "; ".join(active_issues[:5])
        )


ACTIVE_PUBLIC_SURFACES: list[str] = [
    "index.md",
    "agent-first-contact.md",
    "agent-start.md",
    "agent-echo.md",
    "agent-verify.md",
    "agent-verify-simple.md",
    "external-agent-quickstart.md",
    "llms.txt",
    "ai.txt",
    "downloads/record-chain-agent-field-guidance.v1.json",
    "api/agent-first-contact.json",
    "api/agent-start.v2.json",
    "api/record-chain-field-helper.v1.json",
]


def check_active_surface(path: Path) -> None:
    """Reject bare retired routes on active pages.

    An exact old route may appear only in a same-line, explicit retirement or
    prohibition statement. This preserves historical warnings without letting a
    current executable instruction hide behind a remote legacy disclaimer.
    """
    if not path.exists():
        return
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        lower = line.lower()
        for token in FORBIDDEN:
            if token not in line:
                continue
            if any(marker in lower for marker in RETIREMENT_LINE_MARKERS):
                continue
            errors.append(
                f"{path}:{line_number}: active public surface contains bare retired gateway reference '{token}'"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public agent entrypoints")
    parser.add_argument("paths", nargs="+", help="Directories or files to scan")
    args = parser.parse_args()

    files: list[Path] = []
    for raw in args.paths:
        files.extend(iter_json_files(Path(raw)))

    for path in files:
        check_file(path)

    root = Path.cwd()
    for surface in ACTIVE_PUBLIC_SURFACES:
        check_active_surface(root / surface)

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))

    print(
        f"public agent entrypoints OK ({len(files)} JSON files + "
        f"{len(ACTIVE_PUBLIC_SURFACES)} active surfaces checked)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
