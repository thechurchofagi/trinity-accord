#!/usr/bin/env python3
"""Validate that required public API files have unified metadata fields.

Usage:
  python3 scripts/validate_public_api_metadata.py --self-test
  python3 scripts/validate_public_api_metadata.py
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from public_metadata_utils import canonical_json_digest

PUBLIC_API_REQUIRED = [
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

REQUIRED_FIELDS = [
    "schema",
    "version",
    "source_digest",
    "source_digest_algorithm",
    "non_amending_boundary",
    "limitations",
    "does_not_prove",
]

# Schema files are exempt from metadata requirements
SCHEMA_EXEMPT_PATTERN = re.compile(r"schema", re.I)

# Tiered API coverage
CORE_API_FULL_METADATA = set(PUBLIC_API_REQUIRED)

ROUTE_CONTEXT_STATUS_PATTERNS = [
    "agent-start",
    "agent-minimal-context",
    "agent-output-policy",
    "agent-task-router",
    "agent-first-contact",
    "agent-required-reading",
    "agent-entry-protocol",
    "agent-tasks",
    "context-load-map",
    "context-depth",
    "context-pack",
    "gateway-builder-route-map",
    "gateway-workflows",
    "gateway-artifact-custody",
    "guardian-registry",
    "guardian-active-listing-policy",
    "guardian-alliance",
    "public-home-status",
    "agent-submit-gateway",
    "agent-context-readiness",
    "external-agent-quickstart",
    "archive-readiness-policy",
]

# Intentionally exempt from schema identity enforcement (document reason).
LEGACY_PUBLIC_API_SCHEMA_IDENTITY_EXEMPT: set[str] = set()

# Evidence input examples are test fixtures/templates, not public API endpoints.
import os as _os
for _root, _dirs, _files in _os.walk(ROOT / "api" / "evidence-input-examples"):
    for _f in _files:
        if _f.endswith(".json"):
            _rel = str(Path(_root).relative_to(ROOT) / _f)
            LEGACY_PUBLIC_API_SCHEMA_IDENTITY_EXEMPT.add(_rel)


def sitemap_api_json_files() -> list[str]:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        return []
    tree = ET.parse(sitemap)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    out = []
    for loc_el in tree.findall(".//sm:loc", ns):
        loc = (loc_el.text or "").strip()
        parsed = urlparse(loc)
        if parsed.path.startswith("/api/") and parsed.path.endswith(".json"):
            rel = parsed.path.lstrip("/")
            out.append(rel)
    return sorted(set(out))


def is_schema_file(rel: str, data: dict) -> bool:
    name = Path(rel).name.lower()
    if "schema" in name:
        return True
    schema_value = str(data.get("$schema") or data.get("schema") or "").lower()
    return "json-schema" in schema_value or "schema" in name


def is_route_context_status_api(rel: str) -> bool:
    name = Path(rel).name
    return any(pat in name for pat in ROUTE_CONTEXT_STATUS_PATTERNS)


TIER_B_SCHEMA_IDENTITY_EXEMPT: set[str] = {
    # Keep empty if possible.
    # Add a file only with a reason and issue/PR reference.
}

def validate_minimal_public_api(rel: str, path: Path, data: dict) -> list[str]:
    errors = []

    if (
        rel not in TIER_B_SCHEMA_IDENTITY_EXEMPT
        and "schema" not in data
        and "$schema" not in data
    ):
        errors.append(f"{rel}: missing schema/$schema")

    schema_val = str(data.get("schema") or data.get("$schema") or "")
    has_embedded_version = bool(re.search(r"\.v\d+", schema_val))

    if "version" not in data and not is_schema_file(rel, data) and not has_embedded_version:
        errors.append(f"{rel}: missing version")

    return errors


def validate_file(path: Path) -> list[str]:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{path.name}: JSON parse error: {e}"]

    if not isinstance(data, dict):
        return [f"{path.name}: not a JSON object"]

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"{path.name}: missing required field '{field}'")

    # Validate field types
    if "version" in data and not data["version"]:
        errors.append(f"{path.name}: version is empty")

    if "source_digest" in data:
        digest = data["source_digest"]
        if not re.match(r"^[a-fA-F0-9]{16}$|^[a-fA-F0-9]{64}$", str(digest)):
            errors.append(f"{path.name}: source_digest must be 16 or 64 hex, got: {digest}")
        else:
            # Recompute and verify digest matches
            try:
                expected_full = canonical_json_digest(path, ignored_fields={"source_digest"})
                expected_16 = expected_full[:16]
                expected_64 = expected_full
                if str(digest) not in (expected_16, expected_64):
                    errors.append(f"{path.name}: source_digest mismatch: stored={digest}, expected={expected_16}")
            except Exception as e:
                errors.append(f"{path.name}: cannot recompute source_digest: {e}")

    if "source_digest_algorithm" in data:
        algo = data["source_digest_algorithm"]
        if "sha256" not in algo.lower():
            errors.append(f"{path.name}: source_digest_algorithm must include sha256")

    if "non_amending_boundary" in data:
        if data["non_amending_boundary"] is not True:
            # Check fallback
            if "canonical_authority" not in data or "Bitcoin" not in str(data.get("canonical_authority", "")):
                errors.append(f"{path.name}: non_amending_boundary must be true or have canonical_authority")

    if "limitations" in data:
        if not isinstance(data["limitations"], list) or len(data["limitations"]) == 0:
            errors.append(f"{path.name}: limitations must be non-empty list")

    if "does_not_prove" in data:
        if not isinstance(data["does_not_prove"], list) or len(data["does_not_prove"]) == 0:
            errors.append(f"{path.name}: does_not_prove must be non-empty list")

    return errors


def validate_all() -> list[str]:
    errors = []

    all_api = sitemap_api_json_files()
    required = sorted(set(PUBLIC_API_REQUIRED) | set(all_api))

    for rel in required:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: file not found")
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"{rel}: JSON parse error: {e}")
            continue

        if not isinstance(data, dict):
            errors.append(f"{rel}: not a JSON object")
            continue

        if rel in CORE_API_FULL_METADATA:
            errors.extend(validate_file(path))
        elif is_schema_file(rel, data):
            # Schemas must parse and identify themselves but do not need source_digest.
            if "schema" not in data and "$schema" not in data:
                errors.append(f"{rel}: schema file missing schema/$schema identity")
        elif is_route_context_status_api(rel):
            errors.extend(validate_minimal_public_api(rel, path, data))
        else:
            if rel not in LEGACY_PUBLIC_API_SCHEMA_IDENTITY_EXEMPT and "schema" not in data and "$schema" not in data:
                errors.append(f"{rel}: public API missing schema/$schema identity")

    return errors


def self_test():
    """Run self-test cases."""
    import tempfile

    def make_api(overrides=None):
        base = {
            "schema": "trinity-accord.test.v1",
            "version": "v1",
            "source_digest_algorithm": "sha256(canonical_json_without_source_digest)",
            "non_amending_boundary": True,
            "limitations": ["test limitation"],
            "does_not_prove": ["test"],
        }
        if overrides:
            base.update(overrides)
        return base

    def make_api_with_correct_digest(overrides=None):
        """Create API metadata with a correctly computed source_digest."""
        import tempfile as tf
        base = make_api()
        tmp = Path(tf.mktemp(suffix=".json"))
        tmp.write_text(json.dumps(base))
        digest = canonical_json_digest(tmp, ignored_fields={"source_digest"})
        tmp.unlink()
        base["source_digest"] = digest[:16]
        if overrides:
            base.update(overrides)
        return base

    def check(label, description, ok):
        status = "PASS" if ok else "FAIL"
        print(f"  {'✓' if ok else '✗'} {label}: {description}")
        return ok

    print("Public API metadata validator self-test")
    print("=" * 50)

    all_ok = True

    # Valid
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api_with_correct_digest()))
    errs = validate_file(p)
    all_ok &= check("META01", "valid metadata passes", len(errs) == 0)
    p.unlink()

    # Missing version
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api({"version": None})))
    errs = validate_file(p)
    # version=None means key exists but empty
    p.write_text(json.dumps(make_api()))
    d = json.loads(p.read_text())
    del d["version"]
    p.write_text(json.dumps(d))
    errs = validate_file(p)
    all_ok &= check("META02", "missing version rejected", any("version" in e for e in errs))
    p.unlink()

    # Missing source_digest
    p = Path(tempfile.mktemp(suffix=".json"))
    d = make_api_with_correct_digest()
    del d["source_digest"]
    p.write_text(json.dumps(d))
    errs = validate_file(p)
    all_ok &= check("META03", "missing source_digest rejected", any("source_digest" in e and "algorithm" not in e for e in errs))
    p.unlink()

    # Bad digest format
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api_with_correct_digest({"source_digest": "not-hex"})))
    errs = validate_file(p)
    all_ok &= check("META04", "bad digest format rejected", any("source_digest" in e for e in errs))
    p.unlink()

    # Digest mismatch
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api_with_correct_digest({"source_digest": "0000000000000000"})))
    errs = validate_file(p)
    all_ok &= check("META08", "digest mismatch rejected", any("mismatch" in e for e in errs))
    p.unlink()

    # Missing limitations
    p = Path(tempfile.mktemp(suffix=".json"))
    d = make_api()
    del d["limitations"]
    p.write_text(json.dumps(d))
    errs = validate_file(p)
    all_ok &= check("META05", "missing limitations rejected", any("limitations" in e for e in errs))
    p.unlink()

    # Missing does_not_prove
    p = Path(tempfile.mktemp(suffix=".json"))
    d = make_api()
    del d["does_not_prove"]
    p.write_text(json.dumps(d))
    errs = validate_file(p)
    all_ok &= check("META06", "missing does_not_prove rejected", any("does_not_prove" in e for e in errs))
    p.unlink()

    # non_amending_boundary false
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text(json.dumps(make_api({"non_amending_boundary": False})))
    errs = validate_file(p)
    all_ok &= check("META07", "non_amending_boundary=false rejected", any("non_amending" in e for e in errs))
    p.unlink()

    print()
    if all_ok:
        print("VALIDATE_PUBLIC_API_METADATA_SELF_TEST_OK")
    else:
        print("VALIDATE_PUBLIC_API_METADATA_SELF_TEST_FAIL")
        sys.exit(1)


def main():
    if "--self-test" in sys.argv:
        self_test()
        return

    errors = validate_all()
    if errors:
        print("FAIL: public API metadata validation errors:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("VALIDATE_PUBLIC_API_METADATA_OK")


if __name__ == "__main__":
    main()
