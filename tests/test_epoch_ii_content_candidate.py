import base64
import importlib.util
import hashlib
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "epoch_ii_content", ROOT / "scripts/build_epoch_ii_content_candidate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

VERIFY_SPEC = importlib.util.spec_from_file_location(
    "verify_epoch_ii_content", ROOT / "scripts/verify_epoch_ii_content_candidate.py"
)
VERIFY = importlib.util.module_from_spec(VERIFY_SPEC)
assert VERIFY_SPEC.loader
VERIFY_SPEC.loader.exec_module(VERIFY)


class EpochIIContentCandidateTests(unittest.TestCase):
    def test_scope_selects_research_payload_and_only_small_finality_receipts(self):
        rows = [
            {"family": "evidence_or_content", "size_bytes": 10},
            {"family": "encrypted_witness_ciphertext", "size_bytes": 11},
            {"family": "presentation_current", "size_bytes": 12},
            {"family": "research_context", "size_bytes": 13},
            {"family": "sidechain_finality", "size_bytes": 4_999_999},
            {"family": "sidechain_finality", "size_bytes": 5_000_000},
            {"family": "bitcoin_operational_checkpoint", "size_bytes": 1},
            {"family": "presentation_history", "size_bytes": 1},
        ]
        selected = MODULE.selected_release_rows(rows)
        self.assertEqual(len(selected), 5)

    def test_every_finality_file_is_required_for_institutional_copy(self):
        rows = [
            {
                "family": "sidechain_finality",
                "release_id": 1,
                "release_tag": "finality-v1",
                "filename": "part-0000",
                "size_bytes": 943_718_400,
                "declared_sha256": "d" * 64,
                "source_locator": "https://github.com/thechurchofagi/trinity-accord/releases/download/finality-v1/part-0000",
            },
            {
                "family": "sidechain_finality",
                "release_id": 1,
                "release_tag": "finality-v1",
                "filename": "receipt.json",
                "size_bytes": 100,
                "declared_sha256": "e" * 64,
                "source_locator": "https://github.com/thechurchofagi/trinity-accord/releases/download/finality-v1/receipt.json",
            },
        ]
        report = MODULE.full_finality_dependency(rows)
        self.assertEqual(report["logical_assets"], 2)
        self.assertEqual(report["logical_bytes"], 943_718_500)
        self.assertEqual(report["institutional_copy_requirement"], "copy_every_public_file_byte_for_byte")

    def test_path_traversal_and_absolute_archive_members_are_rejected(self):
        for value in ("../secret", "a/../../secret", "/absolute", "a\\..\\secret"):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                MODULE.safe_member(value)

    def test_car_v1_root_cid_is_decoded_from_dag_cbor_link(self):
        cid = bytes([1, 0x55, 0x12, 0x20]) + bytes(range(32))
        link = b"\xd8\x2a\x58" + bytes([len(cid) + 1]) + b"\x00" + cid
        header = b"\xa2\x65roots\x81" + link + b"\x67version\x01"
        car = bytes([len(header)]) + header
        expected = "b" + base64.b32encode(cid).decode("ascii").lower().rstrip("=")
        self.assertEqual(MODULE.car_root_cid(car), expected)

    def test_historical_commitment_becomes_member_match_only_on_hash_and_size(self):
        historical = {
            "rows": [
                {"declared_sha256": "a" * 64, "size_bytes": 7, "capture": "commitment_only", "matching_public_asset_metadata": []},
                {"declared_sha256": "a" * 64, "size_bytes": 8, "capture": "commitment_only", "matching_public_asset_metadata": []},
            ]
        }
        members = [{"sha256": "a" * 64, "bytes": 7, "logical_path": "bundle!one"}]
        report = MODULE.historical_crosscheck(historical, members)
        self.assertEqual(report["summary"]["selected_archive_member_bytes_match"], 1)
        self.assertEqual(report["summary"]["public_historical_commitment_unresolved"], 1)

    def test_nested_nonpublic_path_preserves_historical_label_only(self):
        historical = {
            "rows": [
                {
                    "declared_sha256": "c" * 64,
                    "size_bytes": 9,
                    "capture": "commitment_only",
                    "historical_nonpublic_label": False,
                    "historical_path": "E:\\瑕疵\\未公开\\Snap_004.jpg",
                    "matching_public_asset_metadata": [],
                }
            ]
        }
        report = MODULE.historical_crosscheck(historical, [])
        self.assertEqual(report["summary"]["historical_nonpublic_label_commitment"], 1)
        self.assertNotIn("public_historical_commitment_unresolved", report["summary"])

    def test_publication_decision_supersedes_label_without_claiming_bytes(self):
        historical = {
            "rows": [
                {
                    "declared_sha256": "c" * 64,
                    "size_bytes": 9,
                    "historical_path": "E:\\瑕疵\\未公开\\Snap_004.jpg",
                    "content_resolution": "historical_nonpublic_label_commitment",
                },
                {
                    "declared_sha256": "d" * 64,
                    "size_bytes": 10,
                    "historical_path": "E:\\指令.txt",
                    "content_resolution": "public_historical_commitment_unresolved",
                },
            ]
        }
        canonical = sorted(
            [
                {
                    "declared_sha256": row["declared_sha256"],
                    "historical_path": row["historical_path"],
                    "size_bytes": row["size_bytes"],
                }
                for row in historical["rows"]
            ],
            key=lambda row: (
                row["declared_sha256"], row["size_bytes"], row["historical_path"]
            ),
        )
        digest = hashlib.sha256(
            json.dumps(
                canonical,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        decision = {
            "decision": {"public_access_authorized": True},
            "bound_historical_rows": {
                "combined_rows": 2,
                "distinct_sha256_and_size_identities": 2,
                "logical_bytes_including_duplicate_commitments": 19,
                "canonical_rows_sha256": digest,
            },
        }
        report = MODULE.historical_publication_scope(historical, decision)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["public_if_exact_bytes_are_recovered_rows"], 2)
        self.assertEqual(report["currently_uploadable_rows"], 0)
        self.assertEqual(report["privacy_excluded_rows"], 0)
        self.assertEqual(report["unresolved_scope_decisions"], 0)
        self.assertTrue(
            all(
                row["current_byte_status"]
                == "commitment_only_exact_bytes_not_recovered"
                for row in report["rows"]
            )
        )

    def test_encrypted_witness_layer_is_complete_public_ciphertext(self):
        index = json.loads(
            (ROOT / "archive/encrypted-witness-archives.v1.json").read_text()
        )
        selected = []
        for item in index["archives"].values():
            state = json.loads((ROOT / item["state_record"]).read_text())
            for name, identity in state["source_inventory"].items():
                selected.append(
                    {
                        "family": "encrypted_witness_ciphertext",
                        "release_tag": item["github_release_tag"],
                        "filename": name,
                        "size_bytes": identity["bytes"],
                        "declared_sha256": identity["sha256"],
                    }
                )
        report = MODULE.verify_encrypted_witness_archives(ROOT, selected)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["archive_count"], 3)
        self.assertEqual(report["logical_files"], 48)
        self.assertEqual(report["logical_bytes"], 2_798_199_225)
        self.assertEqual(report["unique_sha256_objects"], 45)
        self.assertFalse(report["plaintext_public_now"])
        self.assertTrue(report["future_computational_decryption_intended"])

    def test_physical_match_requires_both_hash_and_size(self):
        physical = {"files": [{"declared_sha256": "b" * 64, "size_bytes": 4, "capture": "locator_only"}]}
        wrong = [{"sha256": "b" * 64, "bytes": 5, "logical_path": "bundle!wrong"}]
        self.assertEqual(MODULE.physical_crosscheck(physical, wrong)["status"], "incomplete")

    def test_media_car_root_difference_is_an_audit_boundary(self):
        source = (ROOT / "scripts/build_epoch_ii_content_candidate.py").read_text()
        self.assertIn("media_car_root_differs_from_manifest_parent_or_root_cid", source)
        self.assertIn("only metadata roots", source)

    def test_cold_restore_logical_path_rejects_backslashes(self):
        with self.assertRaises(SystemExit):
            VERIFY.safe_relative("release\\..\\escape")

    def test_atomic_source_restore_residue_is_removed_before_sealing(self):
        with tempfile.TemporaryDirectory() as value:
            output = pathlib.Path(value)
            residue = output / ".source-cold-restore.partial-test"
            residue.mkdir()
            (residue / "unsealed-byte").write_text("not candidate data")
            MODULE.cleanup_source_restore_residue(output)
            self.assertFalse(residue.exists())


if __name__ == "__main__":
    unittest.main()
