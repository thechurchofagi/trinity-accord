#!/usr/bin/env python3
"""
check-v3plus-evidence-input-signed-coverage.py

Standalone pre-Claim-Gate or CI gate for V3+ evidence inputs.

Rules:
  - V0/V1/V2 inputs do not require the signed manifest gate.
  - V3+ inputs require signed_manifest_gate booleans.
  - V3+ hashes must have match=true, expected/computed SHA-256, expected_hash_source,
    and an approved expected_hash_authority_class.
  - Sensitive NFT / Chronicle / Covenant / Flaw hashes require a byte-verified
    target in SIGNED-MANIFEST-COVERAGE-AUDIT.json.
  - Hash-only coverage is allowed as preflight only, not as sensitive V3+ byte evidence.

Usage:
  python3 scripts/check-v3plus-evidence-input-signed-coverage.py evidence-input.json
  python3 scripts/check-v3plus-evidence-input-signed-coverage.py evidence-input.json --audit SIGNED-MANIFEST-COVERAGE-AUDIT.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

LEVELS = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]
SHA256_RE = re.compile(r"^[a-f0-9]{64}$", re.I)

SENSITIVE_TERMS = [
    "nft",
    "chronicle",
    "flaw",
    "covenant",
    "physical_anchor",
    "core_object_alpha",
]

ALLOWED_AUTHORITY_CLASSES = {
    "signed_authority_manifest_hash",
    "signed_digest_manifest_hash",
    "canonical_manifest_hash",
}


def level_index(level):
    try:
        return LEVELS.index(str(level).upper())
    except ValueError:
        return -1


def requested_level(obj):
    claims = obj.get("claims_requested_by_agent", []) or []
    text = " ".join(map(str, claims)) + " " + str(obj.get("protocol_level_claimed", ""))

    for lvl in reversed(LEVELS):
        if re.search(rf"\b{re.escape(lvl)}\b", text, flags=re.I):
            return lvl

    # Technical report with hashes is at least V3-intent if hashes are present.
    hashes = obj.get("evidence", {}).get("hashes", [])
    if hashes:
        return "V3"

    return "V0"


def is_v3plus(obj):
    return level_index(requested_level(obj)) >= level_index("V3")


def lower_json(obj):
    return json.dumps(obj, ensure_ascii=False).lower()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def valid_sha256(value):
    return bool(SHA256_RE.match(str(value or "").lower()))


def candidate_hashes_from_hash_entry(hobj):
    expected = str(hobj.get("expected", "")).lower()
    computed = str(hobj.get("computed", "")).lower()
    return [x for x in [expected, computed] if valid_sha256(x)]


def matching_target_results(candidate_hashes, audit):
    candidate_set = {str(h).lower() for h in candidate_hashes if valid_sha256(h)}
    matches = []
    for r in audit.get("target_results", []) or []:
        observed = str(
            r.get("sha256")
            or r.get("sha256_observed")
            or r.get("sha256_expected")
            or ""
        ).lower()
        if observed in candidate_set and r.get("covered_by_signed_manifest_chain") is True:
            matches.append(r)
    return matches


def hash_covered_by_audit(candidate_hashes, audit):
    return len(matching_target_results(candidate_hashes, audit)) > 0


def hash_byte_verified_by_audit(candidate_hashes, audit):
    for r in matching_target_results(candidate_hashes, audit):
        if r.get("byte_verified") is True:
            return True
    return False


def hash_is_coverage_only(candidate_hashes, audit):
    for r in matching_target_results(candidate_hashes, audit):
        if r.get("coverage_only") is True:
            return True
    return False


def is_sensitive_hash_entry(hobj):
    text = lower_json(hobj)
    return any(term in text for term in SENSITIVE_TERMS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence_input")
    ap.add_argument("--audit", default="SIGNED-MANIFEST-COVERAGE-AUDIT.json")
    ap.add_argument("--out", default="V3PLUS-SIGNED-COVERAGE-GATE.json")
    args = ap.parse_args()

    obj = load_json(args.evidence_input)
    result = {
        "schema": "trinityaccord.v3plus-signed-coverage-gate.v2",
        "evidence_input": args.evidence_input,
        "requested_level": requested_level(obj),
        "v3plus_intent": is_v3plus(obj),
        "pass": False,
        "blocking_failures": [],
        "warnings": [],
    }

    if not result["v3plus_intent"]:
        result["pass"] = True
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"PASS: not V3+ intent; wrote {args.out}")
        return 0

    audit_path = Path(args.audit)
    if not audit_path.exists():
        result["blocking_failures"].append(f"Missing signed manifest audit: {args.audit}")
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"FAIL: wrote {args.out}")
        return 1

    audit = load_json(audit_path)

    required_audit_bools = [
        "signed_manifest_coverage_pass",
        "btc_bip340_signature_verified",
        "legacy_eth_witness_verified",
        "digest_manifest_json_hash_match",
        "digest_manifest_csv_hash_match",
    ]

    for k in required_audit_bools:
        if audit.get(k) is not True:
            result["blocking_failures"].append(f"{args.audit}.{k} is not true")

    gate = obj.get("evidence", {}).get("signed_manifest_gate", {})
    if not isinstance(gate, dict):
        gate = {}

    required_gate_bools = [
        "btc_bip340_signature_verified",
        "legacy_eth_witness_verified",
        "authority_jcs_sha256_match",
        "signed_manifest_coverage_audit_pass",
    ]

    for k in required_gate_bools:
        if gate.get(k) is not True:
            result["blocking_failures"].append(f"evidence.signed_manifest_gate.{k} must be true for V3+")

    hashes = obj.get("evidence", {}).get("hashes", []) or []

    for i, hobj in enumerate(hashes):
        sensitive = is_sensitive_hash_entry(hobj)
        match = hobj.get("match") is True

        if not match:
            result["blocking_failures"].append(f"hash[{i}] match must be true for V3+")
            continue

        candidates = candidate_hashes_from_hash_entry(hobj)
        if not candidates:
            result["blocking_failures"].append(f"hash[{i}] has no valid SHA-256 in expected/computed")
            continue

        expected = str(hobj.get("expected", "")).lower()
        computed = str(hobj.get("computed", "")).lower()
        if valid_sha256(expected) and valid_sha256(computed) and expected != computed:
            result["blocking_failures"].append(f"hash[{i}] expected and computed SHA-256 differ")
            continue

        src = hobj.get("expected_hash_source")
        cls = hobj.get("expected_hash_authority_class")

        if not src:
            result["blocking_failures"].append(f"hash[{i}] missing expected_hash_source")

        if cls not in ALLOWED_AUTHORITY_CLASSES:
            result["blocking_failures"].append(
                f"hash[{i}] expected_hash_authority_class must be one of "
                f"{sorted(ALLOWED_AUTHORITY_CLASSES)}; got {cls}"
            )

        # General hashes may be accepted by declared source/class, because not every
        # general hash is listed as an explicit target_result.
        #
        # Sensitive hashes are stricter: they must correspond to an explicit target
        # in SIGNED-MANIFEST-COVERAGE-AUDIT.json, and that target must byte-verify.
        if sensitive:
            if not hash_covered_by_audit(candidates, audit):
                result["blocking_failures"].append(
                    f"hash[{i}] is sensitive NFT/Flaw/Covenant/Chronicle evidence "
                    f"but is not covered by signed manifest audit target_results"
                )
                continue

            if not hash_byte_verified_by_audit(candidates, audit):
                if hash_is_coverage_only(candidates, audit):
                    result["blocking_failures"].append(
                        f"hash[{i}] is sensitive evidence but matching target is coverage_only; "
                        f"coverage-only cannot support V3+ byte verification"
                    )
                else:
                    result["blocking_failures"].append(
                        f"hash[{i}] is sensitive evidence but matching target is not byte_verified; "
                        f"sha256-only coverage cannot support V3+ byte verification"
                    )

    result["pass"] = len(result["blocking_failures"]) == 0
    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(("PASS" if result["pass"] else "FAIL") + f": wrote {args.out}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
