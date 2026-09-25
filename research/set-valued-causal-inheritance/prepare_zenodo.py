#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys, urllib.parse
from publication_common import (
    DATE,REPORT,ROOT,TITLE,VERSION,build_package,check_deposit,client,
    load,persist,read,save,select_existing
)
PHASE="initialization"

def run():
    global PHASE
    z=client()
    checkpoint=ROOT/"deposit.json"
    PHASE="recover_existing_reservation"
    if checkpoint.exists():
        identity=load("deposit.json")
        rid=int(identity["record_id"])
        dep=read(z,f"/deposit/depositions/{rid}")
        check_deposit(dep,identity)
    else:
        rows=read(z,"/deposit/depositions?"+urllib.parse.urlencode({"q":f'"{TITLE}"',"size":100}))
        dep=select_existing(rows)
        if dep is None:
            if (ROOT/"create-intent.json").exists():
                raise RuntimeError("Unresolved TA17 create intent; reconcile before creating another record")
            save("create-intent.json",{
                "title":TITLE,"report_number":REPORT,"version":VERSION,
                "state":"CREATE_ONCE_INTENT","workflow_run_id":os.environ.get("GITHUB_RUN_ID")
            })
            persist({"create-intent.json"})
            PHASE="create_one_new_draft"
            md={
              "upload_type":"publication","publication_type":"preprint","title":TITLE,
              "creators":[{"name":"Liu, Hongju"}],
              "description":(
                "<p>TA-TR-2026-17, version 1.0. Theoretical/computational preprint on "
                "set-valued causal inheritance, branching functional continuity, "
                "representation invariance, current-process lineage, and persistent-agent control. "
                "Substantial AI assistance under human direction. Not peer reviewed; "
                "no claim about phenomenal consciousness, moral status, legal identity, or numerical personal identity.</p>"
              ),
              "publication_date":DATE,"version":VERSION,"access_right":"open",
              "license":"cc-by-4.0","language":"eng",
              "keywords":[
                "functional self-continuity","causal inheritance","successor sets",
                "persistent agents","branching","causal representation","information theory",
                "checkpoint restore merge","reinforcement learning"
              ]
            }
            dep=z.request("/deposit/depositions","POST",{"metadata":md})
    rid,doi=check_deposit(dep)
    receipt={
      "record_id":rid,"doi":doi,"title":TITLE,"report_number":REPORT,"version":VERSION,
      "submitted":bool(dep.get("submitted")),
      "state":"ALREADY_SUBMITTED_REQUIRES_READBACK" if dep.get("submitted") else "RESERVED_NOT_PUBLICATION",
      "prior_records_modified":False,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")
    }
    save("deposit.json",receipt)
    PHASE="build_exact_package"
    expected=build_package()
    save("preparation-attempt.json",{
      "state":receipt["state"],"record_id":rid,"doi":doi,
      "file_count":expected["file_count"],"phase":"completed",
      "workflow_run_id":os.environ.get("GITHUB_RUN_ID")
    })
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=="__main__":
    try:
        run()
    except Exception as e:
        save("preparation-attempt.json",{
          "state":"INCOMPLETE_REQUIRES_SAME_RECORD_RECONCILIATION",
          "phase":PHASE,"error_type":type(e).__name__,"error":str(e),
          "workflow_run_id":os.environ.get("GITHUB_RUN_ID")
        })
        print(f"{type(e).__name__}: {e}",file=sys.stderr)
        sys.exit(1)

# TA17 prepare trigger marker 2

# TA17 prepare trigger marker 3
