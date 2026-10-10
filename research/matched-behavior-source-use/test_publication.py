#!/usr/bin/env python3
"""Offline tests for consequential SCU release gates; no network or credentials."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

spec=importlib.util.spec_from_file_location("scu_publication",Path(__file__).with_name("publication.py"))
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class ReleaseGates(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.original=p.ROOT
        p.ROOT=self.root
        for name in p.INPUTS:
            (self.root/name).parent.mkdir(parents=True,exist_ok=True)
            (self.root/name).write_text("frozen "+name)
        (self.root/"source-main.md").write_text("# Paper\nDOI: "+p.PLACEHOLDER+"\n# Abstract\n\nConditional theory.\n\n**Keywords:** test\n")
        p.save("create-intent.json",{"reservation_token":"test-release-identity","source_inputs":p.input_hashes()})

    def tearDown(self):
        p.ROOT=self.original
        self.tmp.cleanup()

    def package(self):
        self.rid=99999991
        self.doi=f"10.5281/zenodo.{self.rid}"
        p.save("deposit.json",{"record_id":self.rid,"doi":self.doi})
        folder=self.root/"published"
        folder.mkdir()
        for name in p.FILES:
            (folder/name).write_bytes(("fixture "+name).encode())
        (folder/p.MD_NAME).write_text((self.root/"source-main.md").read_text().replace(p.PLACEHOLDER,self.doi))
        (folder/"SHA256SUMS.txt").write_text("".join(f"{p.sha((folder/n).read_bytes())}  {n}\n" for n in sorted(p.FILES-{"SHA256SUMS.txt"})))
        rows=[{"name":n,"bytes":(folder/n).stat().st_size,"sha256":p.sha((folder/n).read_bytes())} for n in sorted(p.FILES)]
        self.expected={"report_number":p.REPORT,"title":p.TITLE,"version":p.VERSION,"record_id":self.rid,"doi":self.doi,"file_count":len(rows),"files":rows,"source_inputs":p.input_hashes()}
        p.save("EXPECTED-PUBLICATION.json",self.expected)
        digest=p.sha((self.root/"EXPECTED-PUBLICATION.json").read_bytes())
        pdf=next(r for r in rows if r["name"]==p.PDF_NAME)["sha256"]
        p.save("visual-review.json",{"state":"VISUAL_REVIEW_PASS","expected_manifest_sha256":digest,"pdf_sha256":pdf})
        p.save("PUBLISH-AUTHORIZATION.json",{"authorization":"PUBLISH_EXACT_REVIEWED_PACKAGE","report_number":p.REPORT,"version":p.VERSION,"record_id":self.rid,"doi":self.doi,"expected_manifest_sha256":digest,"pdf_sha256":pdf})
        return digest

    def deposit(self,submitted=False):
        return {"id":self.rid,"doi":self.doi,"submitted":submitted,"metadata":{"title":p.TITLE,"version":p.VERSION,"creators":[{"name":"Liu, Hongju"}],"notes":"SCU release identity: test-release-identity"},"links":{"bucket":"https://zenodo.org/api/files/test-bucket"}}

    def test_exact_package_and_visual_authorization(self):
        digest=self.package()
        e,h=p.validate_local_package()
        self.assertEqual(h,digest)
        p.validate_authorization(e,h)
        a=p.load("PUBLISH-AUTHORIZATION.json")
        a["expected_manifest_sha256"]="0"*64
        p.save("PUBLISH-AUTHORIZATION.json",a)
        with self.assertRaises(RuntimeError): p.validate_authorization(e,h)
        review=p.load("visual-review.json")
        review["pdf_sha256"]="1"*64
        p.save("visual-review.json",review)
        with self.assertRaises(RuntimeError): p.validate_authorization(e,h)

    def test_byte_manifest_and_source_mutations_fail(self):
        self.package()
        original=(self.root/"published"/p.PDF_NAME).read_bytes()
        (self.root/"published"/p.PDF_NAME).write_bytes(original+b"changed")
        with self.assertRaises(RuntimeError): p.validate_local_package()
        (self.root/"published"/p.PDF_NAME).write_bytes(original)
        (self.root/"source-main.md").write_text("altered source")
        with self.assertRaises(RuntimeError): p.validate_local_package()

    def test_missing_duplicate_and_extra_inventory_fail(self):
        self.package()
        e=p.load("EXPECTED-PUBLICATION.json")
        e["files"][-1]=e["files"][0]
        p.save("EXPECTED-PUBLICATION.json",e)
        with self.assertRaises(RuntimeError): p.validate_local_package()
        with self.assertRaises(RuntimeError): p.remote_files([{"key":"foreign.pdf"}],p.FILES)

    def test_record_identity_and_protected_records(self):
        self.package()
        p.check_deposit(self.deposit(),self.expected)
        for rid in (True,"99999991",-1,23131575,23030320):
            with self.assertRaises(RuntimeError): p.validate_id(rid)
        other=self.deposit()
        other["id"]=99999992
        with self.assertRaises(RuntimeError): p.check_deposit(other,self.expected)
        other=self.deposit()
        other["metadata"]["notes"]="Foreign reservation"
        with self.assertRaises(RuntimeError): p.check_deposit(other,self.expected)

    def test_only_zenodo_https_and_no_redirects(self):
        self.assertEqual(p.check_url("https://zenodo.org/api/records/99"),"https://zenodo.org/api/records/99")
        for url in ("http://zenodo.org/api/x","https://evil.test/api/x","https://zenodo.org.evil.test/api/x","https://token@zenodo.org/api/x","https://zenodo.org:444/api/x"):
            with self.assertRaises(RuntimeError): p.check_url(url)
        with self.assertRaises(RuntimeError): p.NoRedirect().redirect_request(None,None,302,"",{},"https://evil.test")

    def test_uncertain_creation_is_never_posted_twice(self):
        (self.root/"create-intent.json").unlink()
        class Fake:
            posts=0
            def request(self,path,method="GET",data=None,**kwargs):
                if method=="POST":
                    self.posts+=1
                    raise urllib.error.URLError("simulated uncertain create")
                return []
        z=Fake()
        with patch.object(p,"client",return_value=z),patch.object(p,"persist"):
            with self.assertRaises(urllib.error.URLError): p.prepare()
            with self.assertRaises(RuntimeError): p.prepare()
        self.assertEqual(z.posts,1)
        self.assertTrue((self.root/"create-intent.json").exists())

    def test_uncertain_publish_is_never_posted_twice(self):
        self.package()
        outer=self
        class Fake:
            posts=0
            uploaded={}
            def request(self,path,method="GET",data=None,**kwargs):
                if method=="POST":
                    self.posts+=1
                    raise urllib.error.URLError("simulated uncertain publish")
                if method=="PUT":
                    name=path.rsplit("/",1)[1]
                    self.uploaded[name]={"filename":name,"checksum":"md5:"+hashlib.md5(data).hexdigest(),"filesize":len(data)}
                    return {}
                if path.endswith("/files"): return list(self.uploaded.values())
                return outer.deposit()
        z=Fake()
        with patch.object(p,"client",return_value=z),patch.object(p,"persist"):
            with self.assertRaises(urllib.error.URLError): p.publish()
            with self.assertRaises(RuntimeError): p.publish()
        self.assertEqual(z.posts,1)
        self.assertTrue((self.root/"publication-intent.json").exists())

    def test_already_published_resumes_only_anonymous_readback(self):
        self.package()
        outer=self
        class Fake:
            requests=[]
            def request(self,path,method="GET",data=None,authenticated=True,**kwargs):
                self.requests.append((path,method,authenticated))
                if method!="GET": raise AssertionError("Mutation during published readback")
                record=outer.deposit(True)
                if path.startswith("/records/"):
                    record["files"]=[{"key":r["name"],"links":{"self":"https://zenodo.org/api/records/99999991/files/"+r["name"]}} for r in outer.expected["files"]]
                return record
        z=Fake()
        with patch.object(p,"client",return_value=z),patch.object(p,"persist"),patch.object(p,"download_public",side_effect=lambda url:(self.root/"published"/url.rsplit("/",1)[1]).read_bytes()):
            p.publish()
        receipt=p.load("publication-record.json")
        self.assertTrue(receipt["submitted"] and receipt["public_file_readback_pass"])
        self.assertFalse(receipt["public_readback_authenticated"])
        self.assertEqual(len(receipt["files"]),len(p.FILES))
        self.assertTrue(any(path.startswith("/records/") and auth is False for path,_,auth in z.requests))


    def test_normalized_title_other_version_and_subtitle_block_creation(self):
        (self.root/"create-intent.json").unlink()
        variants = [
            (p.TITLE, "1.0.0", ""),
            (p.TITLE.upper(), p.VERSION, ""),
            ("  Matched   Behavior & Source—Use  ", p.VERSION, ""),
            (p.TITLE + ": Exact intervention protocols", p.VERSION, ""),
            ("Different display title", p.VERSION, p.REPORT + "; version 1.0.0"),
        ]
        for title,version,notes in variants:
            with self.subTest(title=title, version=version):
                class Fake:
                    posts=0
                    def request(self,path,method="GET",**kwargs):
                        if method!="GET":
                            self.posts+=1
                            raise AssertionError("Creation despite suspected duplicate")
                        return [{"id":99999991,"metadata":{"title":title,"version":version,"notes":notes}}]
                z=Fake()
                with patch.object(p,"client",return_value=z),patch.object(p,"persist"):
                    with self.assertRaises(RuntimeError): p.prepare()
                self.assertEqual(z.posts,0)
                self.assertFalse((self.root/"create-intent.json").exists())

    def test_later_page_same_marker_recovers_without_post(self):
        self.package()
        (self.root/"deposit.json").unlink()
        outer=self
        class Fake:
            pages=[]
            def request(self,path,method="GET",**kwargs):
                if method!="GET": raise AssertionError("Recovery must not POST")
                query=p.urllib.parse.parse_qs(p.urllib.parse.urlsplit(path).query)
                self.pages.append(query)
                page=int(query["page"][0])
                if page==1:
                    return [{"id":i+1000,"metadata":{"title":"Unrelated "+str(i),"version":"1"}} for i in range(p.DEPOSIT_PAGE_SIZE)]
                if page==2: return [outer.deposit()]
                raise AssertionError("Unexpected page")
        z=Fake()
        with patch.object(p,"client",return_value=z),patch.object(p,"persist"):
            p.prepare()
        self.assertEqual(p.load("deposit.json")["record_id"],self.rid)
        self.assertEqual(len(z.pages),2)
        self.assertTrue(all(q["all_versions"]==["true"] and "status" not in q for q in z.pages))

    def test_exact_record_without_marker_cannot_be_adopted(self):
        self.package()
        (self.root/"deposit.json").unlink()
        wrong=self.deposit()
        wrong["metadata"]["notes"]="Foreign reservation"
        class Fake:
            def request(self,path,method="GET",**kwargs):
                if method!="GET": raise AssertionError("Foreign draft must not mutate")
                return [wrong]
        with patch.object(p,"client",return_value=Fake()),patch.object(p,"persist"):
            with self.assertRaises(RuntimeError): p.prepare()
        self.assertFalse((self.root/"deposit.json").exists())

    def test_incomplete_or_malformed_listing_never_allows_creation(self):
        (self.root/"create-intent.json").unlink()
        for kind in ("full", "duplicate", "malformed"):
            with self.subTest(kind=kind):
                class Fake:
                    calls=0
                    def request(self,path,method="GET",**kwargs):
                        if method!="GET": raise AssertionError("Incomplete search must not POST")
                        self.calls+=1
                        if kind=="malformed": return {"hits":[]}
                        offset=self.calls*1000 if kind=="full" else 0
                        return [{"id":offset+i+1,"metadata":{"title":"Unrelated","version":"1"}} for i in range(p.DEPOSIT_PAGE_SIZE)]
                z=Fake()
                with patch.object(p,"client",return_value=z),patch.object(p,"persist"),patch.object(p,"MAX_DEPOSIT_PAGES",2):
                    with self.assertRaises(RuntimeError): p.prepare()
                self.assertFalse((self.root/"create-intent.json").exists())

    def test_checked_out_commit_is_read_from_git_not_trigger_environment(self):
        commit="a"*40
        with patch.dict(p.os.environ,{"GITHUB_SHA":"b"*40}),patch.object(p.subprocess,"check_output",return_value=commit+"\n") as get:
            self.assertEqual(p.checked_out_commit(),commit)
        self.assertEqual(get.call_args.args[0],["git","rev-parse","--verify","HEAD^{commit}"])
        with patch.object(p.subprocess,"check_output",return_value="invalid\n"):
            with self.assertRaises(RuntimeError): p.checked_out_commit()

    def test_creation_checkpoint_failure_blocks_post_and_records_actual_head(self):
        (self.root/"create-intent.json").unlink()
        class Fake:
            posts=0
            def request(self,path,method="GET",**kwargs):
                if method=="POST":
                    self.posts+=1
                    raise AssertionError("Failed checkpoint must prevent POST")
                return []
        z=Fake()
        with patch.object(p,"client",return_value=z),patch.object(p,"persist",side_effect=RuntimeError("checkpoint failure")),patch.object(p,"checked_out_commit",return_value="a"*40),patch.dict(p.os.environ,{"GITHUB_SHA":"b"*40}):
            with self.assertRaises(RuntimeError): p.prepare()
        self.assertEqual(z.posts,0)
        intent=p.load("create-intent.json")
        self.assertEqual(intent["source_commit"],"a"*40)
        self.assertEqual(intent["workflow_trigger_commit"],"b"*40)

    def test_publish_checkpoint_failure_blocks_post(self):
        self.package()
        outer=self
        class Fake:
            posts=0
            def request(self,path,method="GET",**kwargs):
                if method!="GET":
                    self.posts+=method=="POST"
                    raise AssertionError("Already-uploaded files need no mutation")
                if path.endswith("/files"):
                    return [{"filename":r["name"],"checksum":"md5:"+hashlib.md5((outer.root/"published"/r["name"]).read_bytes()).hexdigest(),"filesize":r["bytes"]} for r in outer.expected["files"]]
                return outer.deposit()
        z=Fake()
        with patch.object(p,"client",return_value=z),patch.object(p,"persist",side_effect=RuntimeError("checkpoint failure")):
            with self.assertRaises(RuntimeError): p.publish()
        self.assertEqual(z.posts,0)
        self.assertTrue((self.root/"publication-intent.json").exists())

    def test_manifest_change_during_upload_blocks_publish(self):
        self.package()
        outer=self
        class Fake:
            posts=0
            uploaded={}
            changed=False
            def request(self,path,method="GET",data=None,**kwargs):
                if method=="POST":
                    self.posts+=1
                    raise AssertionError("Changed manifest must not be published")
                if method=="PUT":
                    name=path.rsplit("/",1)[1]
                    self.uploaded[name]={"filename":name,"checksum":"md5:"+hashlib.md5(data).hexdigest(),"filesize":len(data)}
                    if not self.changed:
                        manifest=outer.root/"EXPECTED-PUBLICATION.json"
                        manifest.write_bytes(manifest.read_bytes()+b"\n")
                        self.changed=True
                    return {}
                if path.endswith("/files"): return list(self.uploaded.values())
                return outer.deposit()
        z=Fake()
        with patch.object(p,"client",return_value=z),patch.object(p,"persist"):
            with self.assertRaises(RuntimeError): p.publish()
        self.assertEqual(z.posts,0)
        self.assertFalse((self.root/"publication-intent.json").exists())

    def test_bad_public_bytes_never_produce_success_receipt(self):
        self.package()
        outer=self
        class Fake:
            def request(self,path,method="GET",**kwargs):
                if method!="GET": raise AssertionError("Published record must not mutate")
                record=outer.deposit(True)
                if path.startswith("/records/"):
                    record["files"]=[{"key":r["name"],"links":{"self":"https://zenodo.org/api/records/99999991/files/"+r["name"]}} for r in outer.expected["files"]]
                return record
        with patch.object(p,"client",return_value=Fake()),patch.object(p,"persist"),patch.object(p,"download_public",return_value=b"wrong bytes"):
            with self.assertRaises(RuntimeError): p.publish()
        self.assertFalse((self.root/"publication-record.json").exists())

if __name__=="__main__":
    unittest.main(verbosity=2)
