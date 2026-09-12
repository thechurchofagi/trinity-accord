import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "harvard_epoch_ii_layout", ROOT / "scripts/build_harvard_epoch_ii_layout.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class HarvardEpochIILayoutTests(unittest.TestCase):
    def test_terms_are_complete_and_bound_to_draft_metadata(self):
        metadata = json.loads(
            (ROOT / "preservation/epoch-ii/HARVARD-DRAFT-METADATA.json").read_text()
        )
        terms = ROOT / metadata["license"]["terms_of_use_file"]
        digest = hashlib.sha256(terms.read_bytes()).hexdigest()
        self.assertGreater(terms.stat().st_size, 1000)
        self.assertFalse(metadata["license"]["terms_of_use_empty"])
        self.assertEqual(digest, metadata["license"]["terms_of_use_sha256"])
        self.assertFalse(metadata["publication_controls"]["old_doi_mutation_allowed"])
        self.assertFalse(
            metadata["publication_controls"]["automatic_resubmission_allowed"]
        )

    def test_researcher_layer_exposes_three_originals_and_175_texts(self):
        rows = MODULE.researcher_files(ROOT)
        paths = {path for path, _ in rows}
        nft_texts = [
            path
            for path, _ in rows
            if path.startswith("nft-text-descriptions/0x")
        ]
        self.assertEqual(len(nft_texts), 175)
        for number in ("97631551", "98369145", "98387475"):
            self.assertTrue(
                any(number in path and "canonical-originals" in path for path in paths)
            )
            self.assertTrue(any(path.endswith(f"raw/{number}.txt") for path in paths))

    def test_layout_keeps_full_finality_and_delayed_access_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate = pathlib.Path(temp)
            documents = {
                "CONTENT-CANDIDATE.json": {
                    "source_git_commit_sha": "a" * 40,
                    "candidate_identity_sha256": "b" * 64,
                },
                "HISTORICAL-PUBLICATION-SCOPE-RESOLUTION.json": {
                    "status": "pass",
                    "unresolved_scope_decisions": 0,
                },
                "ENCRYPTED-DELAYED-ACCESS-VERIFICATION.json": {
                    "status": "pass",
                    "logical_files": 48,
                    "logical_bytes": 2_798_199_225,
                },
                "SELECTED-RELEASE-ASSETS.json": [],
                "FULL-FINALITY-INSTITUTIONAL-COPY-MANIFEST.json": {
                    "institutional_copy_requirement": "copy_every_public_file_byte_for_byte",
                    "logical_bytes": 11,
                    "files": [
                        {
                            "filename": "part-0000",
                            "release_tag": "finality-v1",
                            "bytes": 11,
                            "sha256": "c" * 64,
                            "source_locator": "https://example.invalid/part-0000",
                        }
                    ],
                },
            }
            for name, value in documents.items():
                (candidate / name).write_text(json.dumps(value))
            capsule = candidate / "source-capsule"
            capsule.mkdir()
            (capsule / "README.txt").write_text("recovery")
            report = MODULE.build(ROOT, candidate)
            self.assertEqual(report["polygon_base_finality_files"], 1)
            self.assertEqual(report["polygon_base_finality_bytes"], 11)
            self.assertEqual(report["encrypted_delayed_access_files"], 48)
            self.assertEqual(report["historical_scope_decisions_unresolved"], 0)
            self.assertTrue(report["all_files_within_per_file_limit"])
            self.assertFalse(report["harvard_dataset_created_or_mutated"])
            self.assertFalse(report["automatic_submit_or_resubmit_allowed"])


if __name__ == "__main__":
    unittest.main()
