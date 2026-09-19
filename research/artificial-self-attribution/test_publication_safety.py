#!/usr/bin/env python3
"""Offline release-safety tests; these are not model or scientific experiments."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import publication_common as common
from publish_zenodo import draft_inventory


class PublicationSafetyTests(unittest.TestCase):
    def fixture(self, root):
        identity = {'record_id': 99999999, 'doi': '10.5281/zenodo.99999999', 'title': common.TITLE, 'report_number': common.REPORT, 'version': common.VERSION}
        (root / 'published').mkdir()
        rows = []
        for name in sorted(common.ALLOWED_FILES):
            data = ('offline fixture ' + name).encode()
            (root / 'published' / name).write_bytes(data)
            rows.append({'name': name, 'bytes': len(data), 'sha256': common.sha(data)})
        expected = dict(identity, file_count=14, files=rows)
        (root / 'EXPECTED-PUBLICATION.json').write_text(json.dumps(expected))
        (root / 'deposit.json').write_text(json.dumps(identity))
        (root / 'visual-review.json').write_text(json.dumps({'state': 'VISUAL_AND_CONTENT_REVIEW_PASS', 'expected_manifest_sha256': common.sha((root / 'EXPECTED-PUBLICATION.json').read_bytes())}))
        (root / 'format-checks.json').write_text(json.dumps({key: True for key in ('source_docx_pdf_text_equal', 'reference_lists_identical', 'valid_citation_metadata', 'pdf_text_extractable')}))
        return expected

    def test_accept_reviewed_inventory_and_reject_changed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = self.fixture(root)
            self.assertEqual(common.validate_local_package(root)[0], expected)
            (root / 'published' / 'citation.bib').write_text('unreviewed change')
            with self.assertRaisesRegex(RuntimeError, 'Unreviewed'):
                common.validate_local_package(root)

    def test_review_binds_exact_manifest_and_rejects_extra_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / 'EXPECTED-PUBLICATION.json').write_text((root / 'EXPECTED-PUBLICATION.json').read_text() + '\n')
            with self.assertRaisesRegex(RuntimeError, 'completed visual'):
                common.validate_local_package(root)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / 'published' / 'unrelated.txt').write_text('not reviewed')
            with self.assertRaisesRegex(RuntimeError, 'inventory'):
                common.validate_local_package(root)

    def test_previous_records_and_identity_mismatch_rejected(self):
        for record_id in common.PROTECTED:
            with self.assertRaises(RuntimeError):
                common.validate_record_id(record_id)
        for record_id in (True, 0, -1, '99999999'):
            with self.assertRaises(RuntimeError):
                common.validate_record_id(record_id)
        identity = {'record_id': 99999999, 'doi': '10.5281/zenodo.99999999', 'title': common.TITLE, 'report_number': common.REPORT, 'version': common.VERSION}
        self.assertEqual(common.validate_identity(identity), 99999999)
        changed = dict(identity, version='1.0')
        with self.assertRaises(RuntimeError):
            common.validate_identity(changed)

    def test_existing_record_search_and_remote_inventory_are_fail_closed(self):
        row = {'metadata': {'title': common.TITLE}}
        self.assertIs(common.select_existing([row]), row)
        self.assertIsNone(common.select_existing([]))
        with self.assertRaisesRegex(RuntimeError, 'Ambiguous'):
            common.select_existing([row, copy.deepcopy(row)])
        with self.assertRaises(RuntimeError):
            common.select_existing([{}] * 100)
        with self.assertRaisesRegex(RuntimeError, 'Unrelated'):
            draft_inventory([{'filename': 'unrelated.txt'}], common.ALLOWED_FILES)

    def test_abstract_boundary_and_public_url_guard(self):
        for heading in ('##', '###'):
            self.assertEqual(common.extract_abstract(f'{heading} Abstract\n\nThe bounded argument.\n\nKeywords: evidence\n\n## Body'), 'The bounded argument.')
        self.assertEqual(common.extract_abstract('## Abstract\n\nText.\n\n**Keywords:** evidence'), 'Text.')
        for text in ('No abstract', '### Abstract\n\ntext without boundary', '### Abstract\n\n## Body\n\nKeywords: bad'):
            with self.assertRaises(RuntimeError):
                common.extract_abstract(text)
        for url in ('http://zenodo.org/files/x', 'https://example.com/x', 'https://token@zenodo.org/x', 'https://zenodo.org/x?access_token=wrong'):
            with self.assertRaises(RuntimeError):
                common.check_public_url(url)
        self.assertEqual(common.check_public_url('https://zenodo.org/api/records/99999999/files/test/content'), 'https://zenodo.org/api/records/99999999/files/test/content')


if __name__ == '__main__':
    unittest.main()
