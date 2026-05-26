#!/usr/bin/env python3
"""Any api/ JSON file that declares source_digest must have a correct recomputed value.

This is a broad sweep: it catches Core, Tier B, and any other API file
that includes source_digest, regardless of tier classification.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from public_metadata_utils import canonical_json_digest

SKIP_DIRS = {
    "evidence-input-examples",
    "context-packs",
}

SKIP_FILES = set()


def api_json_files() -> list[Path]:
    """Collect all api/**/*.json, skipping fixture/example directories."""
    out = []
    for p in sorted((ROOT / "api").rglob("*.json")):
        rel = p.relative_to(ROOT / "api")
        if rel.parts[0] in SKIP_DIRS:
            continue
        if str(Path("api") / rel) in SKIP_FILES:
            continue
        out.append(p)
    return out


def main() -> None:
    errors: list[str] = []
    checked = 0

    for path in api_json_files():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        if "source_digest" not in data:
            continue

        # Only verify files that use the standard canonical_json algorithm.
        algo = str(data.get("source_digest_algorithm", ""))
        if "canonical_json" not in algo and "sha256" not in algo.lower():
            continue

        checked += 1
        digest = str(data["source_digest"])

        # Format check: 16 or 64 hex
        if not re.match(r"^[a-fA-F0-9]{16}$|^[a-fA-F0-9]{64}$", digest):
            errors.append(
                f"{path.relative_to(ROOT)}: source_digest must be 16 or 64 hex, got: {digest}"
            )
            continue

        # Recompute
        try:
            expected_full = canonical_json_digest(path, ignored_fields={"source_digest"})
        except Exception as e:
            errors.append(f"{path.relative_to(ROOT)}: cannot recompute source_digest: {e}")
            continue

        expected_16 = expected_full[:16]
        expected_64 = expected_full

        if digest not in (expected_16, expected_64):
            errors.append(
                f"{path.relative_to(ROOT)}: source_digest mismatch: "
                f"stored={digest}, expected={expected_16}"
            )

        # Algorithm check (if present)
        algo = data.get("source_digest_algorithm", "")
        if algo and "sha256" not in algo.lower():
            errors.append(
                f"{path.relative_to(ROOT)}: source_digest_algorithm must include sha256, got: {algo}"
            )

    if errors:
        print(f"FAIL: source_digest verification errors ({checked} files checked):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"PASS: all {checked} api/ files with source_digest verified correct")


if __name__ == "__main__":
    main()
