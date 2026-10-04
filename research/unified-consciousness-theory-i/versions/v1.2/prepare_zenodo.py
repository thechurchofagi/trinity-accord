#!/usr/bin/env python3
import json, os, sys, urllib.parse
from publication_common import *
PHASE="initialization"

def existing_concept_drafts(z,concept):
    rows=read(z,"/deposit/depositions?"+urllib.parse.urlencode({"size":100}))
    hits=[]
    for dep in rows:
        if str(dep.get("conceptrecid",""))!=concept or dep.get("submitted") or dep.get("id")==PREVIOUS_RECORD:
            continue
        md=dep.get("metadata",{})
        creators=[c.get("name") for c in md.get("creators",[])]
        title=md.get("title"); version=str(md.get("version") or "")
        if "Liu, Hongju" in creators and title in {PREVIOUS_TITLE,TITLE} and version in {"","1.1","1.2"}:
            hits.append(dep)
    return hits

def adopt_or_none(z,concept):
    hits=existing_concept_drafts(z,concept)
    if len(hits)>1:
        raise RuntimeError("multiple unpublished drafts in concept lineage: "+",".join(str(x.get("id")) for x in hits))
    return hits[0] if hits else None

def run():
    global PHASE
    ensure_source(); z=client()
    PHASE="read_predecessor"; prev=read(z,f"/deposit/depositions/{PREVIOUS_RECORD}"); concept=previous_ok(prev)
    if (ROOT/"deposit.json").exists():
        ident=load("deposit.json"); rid=validate_record_id(ident["record_id"])
        if str(ident.get("conceptrecid"))!=concept or ident.get("previous_record_id")!=PREVIOUS_RECORD:
            raise RuntimeError("local lineage mismatch")
        dep=read(z,f"/deposit/depositions/{rid}")
    else:
        PHASE="reconcile_existing_draft"; dep=adopt_or_none(z,concept)
        if dep is None:
            if not (ROOT/"create-intent.json").exists():
                save("create-intent.json",{"state":"CREATE_ONE_LINKED_VERSION_INTENT","previous_record_id":PREVIOUS_RECORD,"conceptrecid":concept,"version":VERSION,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
                persist({"create-intent.json"})
            PHASE="create_linked_version"
            try:
                resp=z.request(f"/deposit/depositions/{PREVIOUS_RECORD}/actions/newversion","POST")
                latest=resp.get("links",{}).get("latest_draft")
                dep=read(z,latest) if latest else resp
            except Exception:
                PHASE="reconcile_after_newversion_error"
                dep=adopt_or_none(z,concept)
                if dep is None: raise
    rid=descendant_ok(dep,concept)
    if dep.get("submitted"): raise RuntimeError("v1.2 descendant already submitted before exact-package review")
    PHASE="set_metadata"; dep=z.request(f"/deposit/depositions/{rid}","PUT",{"metadata":zenodo_metadata()})
    md=dep.get("metadata",{}); doi=dep.get("doi") or md.get("prereserve_doi",{}).get("doi") or md.get("doi")
    if (md.get("title"),str(md.get("version")),doi)!=(TITLE,VERSION,f"10.5281/zenodo.{rid}"):
        raise RuntimeError("new-version metadata/DOI mismatch")
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
