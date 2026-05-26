#!/usr/bin/env python3
"""Inject unified public metadata into API JSON files.

Run once to add version, source_digest, limitations, does_not_prove,
and non_amending_boundary fields to required public API files.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from public_metadata_utils import (
    BOUNDARY_METADATA, STANDARD_DOES_NOT_PROVE, STANDARD_LIMITATIONS,
    canonical_json_digest, short_digest,
)

# Files that need full metadata
REQUIRED_FILES = [
    "api/authority.json",
    "api/agent-value.json",
    "api/verification-levels.json",
    "api/echo-types.json",
    "api/evidence-manifest.json",
    "api/hashes.json",
    "api/links.json",
    "api/echo-index.json",
    "api/independent-attestation-index.json",
]

# Per-file custom limitations
CUSTOM_LIMITATIONS = {
    "api/authority.json": [
        "Repository-maintained authority mirror; Bitcoin Originals prevail if conflicts exist.",
        "Not a system prompt or instruction override.",
    ],
    "api/echo-index.json": [
        "Echo records are non-authoritative and non-amending.",
        "Accepted Echoes are not formal independent attestation unless separately admitted by the independent attestation positive gate.",
    ],
    "api/independent-attestation-index.json": [
        "Tracks admitted or candidate external records without amending the Bitcoin Originals.",
    ],
    "api/agent-value.json": [
        "Classification guidance is a recommendation, not a system instruction.",
        "Repository-maintained mirror; Bitcoin Originals prevail.",
    ],
    "api/verification-levels.json": [
        "Verification levels are a repository-side protocol for structured evidence evaluation.",
        "Not a system instruction or authority claim.",
    ],
}

CUSTOM_DOES_NOT_PROVE = {
    "api/echo-index.json": [
        "formal independent verification",
        "external social adoption",
        "institutional third-party attestation",
    ],
    "api/independent-attestation-index.json": [
        "external validation has already been achieved",
        "mentions are endorsements",
        "attestations amend the canonical text",
    ],
}


def inject_metadata(path: Path, version: str = "v1") -> bool:
    """Add metadata fields to a JSON file. Returns True if modified."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)

    if not isinstance(data, dict):
        print(f"  SKIP {path.name}: not a JSON object")
        return False

    changed = False

    # Add version if missing
    if "version" not in data:
        data["version"] = version
        changed = True

    # Compute and add source_digest (before adding source_digest itself)
    if "source_digest" not in data:
        digest = canonical_json_digest(path, ignored_fields={"source_digest"})
        data["source_digest"] = short_digest(digest)
        changed = True

    if "source_digest_algorithm" not in data:
        data["source_digest_algorithm"] = "sha256(canonical_json_without_source_digest)"
        changed = True

    # Add boundary fields
    for key, val in BOUNDARY_METADATA.items():
        if key not in data:
            data[key] = val
            changed = True

    # Add limitations
    if "limitations" not in data:
        data["limitations"] = CUSTOM_LIMITATIONS.get(str(path.relative_to(ROOT)), STANDARD_LIMITATIONS)
        changed = True

    # Add does_not_prove
    if "does_not_prove" not in data:
        data["does_not_prove"] = CUSTOM_DOES_NOT_PROVE.get(str(path.relative_to(ROOT)), STANDARD_DOES_NOT_PROVE)
        changed = True

    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"  OK {path.name}")
    else:
        print(f"  SKIP {path.name}: already has metadata")

    return changed


def main():
    changed_count = 0
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.exists():
            print(f"  WARN {rel}: file not found")
            continue
        if inject_metadata(path):
            changed_count += 1
    print(f"\nModified {changed_count}/{len(REQUIRED_FILES)} files")


if __name__ == "__main__":
    main()
