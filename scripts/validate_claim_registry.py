#!/usr/bin/env python3
"""Validate api/claim-registry.json (TA-REDTEAM-2026-017).

Usage:
  python3 scripts/validate_claim_registry.py
  python3 scripts/validate_claim_registry.py --self-test
  python3 scripts/validate_claim_registry.py api/claim-registry.json
"""
import json
import hashlib
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "api" / "claim-registry.json"

REQUIRED_SCHEMA = "trinity-accord.claim-registry.v1"
REQUIRED_VERSION = "v1"

REQUIRED_CLAIM_IDS = {
    "bitcoin_originals_are_canonical",
    "github_pages_are_non_amending_mirror",
    "btc_signature_binds_authority_manifest",
    "eth_witness_is_secondary",
    "digest_manifest_covers_evidence_integrity",
    "release_pass_requires_corrections_index",
    "echo_records_do_not_count_as_attestation",
    "formal_attestation_requires_positive_gates",
    "notarized_evidence_is_not_formal_attestation",
    "recovery_is_clean_room_executable",
    "github_free_verifier_bundle_is_deferred",
    "nft_car_backups_are_recovery_mirrors_not_authority",
    "scarcity_claim_is_framing_not_proof",
}

ALLOWED_CURRENT_STATUSES = {
    "current", "historical_only", "superseded", "revoked", "invalidated", "deferred", "planned"
}
ALLOWED_TRACEABILITY_STATUSES = {
    "complete", "partial", "deferred", "missing"
}

FORBIDDEN_FIRSTNESS_PHRASES = [
    "proven first",
    "absolute first",
    "guaranteed first",
    "world's first",
    "unique in history",
]


