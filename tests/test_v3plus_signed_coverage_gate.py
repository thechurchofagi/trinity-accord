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

class V3PlusSignedCoverageGateTests(unittest.TestCase):
    def test_v2_does_not_require_signed_gate(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "v2.json"
            out = td / "out.json"
            write_json(inp, {
                "schema": "trinityaccord.evidence-input.v1",
                "agent": {},
                "provenance": {},
                "limitations": [],
                "claims_requested_by_agent": ["V2"],
                "evidence": {}
            })
            r = subprocess.run(["python3", str(SCRIPT), str(inp), "--out", str(out)], cwd=ROOT)
            self.assertEqual(r.returncode, 0)
            self.assertTrue(json.loads(out.read_text())["pass"])

    def test_v3_missing_signed_gate_fails(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "v3.json"
            audit = td / "audit.json"
            out = td / "out.json"
            write_json(audit, {
                "signed_manifest_coverage_pass": True,
                "btc_bip340_signature_verified": True,
                "legacy_eth_witness_verified": True,
                "digest_manifest_json_hash_match": True,
                "digest_manifest_csv_hash_match": True,
                "target_results": []
            })
            write_json(inp, {
                "schema": "trinityaccord.evidence-input.v1",
                "agent": {},
                "provenance": {},
                "limitations": [],
                "claims_requested_by_agent": ["V3"],
                "evidence": {
                    "hashes": [{
                        "artifact": "general",
                        "expected": GOOD_HASH,
                        "computed": GOOD_HASH,
                        "match": True,
                        "expected_hash_source": "archive/evidence/digest-manifest.json",
                        "expected_hash_authority_class": "signed_digest_manifest_hash"
                    }]
                }
            })
            r = subprocess.run(["python3", str(SCRIPT), str(inp), "--audit", str(audit), "--out", str(out)], cwd=ROOT)
            self.assertNotEqual(r.returncode, 0)

    def test_v3_sensitive_hash_requires_target_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "v3.json"
            audit = td / "audit.json"
            out = td / "out.json"
            write_json(audit, {
                "signed_manifest_coverage_pass": True,
                "btc_bip340_signature_verified": True,
                "legacy_eth_witness_verified": True,
                "digest_manifest_json_hash_match": True,
                "digest_manifest_csv_hash_match": True,
                "target_results": [{
                    "sha256": GOOD_HASH,
                    "covered_by_signed_manifest_chain": True
                }]
            })
            write_json(inp, {
                "schema": "trinityaccord.evidence-input.v1",
                "agent": {},
                "provenance": {},
                "limitations": [],
                "claims_requested_by_agent": ["V3"],
                "evidence": {
                    "signed_manifest_gate": {
                        "btc_bip340_signature_verified": True,
                        "legacy_eth_witness_verified": True,
                        "authority_jcs_sha256_match": True,
                        "signed_manifest_coverage_audit_pass": True
                    },
                    "hashes": [{
                        "artifact": "flaw archive",
                        "artifact_class": "covenant_flaw",
                        "expected": GOOD_HASH,
                        "computed": GOOD_HASH,
                        "match": True,
                        "expected_hash_source": "archive/evidence/digest-manifest.json",
                        "expected_hash_authority_class": "signed_digest_manifest_hash"
                    }]
                }
            })
            r = subprocess.run(["python3", str(SCRIPT), str(inp), "--audit", str(audit), "--out", str(out)], cwd=ROOT)
            self.assertEqual(r.returncode, 0)
            self.assertTrue(json.loads(out.read_text())["pass"])

            obj = json.loads(inp.read_text())
            obj["evidence"]["hashes"][0]["expected"] = BAD_HASH
            obj["evidence"]["hashes"][0]["computed"] = BAD_HASH
            write_json(inp, obj)
            r = subprocess.run(["python3", str(SCRIPT), str(inp), "--audit", str(audit), "--out", str(out)], cwd=ROOT)
            self.assertNotEqual(r.returncode, 0)

    def test_v3_sensitive_hash_only_required_must_fail(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            inp = td / "v3.json"
            audit = td / "audit.json"
            out = td / "out.json"
            write_json(audit, {
                "signed_manifest_coverage_pass": True,
                "btc_bip340_signature_verified": True,
                "legacy_eth_witness_verified": True,
                "digest_manifest_json_hash_match": True,
                "digest_manifest_csv_hash_match": True,
                "target_results": [{
                    "sha256": GOOD_HASH,
                    "covered_by_signed_manifest_chain": True,
                    "byte_verified": False,
                    "coverage_only": False
                }]
            })
            write_json(inp, {
                "schema": "trinityaccord.evidence-input.v1",
                "agent": {},
                "provenance": {},
                "limitations": [],
                "claims_requested_by_agent": ["V3"],
                "evidence": {
                    "signed_manifest_gate": {
                        "btc_bip340_signature_verified": True,
                        "legacy_eth_witness_verified": True,
                        "authority_jcs_sha256_match": True,
                        "signed_manifest_coverage_audit_pass": True
                    },
                    "hashes": [{
                        "artifact": "flaw archive",
                        "artifact_class": "covenant_flaw",
                        "expected": GOOD_HASH,
                        "computed": GOOD_HASH,
                        "match": True,
                        "expected_hash_source": "archive/evidence/digest-manifest.json",
                        "expected_hash_authority_class": "signed_digest_manifest_hash"
                    }]
                }
            })
            r = subprocess.run(["python3", str(SCRIPT), str(inp), "--audit", str(audit), "--out", str(out)], cwd=ROOT)
            self.assertEqual(r.returncode, 0)

    def test_coverage_only_is_not_byte_verification(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            audit = td / "audit.json"
            write_json(audit, {
                "signed_manifest_coverage_pass": True,
                "btc_bip340_signature_verified": True,
                "legacy_eth_witness_verified": True,
                "digest_manifest_json_hash_match": True,
                "digest_manifest_csv_hash_match": True,
                "target_results": [{
                    "sha256": GOOD_HASH,
                    "covered_by_signed_manifest_chain": True,
                    "byte_verified": False,
                    "coverage_only": True
                }]
            })
            data = json.loads(audit.read_text())
            self.assertTrue(data["target_results"][0]["coverage_only"])
            self.assertFalse(data["target_results"][0]["byte_verified"])

if __name__ == "__main__":
    unittest.main()
