#!/usr/bin/env python3
"""
check-v3plus-evidence-input-signed-coverage.py

Standalone pre-Claim-Gate or CI gate for V3+ evidence inputs.

It intentionally does not rewrite existing claim_gate.py. This reduces the risk
of breaking current V0/V1/V2/legacy behavior. Once this gate is green, a later
PR may integrate the same checks directly into claim_gate.py.

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

def hash_covered_by_audit(h, audit):
    h = str(h or "").lower()
    if not SHA256_RE.match(h):
        return False
    for r in audit.get("target_results", []):
        if str(r.get("sha256", "")).lower() == h and r.get("covered_by_signed_manifest_chain") is True:
            return True
    # Also allow coverage_index_sample only for diagnostics; not full index.
    # Full index is intentionally not required in audit output to avoid huge files.
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence_input")
    ap.add_argument("--audit", default="SIGNED-MANIFEST-COVERAGE-AUDIT.json")
    ap.add_argument("--out", default="V3PLUS-SIGNED-COVERAGE-GATE.json")
    args = ap.parse_args()

    obj = load_json(args.evidence_input)
    result = {
        "schema": "trinityaccord.v3plus-signed-coverage-gate.v1",
        "evidence_input": args.evidence_input,
        "requested_level": requested_level(obj),
        "v3plus_intent": is_v3plus(obj),
        "pass": False,
        "blocking_failures": [],
        "warnings": []
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
        text = lower_json(hobj)
        category_sensitive = any(x in text for x in [
            "nft", "chronicle", "flaw", "covenant", "physical_anchor", "core_object_alpha"
        ])
        expected = str(hobj.get("expected", "")).lower()
        computed = str(hobj.get("computed", "")).lower()
        match = hobj.get("match") is True

        if not match:
            result["blocking_failures"].append(f"hash[{i}] match must be true for V3+")
            continue

        candidate_hashes = [x for x in [expected, computed] if SHA256_RE.match(x)]
        if not candidate_hashes:
            result["blocking_failures"].append(f"hash[{i}] has no valid SHA-256")
            continue

        # For NFT / flaw / covenant evidence, require explicit target coverage in audit target_results.
        if category_sensitive:
            if not any(hash_covered_by_audit(x, audit) for x in candidate_hashes):
                result["blocking_failures"].append(
                    f"hash[{i}] is NFT/Flaw/Covenant sensitive but is not covered by signed manifest audit target_results"
                )

        cls = hobj.get("expected_hash_authority_class")
        src = hobj.get("expected_hash_source")
        if not src:
            result["blocking_failures"].append(f"hash[{i}] missing expected_hash_source")
        if cls not in ("signed_authority_manifest_hash", "signed_digest_manifest_hash", "canonical_manifest_hash"):
            result["blocking_failures"].append(
                f"hash[{i}] expected_hash_authority_class must be signed_authority_manifest_hash, signed_digest_manifest_hash, or canonical_manifest_hash; got {cls}"
            )

    result["pass"] = len(result["blocking_failures"]) == 0
    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(("PASS" if result["pass"] else "FAIL") + f": wrote {args.out}")
    return 0 if result["pass"] else 1

if __name__ == "__main__":
    sys.exit(main())
