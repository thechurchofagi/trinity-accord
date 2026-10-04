#!/usr/bin/env python3
import hashlib, json, os, re, sys, urllib.parse, urllib.request
from publication_common import *
PHASE="local_review_gate"

def check_identity(dep,e):
    md=dep.get("metadata",{}); rid=e["record_id"]
    if (dep.get("id"),str(dep.get("conceptrecid")),md.get("title"),str(md.get("version")))!=(rid,EXPECTED_CONCEPT,TITLE,VERSION): raise RuntimeError("reserved version/concept identity mismatch")
    if [x.get("name") for x in md.get("creators",[])]!=["Liu, Hongju"]: raise RuntimeError("creator mismatch")
    doi=dep.get("doi") or md.get("doi") or md.get("prereserve_doi",{}).get("doi")
    if doi!=e["doi"]: raise RuntimeError("reserved DOI mismatch")

def validate_review(e,digest):
    vr=json.loads((ROOT/"visual-review.json").read_text(encoding="utf-8"))
    if vr.get("state")!="VISUAL_AND_CONTENT_REVIEW_PASS" or vr.get("expected_manifest_sha256")!=digest: raise RuntimeError("exact visual/content review missing")
    auth=json.loads((ROOT/"PUBLISH-AUTHORIZATION.json").read_text(encoding="utf-8"))
    req=(REPORT,VERSION,e["record_id"],e["doi"],digest,"PUBLISH_EXACT_REVIEWED_LINKED_VERSION")
    got=(auth.get("report_number"),str(auth.get("version")),auth.get("record_id"),auth.get("doi"),auth.get("expected_manifest_sha256"),auth.get("authorization"))
    if got!=req: raise RuntimeError("publish authorization mismatch")
    if auth.get("author_explicit_release_request")!="发布 v1.2": raise RuntimeError("explicit author release authorization marker missing")
    if auth.get("prior_version_must_remain_unchanged") is not True or auth.get("no_new_independent_deposit") is not True: raise RuntimeError("version-lineage safety flags missing")

def delete_draft_file(z,rid,item):
    fid=item.get("id")
    if fid is None: raise RuntimeError("draft file id missing")
    endpoint=f"/deposit/depositions/{rid}/files/{urllib.parse.quote(str(fid),safe='')}"
    try:z.request(endpoint,"DELETE")
    except json.JSONDecodeError:
        listing=z.request(f"/deposit/depositions/{rid}/files")
        if any(str(f.get("id"))==str(fid) for f in listing): raise RuntimeError("draft deletion not confirmed")

