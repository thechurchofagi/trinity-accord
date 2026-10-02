#!/usr/bin/env python3
"""Offline regression tests for record protection and exact-package release gates."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("ta22_publication", Path(__file__).with_name("publication.py"))
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


class PublicationGuards(unittest.TestCase):
    def deposit(self):
        return {"id": 999999999, "metadata": dict(publication.metadata(),
                 prereserve_doi={"doi": "10.5281/zenodo.999999999"})}

    def test_existing_paper_ids_cannot_be_reused(self):
        for rid in publication.PROTECTED:
            dep = self.deposit()
            dep["id"] = rid
            dep["metadata"]["prereserve_doi"]["doi"] = f"10.5281/zenodo.{rid}"
            with self.subTest(rid=rid), self.assertRaises(RuntimeError):
                publication.check_deposit(dep)

    def test_record_identity_changes_are_rejected(self):
        good = self.deposit()
        self.assertEqual(publication.check_deposit(good), (999999999, "10.5281/zenodo.999999999"))
        for key, value in [("title", "Another study"), ("version", "2.0"),
                           ("creators", [{"name": "Another person"}]), ("notes", "TA-TR-2026-21")]:
            dep = copy.deepcopy(good)
            dep["metadata"][key] = value
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                publication.check_deposit(dep)
        with self.assertRaises(RuntimeError):
            publication.check_deposit(good, {"record_id": 999999998, "doi": "10.5281/zenodo.999999998"})

    def test_release_requires_matching_manifest_and_visual_review(self):
        expected = {"record_id": 999999999, "doi": "10.5281/zenodo.999999999"}
        sha = "f" * 64
        auth = dict(expected, report_number=publication.REPORT, version=publication.VERSION,
                    expected_manifest_sha256=sha, authorization="PUBLISH_EXACT_REVIEWED_PACKAGE")
        review = {"state": "EXACT_DOI_BOUND_PACKAGE_REVIEW_PASS", "expected_manifest_sha256": sha,
                  "pdf_visual_review_pass": True}
        with tempfile.TemporaryDirectory() as temporary, patch.object(publication, "ROOT", Path(temporary)):
            publication.save("PUBLISH-AUTHORIZATION.json", auth)
            publication.save("FINAL-REVIEW.json", review)
            publication.require_publication_review(expected, sha)
            with self.assertRaises(RuntimeError):
                publication.require_publication_review(expected, "e" * 64)
            publication.save("FINAL-REVIEW.json", dict(review, pdf_visual_review_pass=False))
            with self.assertRaises(RuntimeError):
                publication.require_publication_review(expected, sha)

    def test_changed_bytes_and_unexpected_files_block_release(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(publication, "ROOT", Path(temporary)), patch.object(publication, "source_review"):
            root = Path(temporary)
            (root / "published").mkdir()
            rows = []
            for name in sorted(publication.PUBLISHED_FILES):
                data = name.encode()
                (root / "published" / name).write_bytes(data)
                rows.append({"name": name, "bytes": len(data), "sha256": publication.digest(data)})
            manifest = {"report_number": publication.REPORT, "title": publication.TITLE,
                        "version": publication.VERSION, "record_id": 999999999,
                        "doi": "10.5281/zenodo.999999999", "file_count": len(rows), "files": rows}
            publication.save("EXPECTED-PUBLICATION.json", manifest)
            publication.validate_package()
            target = root / "published" / rows[0]["name"]
            original = target.read_bytes()
            target.write_bytes(original + b"changed")
            with self.assertRaises(RuntimeError):
                publication.validate_package()
            target.write_bytes(original)
            (root / "published" / "unexpected.txt").write_bytes(b"extra")
            with self.assertRaises(RuntimeError):
                publication.validate_package()


if __name__ == "__main__":
    unittest.main(verbosity=2)
