import importlib.util
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "upload_harvard_epoch_ii", ROOT / "scripts" / "upload_harvard_epoch_ii.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class HarvardEpochIIUploadContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = ROOT / "preservation" / "epoch-ii" / "frozen" / "DATASET-MANIFEST.json"
        cls.sums_path = ROOT / "preservation" / "epoch-ii" / "frozen" / "HARVARD-EPOCH-II-SHA256SUMS"
        cls.manifest = MODULE.validate_manifest(cls.manifest_path, cls.sums_path)

    def test_exact_frozen_identity(self):
        self.assertEqual(self.manifest["source_git_commit_sha"], MODULE.SOURCE_SHA)
        self.assertEqual(self.manifest["candidate_identity_sha256"], MODULE.CANDIDATE_ID)
        self.assertEqual(self.manifest["layout_identity_sha256"], MODULE.LAYOUT_ID)
        self.assertEqual(self.manifest["planned_harvard_file_count"], 419)
        self.assertEqual(self.manifest["total_bytes"], 23_107_006_729)

    def test_exact_source_kind_counts(self):
        rows = self.manifest["files"]
        counts = {kind: sum(row["source_kind"] == kind for row in rows) for kind in {
            "repository_file", "public_github_release_asset", "verified_candidate_file"
        }}
        self.assertEqual(counts, {
            "repository_file": 206,
            "public_github_release_asset": 190,
            "verified_candidate_file": 21,
        })

    def test_release_shards_partition_exactly(self):
        rows = sorted(
            [row for row in self.manifest["files"] if row["source_kind"] == "public_github_release_asset"],
            key=lambda row: MODULE.file_key(row["directory_label"], row["filename"]),
        )
        shards = [[row for index, row in enumerate(rows) if index % 8 == shard] for shard in range(8)]
        flattened = [MODULE.file_key(row["directory_label"], row["filename"]) for shard in shards for row in shard]
        self.assertEqual(len(flattened), 190)
        self.assertEqual(len(flattened), len(set(flattened)))

    def test_required_public_families_are_complete(self):
        self.assertEqual(self.manifest["polygon_base_finality_files"], 26)
        self.assertEqual(self.manifest["polygon_base_finality_bytes"], 17_551_241_826)
        self.assertEqual(self.manifest["encrypted_delayed_access_files"], 48)
        self.assertEqual(self.manifest["encrypted_delayed_access_bytes"], 2_798_199_225)
        self.assertTrue(self.manifest["all_files_publicly_accessible"])

    def test_old_doi_is_read_only_constant(self):
        source = (ROOT / "scripts" / "upload_harvard_epoch_ii.py").read_text(encoding="utf-8")
        self.assertNotIn("api/dataverses/harvard/datasets", source)
        self.assertNotIn("/actions/:publish", source)
        self.assertNotIn("returnToAuthor", source)
        self.assertNotIn("/destroy", source)

    def test_s3_tagging_header_follows_signed_headers(self):
        tagged = MODULE.s3_upload_headers(
            "https://bucket.s3.amazonaws.com/object?X-Amz-SignedHeaders=host%3Bx-amz-tagging",
            123,
        )
        self.assertEqual(tagged["Content-Length"], "123")
        self.assertEqual(tagged["x-amz-tagging"], "dv-state=temp")
        untagged = MODULE.s3_upload_headers(
            "https://bucket.s3.amazonaws.com/object?X-Amz-SignedHeaders=host",
            456,
        )
        self.assertNotIn("x-amz-tagging", untagged)
        self.assertEqual(untagged["Content-Length"], "456")


if __name__ == "__main__":
    unittest.main()