def _stable_json(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _compute_source_digest(data: dict) -> str:
    """Compute source_digest: sha256 of canonical JSON with source_digest field omitted, truncated to 16 hex."""
    data_no_digest = {k: v for k, v in data.items() if k != "source_digest"}
    canonical = _stable_json(data_no_digest)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def validate(registry_path: str | Path) -> list[str]:
    """Validate claim-registry.json. Returns list of errors."""
    errors = []
    path = Path(registry_path)

    if not path.exists():
        errors.append(f"File not found: {path}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    # Schema field
    if data.get("schema") != REQUIRED_SCHEMA:
        errors.append(f"schema must be {REQUIRED_SCHEMA}, got: {data.get('schema')}")

    # Version
    if data.get("version") != REQUIRED_VERSION:
        errors.append(f"version must be {REQUIRED_VERSION}, got: {data.get('version')}")

    # source_digest
    stored_digest = data.get("source_digest")
    if not stored_digest:
        errors.append("source_digest is missing")
    else:
        expected = _compute_source_digest(data)
        if stored_digest != expected:
            errors.append(f"source_digest mismatch: stored={stored_digest}, expected={expected}")

    # non_amending_boundary
    if data.get("non_amending_boundary") is not True:
        errors.append("non_amending_boundary must be true")

    # canonical_authority
    if data.get("canonical_authority") != "Bitcoin Originals only":
        errors.append("canonical_authority must be 'Bitcoin Originals only'")

    # Required top-level fields
    for field in ["schema", "version", "source_digest_algorithm", "source_digest",
                   "non_amending_boundary", "canonical_authority", "purpose",
                   "claim_type_definitions", "claims", "limitations", "does_not_prove"]:
        if field not in data:
            errors.append(f"Missing required top-level field: {field}")

    # claim_type_definitions must have required types
    ctd = data.get("claim_type_definitions", {})
    for required_type in ["NOTARIZED_EVIDENCE_CLAIM", "SCARCITY_OR_FIRSTNESS_CLAIM"]:
        if required_type not in ctd:
            errors.append(f"claim_type_definitions missing required type: {required_type}")

    # Claims validation
    claims = data.get("claims", [])
    if not claims:
        errors.append("claims array is empty")

    claim_ids_seen = set()
    for i, claim in enumerate(claims):
        prefix = f"claims[{i}]"
        cid = claim.get("claim_id", f"<no-id-{i}>")

        # Required fields
        for field in ["claim_id", "claim_type", "claim_text", "public_surfaces", "source_files",
                       "evidence_files", "digest_or_hash_binding", "validators", "limitations",
                       "does_not_prove", "corrections_path", "current_status", "traceability_status"]:
            if field not in claim:
                errors.append(f"{prefix} ({cid}): missing required field '{field}'")

        # Unique claim_id
        if cid in claim_ids_seen:
            errors.append(f"Duplicate claim_id: {cid}")
        claim_ids_seen.add(cid)

        # Status values
        cs = claim.get("current_status")
        if cs and cs not in ALLOWED_CURRENT_STATUSES:
            errors.append(f"{prefix} ({cid}): invalid current_status '{cs}'")
        ts = claim.get("traceability_status")
        if ts and ts not in ALLOWED_TRACEABILITY_STATUSES:
            errors.append(f"{prefix} ({cid}): invalid traceability_status '{ts}'")

        # Limitations and does_not_prove non-empty (unless deferred/planned)
        if cs not in ("deferred", "planned"):
            if not claim.get("limitations"):
                errors.append(f"{prefix} ({cid}): limitations must be non-empty")
            if not claim.get("does_not_prove"):
                errors.append(f"{prefix} ({cid}): does_not_prove must be non-empty")

        # corrections_path
        if claim.get("corrections_path") != "api/corrections-index.json":
            errors.append(f"{prefix} ({cid}): corrections_path must be 'api/corrections-index.json'")

        # Validators non-empty unless deferred/planned
        if cs not in ("deferred", "planned") and ts not in ("deferred",):
            if not claim.get("validators"):
                errors.append(f"{prefix} ({cid}): validators must be non-empty unless deferred/planned")

        # Source files non-empty unless deferred/planned
        if cs not in ("deferred", "planned") and ts not in ("deferred",):
            if not claim.get("source_files"):
                errors.append(f"{prefix} ({cid}): source_files must be non-empty unless deferred/planned")

        # NOTARIZED_EVIDENCE_CLAIM checks
        if claim.get("claim_type") == "NOTARIZED_EVIDENCE_CLAIM":
            if claim.get("counts_as_independent_attestation") is not False:
                errors.append(f"{prefix} ({cid}): NOTARIZED_EVIDENCE_CLAIM must have counts_as_independent_attestation=false")
            if claim.get("formal_attestation_gate_required") is not True:
                errors.append(f"{prefix} ({cid}): NOTARIZED_EVIDENCE_CLAIM must have formal_attestation_gate_required=true")
            limits = " ".join(claim.get("limitations", [])).lower()
            if "formal independent attestation" not in limits:
                errors.append(f"{prefix} ({cid}): NOTARIZED_EVIDENCE_CLAIM limitations must mention 'formal independent attestation'")
            dnp = " ".join(claim.get("does_not_prove", [])).lower()
            if "formal independent verification" not in dnp:
                errors.append(f"{prefix} ({cid}): NOTARIZED_EVIDENCE_CLAIM does_not_prove must include 'formal independent verification'")

        # SCARCITY_OR_FIRSTNESS_CLAIM checks
        if claim.get("claim_type") == "SCARCITY_OR_FIRSTNESS_CLAIM":
            mb = claim.get("method_boundary")
            if not mb:
                errors.append(f"{prefix} ({cid}): SCARCITY_OR_FIRSTNESS_CLAIM must have method_boundary")
            else:
                if mb.get("status") != "bounded_framing_not_proof":
                    errors.append(f"{prefix} ({cid}): method_boundary.status must be 'bounded_framing_not_proof'")
                if not mb.get("limitations"):
                    errors.append(f"{prefix} ({cid}): method_boundary.limitations must be non-empty")

            # Check for forbidden firstness phrases in claim_text
            claim_text_lower = claim.get("claim_text", "").lower()
            for phrase in FORBIDDEN_FIRSTNESS_PHRASES:
                if phrase in claim_text_lower:
                    errors.append(f"{prefix} ({cid}): claim_text contains forbidden phrase '{phrase}'")

            # does_not_prove must include firstness-related entry
            dnp = " ".join(claim.get("does_not_prove", [])).lower()
            firstness_terms = ["firstness", "absolute first", "proven first", "uniqueness"]
            if not any(t in dnp for t in firstness_terms):
                errors.append(f"{prefix} ({cid}): SCARCITY_OR_FIRSTNESS_CLAIM does_not_prove must include firstness-related entry")

        # FORMAL_ATTESTATION_CLAIM checks
        if claim.get("claim_type") == "FORMAL_ATTESTATION_CLAIM":
            validators = claim.get("validators", [])
            has_gate_validator = any("validate_independent_attestation" in v for v in validators)
            if not has_gate_validator:
                errors.append(f"{prefix} ({cid}): FORMAL_ATTESTATION_CLAIM must reference validate_independent_attestation_index.py")

    # Check required claim IDs
    for required_id in REQUIRED_CLAIM_IDS:
        if required_id not in claim_ids_seen:
            errors.append(f"Missing required claim_id: {required_id}")

    # Top-level limitations and does_not_prove
    if not data.get("limitations"):
        errors.append("Top-level limitations must be non-empty")
    if not data.get("does_not_prove"):
        errors.append("Top-level does_not_prove must be non-empty")

    # Check referenced files exist (source_files, evidence_files, validators)
    for claim in claims:
        cid = claim.get("claim_id", "?")
        cs = claim.get("current_status", "current")
        ts = claim.get("traceability_status", "complete")
        if cs in ("deferred", "planned") or ts in ("deferred",):
            continue
        for sf in claim.get("source_files", []):
            if not (ROOT / sf).exists():
                errors.append(f"Claim {cid}: source_file not found: {sf}")
        for ef in claim.get("evidence_files", []):
            if not (ROOT / ef).exists():
                errors.append(f"Claim {cid}: evidence_file not found: {ef}")
        for v in claim.get("validators", []):
            if not (ROOT / v).exists():
                errors.append(f"Claim {cid}: validator not found: {v}")
        for ps in claim.get("public_surfaces", []):
            if ps.startswith("/") or ps.startswith("http"):
                continue
            if not (ROOT / ps).exists():
                errors.append(f"Claim {cid}: public_surface not found: {ps}")

    return errors


def self_test() -> bool:
    """Run self-test cases. Returns True if all pass."""
    passed = 0
    failed = 0

    def _make_valid_registry():
        """Return a minimal valid registry dict."""
        data = json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))
        return data

    def _test_case(name: str, registry: dict, expect_pass: bool, check_fn=None):
        nonlocal passed, failed
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(registry, f)
            f.flush()
            tmp_path = f.name
        try:
            errs = validate(tmp_path)
            actual_pass = len(errs) == 0
            if check_fn:
                actual_pass = actual_pass and check_fn(errs)
            if actual_pass == expect_pass:
                passed += 1
                print(f"  PASS: {name}")
            else:
                failed += 1
                print(f"  FAIL: {name} (expected {'pass' if expect_pass else 'fail'}, got {'pass' if actual_pass else 'fail'})")
                if errs:
                    for e in errs[:3]:
                        print(f"        {e}")
        finally:
            os.unlink(tmp_path)

    print("Self-test cases:")
    # 1. VALID registry accepted
    _test_case("VALID registry accepted", _make_valid_registry(), True)

    # 2. missing required claim id rejected
    reg = _make_valid_registry()
    reg["claims"] = [c for c in reg["claims"] if c["claim_id"] != "bitcoin_originals_are_canonical"]
    _test_case("missing required claim id rejected", reg, False)

    # 3. duplicate claim_id rejected
    reg = _make_valid_registry()
    dup = dict(reg["claims"][0])
    reg["claims"].append(dup)
    _test_case("duplicate claim_id rejected", reg, False)

    # 4. missing corrections_path rejected
    reg = _make_valid_registry()
    del reg["claims"][0]["corrections_path"]
    _test_case("missing corrections_path rejected", reg, False)

    # 5. missing limitations rejected
    reg = _make_valid_registry()
    reg["claims"][0]["limitations"] = []
    _test_case("missing limitations rejected", reg, False)

    # 6. missing does_not_prove rejected
    reg = _make_valid_registry()
    reg["claims"][0]["does_not_prove"] = []
    _test_case("missing does_not_prove rejected", reg, False)

    # 7. non_amending_boundary=false rejected
    reg = _make_valid_registry()
    reg["non_amending_boundary"] = False
    _test_case("non_amending_boundary=false rejected", reg, False)

    # 8. canonical_authority wrong rejected
    reg = _make_valid_registry()
    reg["canonical_authority"] = "wrong"
    _test_case("canonical_authority != Bitcoin Originals only rejected", reg, False)

    # 9. notarized evidence counts_as_independent_attestation=true rejected
    reg = _make_valid_registry()
    for c in reg["claims"]:
        if c["claim_id"] == "notarized_evidence_is_not_formal_attestation":
            c["counts_as_independent_attestation"] = True
    _test_case("notarized evidence counts_as_independent_attestation=true rejected", reg, False)

    # 10. notarized evidence missing formal_attestation_gate_required rejected
    reg = _make_valid_registry()
    for c in reg["claims"]:
        if c["claim_id"] == "notarized_evidence_is_not_formal_attestation":
            del c["formal_attestation_gate_required"]
    _test_case("notarized evidence missing formal_attestation_gate_required rejected", reg, False)

    # 11. scarcity claim missing method_boundary rejected
    reg = _make_valid_registry()
    for c in reg["claims"]:
        if c["claim_id"] == "scarcity_claim_is_framing_not_proof":
            del c["method_boundary"]
    _test_case("scarcity claim missing method_boundary rejected", reg, False)

    # 12. scarcity claim saying "proven first" rejected
    reg = _make_valid_registry()
    for c in reg["claims"]:
        if c["claim_id"] == "scarcity_claim_is_framing_not_proof":
            c["claim_text"] = "This is proven first in history."
    _test_case('scarcity claim saying "proven first" rejected', reg, False)

    # 13. source_digest mismatch rejected
    reg = _make_valid_registry()
    reg["source_digest"] = "0000000000000000"
    _test_case("source_digest mismatch rejected", reg, False)

    # 14. missing validator path rejected
    reg = _make_valid_registry()
    for c in reg["claims"]:
        if c["claim_id"] == "bitcoin_originals_are_canonical":
            c["validators"] = ["scripts/nonexistent_validator.py"]
    _test_case("missing validator path rejected", reg, False)

    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


def main():
    if "--self-test" in sys.argv:
        ok = self_test()
        if ok:
            print("\nSELF-TEST PASS")
        else:
            print("\nSELF-TEST FAIL")
            sys.exit(1)
        # Also validate actual file
        errs = validate(DEFAULT_REGISTRY)
        if errs:
            print("CLAIM_REGISTRY_VALIDATION_ERRORS:")
            for e in errs:
                print(f"  - {e}")
            sys.exit(1)
        print("CLAIM_REGISTRY_OK")
        return

    # Determine path
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        registry_path = sys.argv[1]
    else:
        registry_path = DEFAULT_REGISTRY

    errs = validate(registry_path)
    if errs:
        print(f"CLAIM_REGISTRY_VALIDATION_ERRORS ({len(errs)}):")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("CLAIM_REGISTRY_OK")


if __name__ == "__main__":
    main()
