"""Bounded implementation tests; not philosophical validation or peer review."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('editorial', ROOT / 'research/editorial-supplement/manage.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
DOI = '10.5281/zenodo.99999999'

class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.md = {'title':'Existing paper', 'version':'1.0', 'publication_date':'2026-09-15',
                   'creators':[{'name':'Liu, Hongju'}], 'description':'<p>Original abstract.</p>',
                   'related_identifiers':[{'identifier':'10.5281/zenodo.21699878','relation':'references','scheme':'doi'}],
                   'notes':'Earlier note', 'license':'cc-by-4.0', 'keywords':['old'], 'upload_type':'publication',
                   'publication_type':'preprint', 'doi':'10.5281/zenodo.22761411'}

    def test_metadata_update_does_not_mutate_input(self):
        before = copy.deepcopy(self.md)
        M.linked_metadata(self.md,DOI)
        self.assertEqual(self.md,before)

    def test_only_description_and_relations_change(self):
        out = M.linked_metadata(self.md,DOI)
        self.assertEqual({k:v for k,v in out.items() if k not in ('description','related_identifiers')},
                         {k:v for k,v in self.md.items() if k not in ('description','related_identifiers')})
        self.assertTrue(out['description'].startswith(self.md['description']))
        self.assertEqual(out['related_identifiers'][:-1],self.md['related_identifiers'])
        self.assertEqual(out['related_identifiers'][-1]['relation'],'isSupplementedBy')

    def test_link_updates_are_idempotent(self):
        once = M.linked_metadata(self.md,DOI)
        self.assertEqual(M.linked_metadata(once,DOI),once)

    def test_invalid_or_conflicting_link_rejected(self):
        for value in ('https://example.com','10.5281/zenodo.x',''):
            with self.assertRaises(ValueError): M.linked_metadata(self.md,value)
        once = M.linked_metadata(self.md,DOI)
        with self.assertRaises(RuntimeError): M.linked_metadata(once,'10.5281/zenodo.88888888')

    def test_paper_identity_and_creator_fail_closed(self):
        r = {'id':22761411,'metadata':self.md}
        M.validate_identity(r,22761411,'1.0')
        with self.assertRaises(RuntimeError): M.validate_identity(r,22830239,'1.0')
        with self.assertRaises(RuntimeError): M.validate_identity(r,22761411,'1.1')
        r['metadata'] = {**self.md,'creators':[{'name':'Unrelated, Person'}]}
        with self.assertRaises(RuntimeError): M.validate_identity(r,22761411,'1.0')

    def test_public_readback_checks_bytes(self):
        content = b'public record'
        class Fake:
            def download_public(self,url): return content
        record = {'files':[{'key':'file.txt','links':{'self':'https://zenodo.org/files/x'},
                           'checksum':'md5:' + hashlib.md5(content).hexdigest()}]}
        self.assertEqual(M.readback(Fake(),record)[0]['sha256'],hashlib.sha256(content).hexdigest())
        record['files'][0]['checksum'] = 'md5:' + '0'*32
        with self.assertRaises(RuntimeError): M.readback(Fake(),record)
        with self.assertRaises(RuntimeError): M.readback(Fake(),{'files':[]})

    @unittest.skipUnless(importlib.util.find_spec('markdown'), 'Renderer exercised in the dedicated publication workflow')
    def test_package_is_reproducible_and_contains_both_full_guides(self):
        sources = {p:('---\ntitle: Test\n---\n# Guide\n\n' + ('正文' if '-zh' in p else 'Full text') +
                      '\n\n' + '\n'.join('Paper DOI 10.5281/zenodo.'+str(r) for r,_ in M.PAPERS)).encode()
                   for p in M.SOURCES}
        with tempfile.TemporaryDirectory() as tmp, patch.object(M,'source_material',return_value=sources):
            batch = Path(tmp)
            with patch.object(M,'BATCH',batch), patch.object(M,'FILES',batch/'published'):
                first = M.build(DOI)
                self.assertEqual(first,M.build(DOI))
                self.assertEqual(len(first['files']),8)
                self.assertEqual(M.validate_assets(),first)
                manifest = json.loads((batch/'published/SOURCE-MANIFEST.json').read_text())
                self.assertEqual(manifest['new_research_paper_count'],0)
                for lang in ('en','zh'):
                    self.assertTrue((batch/'published'/f'critical-use-{lang}-v1.0.html').read_text().startswith('<!doctype html>'))
                (batch/'published/critical-use-en-v1.0.md').write_text('corrupted')
                with self.assertRaises(RuntimeError): M.validate_assets()
                with self.assertRaises(RuntimeError): M.build(DOI)

    def test_source_drift_is_rejected(self):
        with patch.object(M.subprocess,'check_output',return_value=b'wrong source'):
            with self.assertRaises(RuntimeError): M.source_material()

    def test_pending_or_completed_state_does_not_spend(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(M,'BATCH',Path(tmp)), patch.object(M.subprocess,'run') as paid:
            M.upload()
            for state in ('PENDING_BITCOIN','ARWEAVE_READBACK_PASS'):
                M.write(Path(tmp)/'status.json',{'state':state})
                M.upload()
            paid.assert_not_called()

    def test_unpublished_supplement_is_not_stamped(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(M,'BATCH',Path(tmp)), patch.object(M,'load_module') as load:
            M.preserve()
            load.assert_not_called()

    def test_no_paper_replacement_endpoint(self):
        code = (ROOT/'research/editorial-supplement/manage.py').read_text()
        self.assertNotIn('/actions/newversion',code)
        self.assertNotIn("'DELETE'",code)
        self.assertEqual(len({r for r,_ in M.PAPERS}),6)
        self.assertIn("env['ARWEAVE_MAX_TRANSACTION_REWARD_AR'] = '0.003'",code)

if __name__ == '__main__': unittest.main()
