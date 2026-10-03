"""Meaningful tests of linked-version identity and ambiguous-action guards."""
import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
import publication as p

class Fake:
    def __init__(self):
        self.calls=[];self.rid=23109999;self.has_draft=False;self.wrong=False
    def request(self,url,method='GET',data=None,**kw):
        self.calls.append((method,url))
        base={'title':p.TITLE,'version':'1.0','creators':[{'name':'Liu, Hongju'}],'notes':p.REPORT}
        if url==f'/deposit/depositions/{p.PREVIOUS_RECORD}' and method=='GET':
            return {'id':p.PREVIOUS_RECORD,'submitted':True,'metadata':base,'conceptrecid':'23103273',
                    'links':{'latest_draft':f'https://zenodo.org/api/deposit/depositions/{self.rid if self.has_draft else p.PREVIOUS_RECORD}'}}
        if method=='POST' and url.endswith('/actions/newversion'):
            self.has_draft=True
            return {'id':p.PREVIOUS_RECORD,'links':{'latest_draft':f'https://zenodo.org/api/deposit/depositions/{self.rid}'}}
        if url==f'/deposit/depositions/{self.rid}':
            if method=='PUT':self.version='1.1'
            base['version']=getattr(self,'version','1.0')
            if self.wrong:base['title']='Unrelated deposit'
            return {'id':self.rid,'submitted':False,'metadata':base,'conceptrecid':'23103273','doi':f'10.5281/zenodo.{self.rid}'}
        raise AssertionError((method,url))

class Guards(unittest.TestCase):
    def run_prepare(self,f,root):
        with patch.object(p,'ROOT',root),patch.object(p,'client',return_value=f),patch.object(p,'source_review'),patch.object(p,'persist'),patch.object(p,'build_package'):
            p.prepare()
    def test_first_action_then_reuse_same_reserved_descendant(self):
        with tempfile.TemporaryDirectory() as td:
            f=Fake();root=Path(td)
            self.run_prepare(f,root);self.run_prepare(f,root)
            self.assertEqual(sum(method=='POST' for method,url in f.calls),1)
            self.assertFalse(any(method!='GET' and url==f'/deposit/depositions/{p.PREVIOUS_RECORD}' for method,url in f.calls))
            self.assertEqual(json.loads((root/'deposit.json').read_text())['record_id'],f.rid)
    def test_uncertain_prior_action_is_not_repeated(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'create-intent.json').write_text('{}');f=Fake()
            with self.assertRaisesRegex(RuntimeError,'Uncertain prior'):self.run_prepare(f,root)
            self.assertFalse(any(method=='POST' for method,url in f.calls))
    def test_unrelated_linked_draft_is_not_adopted(self):
        with tempfile.TemporaryDirectory() as td:
            f=Fake();f.has_draft=True;f.wrong=True
            with self.assertRaisesRegex(RuntimeError,'Unexpected linked'):self.run_prepare(f,Path(td))
            self.assertFalse(any(method!='GET' for method,url in f.calls))
    def test_valid_linked_draft_with_unset_version_is_recovered(self):
        with tempfile.TemporaryDirectory() as td:
            f=Fake();f.has_draft=True;f.version=None
            self.run_prepare(f,Path(td))
            self.assertFalse(any(method=='POST' for method,url in f.calls))
            self.assertEqual(f.version,'1.1')
    def test_predecessor_is_protected_and_draft_url_is_strict(self):
        with self.assertRaises(RuntimeError):p.check_deposit({'id':p.PREVIOUS_RECORD})
        with self.assertRaises(RuntimeError):p.draft_id('https://example.org/api/deposit/depositions/23109999')
        with self.assertRaises(RuntimeError):p.draft_id('https://zenodo.org/api/deposit/depositions/23109999?other=1')

if __name__=='__main__':unittest.main()
