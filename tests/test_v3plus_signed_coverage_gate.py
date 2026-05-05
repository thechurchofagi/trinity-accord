#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check-v3plus-evidence-input-signed-coverage.py"

GOOD_HASH = "a" * 64
BAD_HASH = "b" * 64


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def base_audit(target_results=None):
    return {
        "signed_manifest_coverage_pass": True,
        "btc_bip340_signature_verified": True,
        "legacy_eth_witness_verified": True,
        "digest_manifest_json_hash_match": True,
        "digest_manifest_csv_hash_match": True,
        "target_results": target_results or [],
    }


def signed_gate():
    return {
        "btc_bip340_signature_verified": True,
        "legacy_eth_witness_verified": True,
        "authority_jcs_sha256_match": True,
        "signed_manifest_coverage_audit_pass": True,
    }


def base_input(level="V3", hashes=None, include_gate=True):
    evidence = {"hashes": hashes or []}
    if include_gate:
        evidence["signed_manifest_gate"] = signed_gate()

    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {},
        "provenance": {},
        "limitations": [],
        "claims_requested_by_agent": [level],
        "evidence": evidence,
    }


class V3PlusSignedCoverageGateTests(unittest.TestCase):
    def run_gate(self, evidence_input, audit_obj=None):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "evidence-input.json"
            audit = td / "audit.json"
            out = td / "out.json"

            write_json(inp, evidence_input)

            cmd = ["python3", str(SCRIPT), str(inp), "--out", str(out)]

            if audit_obj is not None:
                write_json(audit, audit_obj)
                cmd.extend(["--audit", str(audit)])

            r = subprocess.run(cmd, cwd=ROOT)
            result = json.loads(out.read_text()) if out.exists() else {}
            return r.returncode, result

    def test_v2_does_not_require_signed_gate(self):
        obj = {
            "schema": "trinityaccord.evidence-input.v1",
            "agent": {},
            "provenance": {},
            "limitations": [],
            "claims_requested_by_agent": ["V2"],
            "evidence": {},
        }
        rc, result = self.run_gate(obj)
        self.assertEqual(rc, 0)
        self.assertTrue(result["pass"])

    def test_v3_missing_signed_gate_fails(self):
        h = {
            "artifact": "general",
            "expected": GOOD_HASH,
            "computed": GOOD_HASH,
            "match": True,
            "expected_hash_source": "archive/evidence/digest-manifest.json",
            "expected_hash_authority_class": "signed_digest_manifest_hash",
        }
        obj = base_input(level="V3", hashes=[h], include_gate=False)
        rc, result = self.run_gate(obj, base_audit())
        self.assertNotEqual(rc, 0)
        self.assertFalse(result["pass"])
        self.assertTrue(any("signed_manifest_gate" in x for x in result["blocking_failures"]))

    def test_v3_general_hash_with_signed_gate_passes(self):
        h = {
            "artifact": "general",
            "expected": GOOD_HASH,
            "computed": GOOD_HASH,
            "match": True,
            "expected_hash_source": "archive/evidence/digest-manifest.json",
            "expected_hash_authority_class": "signed_digest_manifest_hash",
        }
        obj = base_input(level="V3", hashes=[h], include_gate=True)
        rc, result = self.run_gate(obj, base_audit())
        self.assertEqual(rc, 0)
        self.assertTrue(result["pass"])

    def test_v3_sensitive_hash_requires_target_coverage(self):
        h = {
            "artifact": "flaw archive",
            "artifact_class": "covenant_flaw",
            "expected": GOOD_HASH,
            "computed": GOOD_HASH,
            "match": True,
            "expected_hash_source": "archive/evidence/digest-manifest.json",
            "expected_hash_authority_class": "signed_digest_manifest_hash",
        }
        obj = base_input(level="V3", hashes=[h], include_gate=True)

        rc, result = self.run_gate(obj, base_audit(target_results=[]))
        self.assertNotEqual(rc, 0)
        self.assertFalse(result["pass"])
        self.assertTrue(any("not covered" in x for x in result["blocking_failures"]))

    def test_v3_sensitive_hash_requires_byte_verified_target(self):
        h = {
            "artifact": "flaw archive",
            "artifact_class": "covenant_flaw",
            "expected": GOOD_HASH,
            "computed": GOOD_HASH,
            "match": True,
            "expected_hash_source": "archive/evidence/digest-manifest.json",
            "expected_hash_authority_class": "signed_digest_manifest_hash",
        }
        obj = base_input(level="V3", hashes=[h], include_gate=True)

        audit = base_audit(target_results=[{
            "sha256": GOOD_HASH,
            "covered_by_signed_manifest_chain": True,
            "byte_verified": False,
            "coverage_only": False,
        }])

        rc, result = self.run_gate(obj, audit)
        self.assertNotEqual(rc, 0)
        self.assertFalse(result["pass"])
        self.assertTrue(any("not byte_verified" in x or "sha256-only" in x for x in result["blocking_failures"]))

    def test_v3_sensitive_coverage_only_cannot_support_byte_claim(self):
        h = {
            "artifact": "flaw archive",
            "artifact_class": "covenant_flaw",
            "expected": GOOD_HASH,
            "computed": GOOD_HASH,
            "match": True,
            "expected_hash_source": "archive/evidence/digest-manifest.json",
            "expected_hash_authority_class": "signed_digest_manifest_hash",
        }
        obj = base_input(level="V3", hashes=[h], include_gate=True)

        audit = base_audit(target_results=[{
            "sha256": GOOD_HASH,
            "covered_by_signed_manifest_chain": True,
            "byte_verified": False,
            "coverage_only": True,
        }])

        rc, result = self.run_gate(obj, audit)
        self.assertNotEqual(rc, 0)
        self.assertFalse(result["pass"])
        self.assertTrue(any("coverage-only" in x or "coverage_only" in x for x in result["blocking_failures"]))

    def test_v3_sensitive_byte_verified_target_passes(self):
        h = {
            "artifact": "flaw archive",
            "artifact_class": "covenant_flaw",
            "expected": GOOD_HASH,
            "computed": GOOD_HASH,
            "match": True,
            "expected_hash_source": "archive/evidence/digest-manifest.json",
            "expected_hash_authority_class": "signed_digest_manifest_hash",
        }
        obj = base_input(level="V3", hashes=[h], include_gate=True)

        audit = base_audit(target_results=[{
            "sha256": GOOD_HASH,
            "covered_by_signed_manifest_chain": True,
            "byte_verified": True,
            "coverage_only": False,
            "source_kind": "github_release_asset",
        }])

        rc, result = self.run_gate(obj, audit)
        self.assertEqual(rc, 0)
        self.assertTrue(result["pass"])

    def test_v3_expected_computed_mismatch_fails_even_if_match_true(self):
        h = {
            "artifact": "general",
            "expected": GOOD_HASH,
            "computed": BAD_HASH,
            "match": True,
            "expected_hash_source": "archive/evidence/digest-manifest.json",
            "expected_hash_authority_class": "signed_digest_manifest_hash",
        }
        obj = base_input(level="V3", hashes=[h], include_gate=True)
        rc, result = self.run_gate(obj, base_audit())
        self.assertNotEqual(rc, 0)
        self.assertFalse(result["pass"])
        self.assertTrue(any("expected and computed" in x for x in result["blocking_failures"]))

    def test_v3_hash_mismatch_fails(self):
        h = {
            "artifact": "flaw archive",
            "artifact_class": "covenant_flaw",
            "expected": GOOD_HASH,
            "computed": BAD_HASH,
            "match": False,
            "expected_hash_source": "archive/evidence/digest-manifest.json",
            "expected_hash_authority_class": "signed_digest_manifest_hash",
        }
        obj = base_input(level="V3", hashes=[h], include_gate=True)

        audit = base_audit(target_results=[{
            "sha256": GOOD_HASH,
            "covered_by_signed_manifest_chain": True,
            "byte_verified": True,
        }])

        rc, result = self.run_gate(obj, audit)
        self.assertNotEqual(rc, 0)
        self.assertFalse(result["pass"])
        self.assertTrue(any("match must be true" in x for x in result["blocking_failures"]))


if __name__ == "__main__":
    unittest.main()
