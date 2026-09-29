#!/usr/bin/env python3
import hashlib, html, json, os, re, sys, urllib.parse, urllib.request
from publication_common import *
PHASE="local_review_gate"
def public_inventory(record):
    return {x["key"]:(x["size"],x["checksum"]) for x in record.get("files",[])}

def check_identity(dep,e):
    rid=e["record_id"];concept=str(e["conceptrecid"]);md=dep.get("metadata",{})
    if (dep.get("id"),str(dep.get("conceptrecid")),md.get("title"),str(md.get("version")))!=(rid,concept,TITLE,VERSION):raise RuntimeError("reserved version/concept identity mismatch")
    if [x.get("name") for x in md.get("creators",[])]!=["Liu, Hongju"]:raise RuntimeError("creator mismatch")
    doi=dep.get("doi") or md.get("doi") or md.get("prereserve_doi",{}).get("doi")
    if doi!=e["doi"]:raise RuntimeError("reserved DOI mismatch")

def validate_review(e,digest):
    vr=json.loads((ROOT/"visual-review.json").read_text(encoding="utf-8"))
    if vr.get("state")!="VISUAL_AND_CONTENT_REVIEW_PASS" or vr.get("expected_manifest_sha256")!=digest:raise RuntimeError("exact visual/content review missing")
    auth=json.loads((ROOT/"PUBLISH-AUTHORIZATION.json").read_text(encoding="utf-8"))
    req=(REPORT,VERSION,e["record_id"],e["doi"],digest,"PUBLISH_EXACT_REVIEWED_LINKED_VERSION")
    got=(auth.get("report_number"),str(auth.get("version")),auth.get("record_id"),auth.get("doi"),auth.get("expected_manifest_sha256"),auth.get("authorization"))
    if got!=req:raise RuntimeError("publish authorization mismatch")

