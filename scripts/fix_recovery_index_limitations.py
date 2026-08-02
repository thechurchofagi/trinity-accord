#!/usr/bin/env python3
"""Normalize repository-preservation limitations and harden future sealing.

This repair is idempotent. It patches the refresh implementation once, removes the
legacy moving-main wording, deduplicates the exact publication-baseline limitation,
and recomputes the recovery-index canonical digest.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFRESH = ROOT / "scripts/repository_preservation_refresh.py"
INDEX = ROOT / "api/recovery-index.json"

LEGACY_TREE_LIMITATION = (
    "The core repository capsule embeds every current Git-tracked byte but "
    "deliberately excludes production parent-history and tag objects so historical "
    "credentials are not republished; source commit/tag identities remain manifest "
    "metadata."
)
BASELINE_TREE_LIMITATION = (
    "The core repository capsule embeds every Git-tracked byte in the exact "
    "publication baseline named by its manifest, while deliberately excluding "
    "production parent-history and tag objects so historical credentials are not "
    "republished; source commit/tag identities remain manifest metadata."
)
QUALIFIED_LIMITATION = (
    "The core repository capsule and the separately published evidence and Chronicle "
    "NFT binary annex DOI records together preserve the exact Git-tracked publication "
    "baseline named by the core manifest and every custom asset; this does not assert "
    "byte equality with a later moving GitHub main."
)

OLD_FUNCTION = '''def qualified_limitation() -> str:
    return (
        "The core repository capsule and the separately published evidence and Chronicle "
        "NFT binary annex DOI records together preserve the exact Git-tracked publication "
        "baseline named by the core manifest and every custom asset; this does not "
        "assert byte equality with a later moving GitHub main."
    )
'''

NEW_FUNCTION = '''def baseline_tree_limitation() -> str:
    return (
        "The core repository capsule embeds every Git-tracked byte in the exact "
        "publication baseline named by its manifest, while deliberately excluding "
        "production parent-history and tag objects so historical credentials are not "
        "republished; source commit/tag identities remain manifest metadata."
    )


def qualified_limitation() -> str:
    return (
        "The core repository capsule and the separately published evidence and Chronicle "
        "NFT binary annex DOI records together preserve the exact Git-tracked publication "
        "baseline named by the core manifest and every custom asset; this does not "
        "assert byte equality with a later moving GitHub main."
    )


def normalize_limitations(value: object) -> list[str]:
    if not isinstance(value, list):
        raise SystemExit("recovery index limitations are invalid")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise SystemExit("recovery index limitation is not a string")
        if item == (
            "The core repository capsule embeds every current Git-tracked byte but "
            "deliberately excludes production parent-history and tag objects so historical "
            "credentials are not republished; source commit/tag identities remain manifest "
            "metadata."
        ):
            item = baseline_tree_limitation()
        if (
            "together preserve the current Git-tracked repository" in item
            or item == qualified_limitation()
        ):
            continue
        if item not in normalized:
            normalized.append(item)
    tree = baseline_tree_limitation()
    if tree not in normalized:
        normalized.append(tree)
    normalized.append(qualified_limitation())
    return normalized
'''

OLD_FILTER = '''    limitations = [
        item
        for item in limitations
        if not (
            isinstance(item, str)
            and "together preserve the current Git-tracked repository" in item
        )
    ]
    limitations.append(qualified_limitation())
    index["limitations"] = limitations
'''

NEW_FILTER = '''    index["limitations"] = normalize_limitations(limitations)
'''

OLD_VALIDATION = '''        if index.get("source_digest") != canonical_index_digest(index):
            raise SystemExit("recovery index source digest mismatch")
'''

NEW_VALIDATION = '''        if index.get("source_digest") != canonical_index_digest(index):
            raise SystemExit("recovery index source digest mismatch")
        limitations = index.get("limitations")
        if limitations != normalize_limitations(limitations):
            raise SystemExit("recovery index limitations are stale or duplicated")
'''


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def canonical_digest(value: dict[str, Any]) -> str:
    canonical = dict(value)
    canonical.pop("source_digest", None)
    raw = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def replace_required(text: str, old: str, new: str, *, expected_count: int) -> str:
    if new in text and old not in text:
        return text
    observed = text.count(old)
    if observed != expected_count:
        raise SystemExit(
            f"recovery-index repair anchor count mismatch: expected={expected_count} observed={observed}"
        )
    return text.replace(old, new)


def normalize_values(value: object) -> list[str]:
    if not isinstance(value, list):
        raise SystemExit("recovery index limitations are invalid")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise SystemExit("recovery index limitation is not a string")
        if item == LEGACY_TREE_LIMITATION:
            item = BASELINE_TREE_LIMITATION
        if (
            "together preserve the current Git-tracked repository" in item
            or item == QUALIFIED_LIMITATION
        ):
            continue
        if item not in result:
            result.append(item)
    if BASELINE_TREE_LIMITATION not in result:
        result.append(BASELINE_TREE_LIMITATION)
    result.append(QUALIFIED_LIMITATION)
    return result


def main() -> int:
    source = REFRESH.read_text(encoding="utf-8")
    source = replace_required(source, OLD_FUNCTION, NEW_FUNCTION, expected_count=1)
    source = replace_required(source, OLD_FILTER, NEW_FILTER, expected_count=2)
    source = replace_required(source, OLD_VALIDATION, NEW_VALIDATION, expected_count=1)
    compile(source, str(REFRESH), "exec")
    REFRESH.write_text(source, encoding="utf-8")

    index = read_json(INDEX)
    index["limitations"] = normalize_values(index.get("limitations"))
    index["source_digest"] = canonical_digest(index)
    write_json(INDEX, index)

    verified = read_json(INDEX)
    limitations = verified.get("limitations")
    if limitations != normalize_values(limitations):
        raise SystemExit("normalized recovery index is not idempotent")
    if verified.get("source_digest") != canonical_digest(verified):
        raise SystemExit("normalized recovery index digest mismatch")
    print("RECOVERY_INDEX_LIMITATIONS_NORMALIZED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