def run():
    global PHASE
    e,digest=validate_local_package(); validate_review(e,digest); rid=e["record_id"]; doi=e["doi"]
    z=client()
    PHASE="read_predecessor"; prev=read(z,f"/records/{PREVIOUS_RECORD}",authenticated=False)
    prev_files=sorted((f["key"],f.get("checksum"),f.get("size")) for f in prev.get("files",[]))
    if (prev.get("id"),str(prev.get("conceptrecid")),prev.get("doi"),str(prev.get("metadata",{}).get("version")))!=(PREVIOUS_RECORD,EXPECTED_CONCEPT,f"10.5281/zenodo.{PREVIOUS_RECORD}","1.1"): raise RuntimeError("predecessor lineage mismatch")
    PHASE="read_descendant"; dep=read(z,f"/deposit/depositions/{rid}"); check_identity(dep,e); already=bool(dep.get("submitted"))
    if not already:
        PHASE="metadata_refresh"; md=dict(dep.get("metadata",{})); md.pop("doi",None); md.pop("prereserve_doi",None); md.update(zenodo_metadata())
        dep=z.request(f"/deposit/depositions/{rid}","PUT",{"metadata":md}); check_identity(dep,e)
        PHASE="upload_exact_package"; remote=read(z,f"/deposit/depositions/{rid}/files")
        expected={x["name"]:x for x in e["files"]}; predecessor_names={x[0] for x in prev_files}
        for item in remote:
            name=item.get("filename",item.get("key"))
            if name not in expected:
                if name not in predecessor_names: raise RuntimeError("unrecognized draft asset; refusing deletion")
                delete_draft_file(z,rid,item)
        bucket=dep["links"]["bucket"]; p=urllib.parse.urlsplit(bucket)
        if p.scheme!="https" or p.hostname!="zenodo.org" or not p.path.startswith("/api/files/") or p.query or p.fragment: raise RuntimeError("unexpected bucket")
        for row in e["files"]:
            data=(ROOT/"published"/row["name"]).read_bytes()
            z.request(bucket.rstrip("/")+"/"+urllib.parse.quote(row["name"],safe=""),"PUT",data,binary=True)
        remote=read(z,f"/deposit/depositions/{rid}/files"); inv={x.get("filename",x.get("key")):x for x in remote}
        if len(remote)!=len(PACKAGE_FILES) or set(inv)!=PACKAGE_FILES: raise RuntimeError("draft inventory mismatch")
        for row in e["files"]:
            data=(ROOT/"published"/row["name"]).read_bytes(); item=inv[row["name"]]
            if item.get("filesize")!=len(data) or str(item.get("checksum","")).removeprefix("md5:")!=hashlib.md5(data).hexdigest(): raise RuntimeError("draft byte mismatch")
        save("publication-attempt.json",{"state":"PUBLICATION_INTENT_FOR_EXISTING_LINKED_VERSION","record_id":rid,"expected_manifest_sha256":digest,"new_record_creation":False,"newversion_creation":False,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")}); persist()
        result=z.request(f"/deposit/depositions/{rid}/actions/publish","POST"); check_identity(result,e)
        if not result.get("submitted"): raise RuntimeError("not published")
    PHASE="anonymous_public_readback"; public=read(z,f"/records/{rid}",authenticated=False); check_identity(public,e)
    remote={x["key"]:x for x in public.get("files",[])}
    if len(public.get("files",[]))!=len(PACKAGE_FILES) or set(remote)!=PACKAGE_FILES: raise RuntimeError("public inventory mismatch")
    rows=[]
    for row in e["files"]:
        url=remote[row["name"]]["links"].get("self") or remote[row["name"]]["links"].get("download"); data=public_download(url)
        if len(data)!=row["bytes"] or sha(data)!=row["sha256"]: raise RuntimeError("public exact-byte mismatch: "+row["name"])
        rows.append(dict(row,public_url=url,matches_local=True))
    after=read(z,f"/records/{PREVIOUS_RECORD}",authenticated=False)
    after_files=sorted((f["key"],f.get("checksum"),f.get("size")) for f in after.get("files",[]))
    if after_files!=prev_files or after.get("doi")!=prev.get("doi") or str(after.get("metadata",{}).get("version"))!="1.1": raise RuntimeError("predecessor public edition changed")
    PHASE="doi_resolution"; resolver=resolver_check(doi,rid); passed=resolver.get("matches_record") is True
    receipt={"state":"PUBLISHED_AND_PUBLIC_READBACK_PASS" if passed else "PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING","report_number":REPORT,"title":TITLE,"version":VERSION,"record_id":rid,"doi":doi,"conceptrecid":EXPECTED_CONCEPT,"conceptdoi":e["conceptdoi"],"previous_record_id":PREVIOUS_RECORD,"previous_doi":f"10.5281/zenodo.{PREVIOUS_RECORD}","submitted":True,"file_count":len(rows),"files":rows,"expected_manifest_sha256":digest,"public_readback_authenticated":False,"public_file_readback_pass":True,"doi_resolution_pass":passed,"doi_resolver":resolver,"prior_version_inventory_unchanged":True,"was_already_published":already,"workflow_run_id":os.environ.get("GITHUB_RUN_ID"),"source_commit":os.environ.get("GITHUB_SHA"),"peer_reviewed":False,"global_originality_certified":False}
    save("publication-record.json",receipt); save("publication-attempt.json",{"state":receipt["state"],"record_id":rid,"phase":"completed","workflow_run_id":os.environ.get("GITHUB_RUN_ID")}); print(json.dumps(receipt,ensure_ascii=False,indent=2))
    if not passed: raise RuntimeError("published exact bytes passed; DOI resolution pending")
if __name__=="__main__":
    try:run()
    except Exception as e:
        save("publication-attempt.json",{"state":"INCOMPLETE_REQUIRES_SAME_RECORD_RESUMPTION","phase":PHASE,"error_type":type(e).__name__,"error":str(e),"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        print(type(e).__name__+": "+str(e),file=sys.stderr); sys.exit(1)
