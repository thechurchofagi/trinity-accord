#!/usr/bin/env python3
import json, os, sys
from publication_common import *
PHASE="initialization"
def run():
    global PHASE
    ensure_source(); z=client()
    PHASE="read_predecessor"; prev=read(z,f"/deposit/depositions/{PREVIOUS_RECORD}"); concept=previous_ok(prev)
    if (ROOT/"deposit.json").exists():
        ident=load("deposit.json"); rid=validate_record_id(ident["record_id"])
        if str(ident.get("conceptrecid"))!=concept or ident.get("previous_record_id")!=PREVIOUS_RECORD: raise RuntimeError("local lineage mismatch")
        dep=read(z,f"/deposit/depositions/{rid}")
    else:
        latest=prev.get("links",{}).get("latest_draft"); existing=draft_id(latest) if latest else PREVIOUS_RECORD
        if existing==PREVIOUS_RECORD:
            if (ROOT/"create-intent.json").exists(): raise RuntimeError("unresolved prior creation intent")
            save("create-intent.json",{"state":"CREATE_ONE_LINKED_VERSION_INTENT","previous_record_id":PREVIOUS_RECORD,"conceptrecid":concept,"version":VERSION,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
            persist({"create-intent.json"})
            PHASE="create_linked_version"; resp=z.request(f"/deposit/depositions/{PREVIOUS_RECORD}/actions/newversion","POST")
            existing=draft_id(resp.get("links",{}).get("latest_draft")) if resp.get("id")==PREVIOUS_RECORD else descendant_ok(resp,concept)
        dep=read(z,f"/deposit/depositions/{validate_record_id(existing)}")
    rid=descendant_ok(dep,concept)
    if dep.get("submitted"): raise RuntimeError("v1.2 descendant already submitted before exact-package review")
    PHASE="set_metadata"; dep=z.request(f"/deposit/depositions/{rid}","PUT",{"metadata":zenodo_metadata()})
    md=dep.get("metadata",{}); doi=dep.get("doi") or md.get("prereserve_doi",{}).get("doi") or md.get("doi")
    if (md.get("title"),str(md.get("version")),doi)!=(TITLE,VERSION,f"10.5281/zenodo.{rid}"): raise RuntimeError("new-version metadata/DOI mismatch")
    rec={"record_id":rid,"doi":doi,"conceptrecid":concept,"conceptdoi":f"10.5281/zenodo.{concept}","previous_record_id":PREVIOUS_RECORD,"previous_doi":f"10.5281/zenodo.{PREVIOUS_RECORD}","title":TITLE,"report_number":REPORT,"version":VERSION,"submitted":False,"state":"RESERVED_NOT_PUBLISHED","prior_version_files_modified":False,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")}
    save("deposit.json",rec)
    PHASE="build_exact_package"; e=build_package()
    save("preparation-attempt.json",{"state":"RESERVED_AND_EXACT_PACKAGE_BUILT","record_id":rid,"doi":doi,"file_count":e["file_count"],"phase":"completed","workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
    print(json.dumps(rec,indent=2))
if __name__=="__main__":
    try: run()
    except Exception as e:
        save("preparation-attempt.json",{"state":"INCOMPLETE_REQUIRES_SAME_VERSION_RECONCILIATION","phase":PHASE,"error_type":type(e).__name__,"error":str(e),"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        print(type(e).__name__+": "+str(e),file=sys.stderr); sys.exit(1)