def run():
    global PHASE
    e,digest=validate_local_package();validate_review(e,digest);rid=e["record_id"];doi=e["doi"];concept=str(e["conceptrecid"])
    z=client()
    PHASE="read_predecessor";prev=read(z,f"/records/{PREVIOUS_RECORD}",authenticated=False)
    if (prev.get("id"),str(prev.get("conceptrecid")),prev.get("doi"),str(prev.get("metadata",{}).get("version")))!=(PREVIOUS_RECORD,concept,f"10.5281/zenodo.{PREVIOUS_RECORD}","1.0"):raise RuntimeError("predecessor lineage mismatch")
    prev_inventory=public_inventory(prev)
    PHASE="read_descendant";dep=read(z,f"/deposit/depositions/{rid}");check_identity(dep,e);already=bool(dep.get("submitted"))
    if not already:
        PHASE="metadata_refresh"
        md=dict(dep.get("metadata",{}))
        for key in ("doi","prereserve_doi"):md.pop(key,None)
        md.update(zenodo_metadata())
        dep=z.request(f"/deposit/depositions/{rid}","PUT",{"metadata":md});check_identity(dep,e)
        PHASE="upload_exact_package"
        remote=read(z,f"/deposit/depositions/{rid}/files")
        if len({x["filename"] for x in remote})!=len(remote):raise RuntimeError("duplicate draft files")
        for item in remote:
            name=item["filename"]
            if name not in PACKAGE_FILES:
                old=prev_inventory.get(name)
                checksum=str(item.get("checksum","")).removeprefix("md5:")
                if not old or item.get("filesize")!=old[0] or checksum!=old[1].removeprefix("md5:"):raise RuntimeError("unrelated draft asset; refusing deletion")
                fid=str(item["id"])
                if not re.fullmatch(r"[A-Za-z0-9-]+",fid):raise RuntimeError("bad inherited file id")
                url=f"https://zenodo.org/api/deposit/depositions/{rid}/files/{fid}"
                req=urllib.request.Request(url,method="DELETE",headers={"Authorization":"Bearer "+z.token})
                with urllib.request.urlopen(req,timeout=120) as response:
                    if response.status!=204:raise RuntimeError("inherited draft copy deletion failed")
        bucket=dep["links"]["bucket"];p=urllib.parse.urlsplit(bucket)
        if p.scheme!="https" or p.hostname!="zenodo.org" or not p.path.startswith("/api/files/") or p.query or p.fragment:raise RuntimeError("unexpected bucket")
        for row in e["files"]:
            data=(ROOT/"published"/row["name"]).read_bytes()
            z.request(bucket.rstrip("/")+"/"+urllib.parse.quote(row["name"],safe=""),"PUT",data,binary=True)
        remote=read(z,f"/deposit/depositions/{rid}/files");inventory={x["filename"]:x for x in remote}
        if len(remote)!=len(PACKAGE_FILES) or set(inventory)!=PACKAGE_FILES:raise RuntimeError("draft inventory mismatch")
        for row in e["files"]:
            data=(ROOT/"published"/row["name"]).read_bytes();r=inventory[row["name"]]
            if r["filesize"]!=len(data) or str(r["checksum"]).removeprefix("md5:")!=hashlib.md5(data).hexdigest():raise RuntimeError("draft byte mismatch")
        PHASE="publish_existing_linked_version"
        save("publication-attempt.json",{"state":"PUBLICATION_INTENT_FOR_EXISTING_LINKED_VERSION","record_id":rid,"expected_manifest_sha256":digest,"new_record_creation":False,"newversion_creation":False,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        result=z.request(f"/deposit/depositions/{rid}/actions/publish","POST");check_identity(result,e)
        if not result.get("submitted"):raise RuntimeError("not published")
    PHASE="anonymous_public_readback";public=read(z,f"/records/{rid}",authenticated=False);check_identity(public,e)
    remote={x["key"]:x for x in public.get("files",[])}
    if len(public.get("files",[]))!=len(PACKAGE_FILES) or set(remote)!=PACKAGE_FILES:raise RuntimeError("public inventory mismatch")
    rows=[]
    for row in e["files"]:
        url=remote[row["name"]]["links"].get("self") or remote[row["name"]]["links"].get("download")
        data=public_download(url)
        if len(data)!=row["bytes"] or sha(data)!=row["sha256"]:raise RuntimeError("public exact-byte mismatch: "+row["name"])
        rows.append(dict(row,public_url=url,matches_local=True))
    after=read(z,f"/records/{PREVIOUS_RECORD}",authenticated=False)
    if public_inventory(after)!=prev_inventory or after.get("doi")!=prev.get("doi") or str(after.get("metadata",{}).get("version"))!="1.0":raise RuntimeError("predecessor inventory changed")
    PHASE="doi_resolution";resolver=resolver_check(doi,rid);passed=resolver.get("matches_record") is True
    receipt={"state":"PUBLISHED_AND_PUBLIC_READBACK_PASS" if passed else "PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING","report_number":REPORT,"title":TITLE,"version":VERSION,"record_id":rid,"doi":doi,"conceptrecid":concept,"conceptdoi":e["conceptdoi"],"previous_record_id":PREVIOUS_RECORD,"previous_doi":f"10.5281/zenodo.{PREVIOUS_RECORD}","submitted":True,"file_count":len(rows),"files":rows,"expected_manifest_sha256":digest,"public_readback_authenticated":False,"public_file_readback_pass":True,"doi_resolution_pass":passed,"doi_resolver":resolver,"prior_version_inventory_unchanged":True,"new_research_papers":0,"distinct_research_papers_delta":0,"was_already_published":already,"workflow_run_id":os.environ.get("GITHUB_RUN_ID"),"source_commit":os.environ.get("GITHUB_SHA"),"peer_reviewed":False,"global_originality_certified":False}
    save("publication-record.json",receipt);save("publication-attempt.json",{"state":receipt["state"],"record_id":rid,"phase":"completed","workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    if not passed:raise RuntimeError("published exact bytes passed; DOI resolution pending")
if __name__=="__main__":
    try:run()
    except Exception as e:
        save("publication-attempt.json",{"state":"INCOMPLETE_REQUIRES_SAME_RECORD_RESUMPTION","phase":PHASE,"error_type":type(e).__name__,"error":str(e),"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        print(type(e).__name__+": "+str(e),file=sys.stderr);sys.exit(1)
