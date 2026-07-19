#!/usr/bin/env python3
"""Validate repository JSON with strict RFC-compatible parsing.

Unlike ``python -m json.tool``, this rejects duplicate object keys and the
non-standard NaN/Infinity constants that Python's default decoder accepts.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "node_modules", "_site", "vendor", ".venv", "venv"}


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def load_strict_json_bytes(data: bytes, label: str) -> Any:
    try:
        text = data.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label}: invalid strict UTF-8 JSON: {exc}") from exc


def iter_json_files(paths: Iterable[Path]) -> Iterable[Path]:
    seen: set[Path] = set()
    for path in paths:
        path = path.resolve()
        if path.is_file():
            if path.suffix == ".json" and path not in seen:
                seen.add(path)
                yield path
            continue
        if not path.exists():
            raise FileNotFoundError(path)
        for candidate in sorted(path.rglob("*.json")):
            if any(part in SKIP_PARTS for part in candidate.relative_to(ROOT).parts):
                continue
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, default=[ROOT])
    args = parser.parse_args()

    errors: list[str] = []
    count = 0
    try:
        files = list(iter_json_files(args.paths))
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    for path in files:
        count += 1
        try:
            load_strict_json_bytes(path.read_bytes(), str(path.relative_to(ROOT)))
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    if errors:
        print("FAIL: strict JSON validation errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"PASS: {count} JSON files use strict UTF-8 JSON without duplicate keys or non-finite numbers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
