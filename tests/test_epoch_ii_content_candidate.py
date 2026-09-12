import base64
import importlib.util
import pathlib
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

    def test_nested_nonpublic_path_is_intentionally_restricted(self):
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
        self.assertEqual(report["summary"]["intentionally_restricted_commitment"], 1)
        self.assertNotIn("public_historical_commitment_unresolved", report["summary"])

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


if __name__ == "__main__":
    unittest.main()
