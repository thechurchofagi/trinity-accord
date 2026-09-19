#!/usr/bin/env python3
"""Offline release-safety tests; these are not model or scientific experiments."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import publication_common as common
import prepare_zenodo as prepare
from publish_zenodo import check_doi_resolution, draft_inventory, resolver_matches_record


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
        (root / 'format-checks.json').write_text(json.dumps({key: True for key in common.FORMAT_GATES}))
        return expected

    def test_exact_fourteen_assets_and_guide_names(self):
        self.assertEqual(len(common.ALLOWED_FILES), 14)
        self.assertEqual(sum('-zh-guide-' in name for name in common.ALLOWED_FILES), 4)
        self.assertFalse(any('-zh-v' in name for name in common.ALLOWED_FILES))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = self.fixture(root)
            for row in expected['files']:
                row['name'] = row['name'].replace('-zh-guide-', '-zh-')
            (root / 'EXPECTED-PUBLICATION.json').write_text(json.dumps(expected))
            (root / 'visual-review.json').write_text(json.dumps({
                'state': 'VISUAL_AND_CONTENT_REVIEW_PASS',
                'expected_manifest_sha256': common.sha((root / 'EXPECTED-PUBLICATION.json').read_bytes())}))
            with self.assertRaisesRegex(RuntimeError, 'exact fourteen'):
                common.validate_local_package(root)

    def test_every_format_gate_is_required_and_truthy_strings_do_not_pass(self):
        for field in common.FORMAT_GATES:
            for bad_value in (False, 'true', 1, None):
                with self.subTest(field=field, value=bad_value), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    self.fixture(root)
                    formats = {key: True for key in common.FORMAT_GATES}
                    formats[field] = bad_value
                    (root / 'format-checks.json').write_text(json.dumps(formats))
                    with self.assertRaisesRegex(RuntimeError, 'Required real format check'):
                        common.validate_local_package(root)

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
        self.assertIn(22842789, common.PROTECTED)
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

    def test_reservation_must_match_the_reviewed_identity_and_creator(self):
        identity = {'record_id': 99999999, 'doi': '10.5281/zenodo.99999999',
                    'title': common.TITLE, 'report_number': common.REPORT, 'version': common.VERSION}
        deposit = {'id': 99999999, 'metadata': {'title': common.TITLE, 'version': common.VERSION,
                   'creators': [{'name': 'Liu, Hongju'}], 'prereserve_doi': {'doi': identity['doi']}}}
        self.assertEqual(common.check_deposit(deposit, identity), (99999999, identity['doi']))
        for key, value in (('title', 'Other paper'), ('version', '1.0'),
                           ('creators', [{'name': 'Other author'}])):
            changed = copy.deepcopy(deposit)
            changed['metadata'][key] = value
            with self.subTest(field=key), self.assertRaises(RuntimeError):
                common.check_deposit(changed, identity)
        with self.assertRaises(RuntimeError):
            common.check_deposit(deposit, dict(identity, record_id=99999998))

    def test_unresolved_creation_intent_blocks_another_post(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'create-intent.json').write_text('{}')
            client = Mock()
            previous = {'id':common.PREVIOUS_RECORD,'submitted':True,'conceptrecid':'22844927',
                'metadata':{'title':common.TITLE,'version':'1.1','creators':[{'name':'Liu, Hongju'}]}}
            with patch.object(prepare, 'ROOT', root), patch.object(prepare, 'client', return_value=client), \
                    patch.object(prepare, 'read', side_effect=[previous, []]), patch.object(prepare, 'persist_states') as persist:
                with self.assertRaisesRegex(RuntimeError, 'Unresolved creation intent'):
                    prepare.run()
            client.request.assert_not_called()
            persist.assert_not_called()

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

    def test_doi_resolution_must_reach_exact_public_record(self):
        self.assertTrue(resolver_matches_record(200, 'https://zenodo.org/records/99999999', 99999999))
        self.assertTrue(resolver_matches_record(200, 'https://zenodo.org/record/99999999/', 99999999))
        for status, url in ((404, 'https://zenodo.org/records/99999999'),
                            (200, 'https://zenodo.org/records/22842789'),
                            (200, 'http://zenodo.org/records/99999999'),
                            (200, 'https://other.example/records/99999999'),
                            (200, 'https://user@zenodo.org/records/99999999'),
                            (200, 'https://zenodo.org/records/99999999?download=1')):
            with self.subTest(url=url, status=status):
                self.assertFalse(resolver_matches_record(status, url, 99999999))
        with patch('publish_zenodo.urllib.request.urlopen', side_effect=TimeoutError), \
                patch('publish_zenodo.time.sleep'):
            result = check_doi_resolution('10.5281/zenodo.99999999', 99999999)
        self.assertIs(result['matches_record'], False)
        self.assertEqual(result['state'], 'RESOLVER_CHECK_UNAVAILABLE')

    def test_verified_client_blob_is_unchanged(self):
        import hashlib
        data = (common.REPO / 'research/reading-trinity-accord/publish_zenodo.py').read_bytes()
        self.assertEqual(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
                         common.CLIENT_BLOB)

    def test_new_version_cannot_target_prior_or_unrelated_record(self):
        draft = {'id':99999999,'conceptrecid':'22844927','submitted':False,
                 'metadata':{'title':common.TITLE,'version':'1.1','creators':[{'name':'Liu, Hongju'}]}}
        self.assertEqual(prepare.validate_descendant(draft,'22844927'),99999999)
        for field,value in [('id',common.PREVIOUS_RECORD),('conceptrecid','99999888')]:
            bad=copy.deepcopy(draft);bad[field]=value
            with self.assertRaises(RuntimeError):prepare.validate_descendant(bad,'22844927')
        for field,value in [('version','2.0'),('title','Different paper'),('creators',[{'name':'Other author'}])]:
            bad=copy.deepcopy(draft);bad['metadata'][field]=value
            with self.assertRaises(RuntimeError):prepare.validate_descendant(bad,'22844927')
        bad=copy.deepcopy(draft);bad['submitted']=True
        with self.assertRaises(RuntimeError):prepare.validate_descendant(bad,'22844927')

    def test_latest_draft_link_must_be_exact_zenodo_route(self):
        self.assertEqual(prepare.draft_id('https://zenodo.org/api/deposit/depositions/99999999'),99999999)
        for url in ['http://zenodo.org/api/deposit/depositions/99999999','https://example.com/api/deposit/depositions/99999999',
                    'https://zenodo.org/api/deposit/depositions/99999999?access_token=x','https://user@zenodo.org/api/deposit/depositions/99999999',
                    'https://zenodo.org/api/records/99999999']:
            with self.assertRaises(RuntimeError):prepare.draft_id(url)


if __name__ == '__main__':
    unittest.main()
