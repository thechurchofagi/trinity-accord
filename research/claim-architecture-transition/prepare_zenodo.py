#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys, urllib.parse
from publication_common import DATE,REPORT,ROOT,TITLE,VERSION,check_deposit,client,load,read,save,select_existing,validate_identity
PHASE='initialization'
def run():
    global PHASE
    z=client(); checkpoint=ROOT/'deposit.json'
    PHASE='recover_existing_reservation'
    if checkpoint.exists():
        identity=load('deposit.json'); rid=validate_identity(identity)
        dep=read(z,f'/deposit/depositions/{rid}'); check_deposit(dep,identity)
    else:
        rows=read(z,'/deposit/depositions?'+urllib.parse.urlencode({'q':'"The Claim Architecture Transition"','size':100}))
        dep=select_existing(rows)
        if dep is None:
            if (ROOT/'create-intent.json').exists(): raise RuntimeError('Unresolved creation intent; reconcile before creating another record')
            save('create-intent.json',{'title':TITLE,'report_number':REPORT,'version':VERSION,'state':'CREATE_ONCE_INTENT','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
            PHASE='create_one_new_draft'
            md={'upload_type':'publication','publication_type':'preprint','title':TITLE,
                'creators':[{'name':'Liu, Hongju'}],
                'description':'<p>TA-TR-2026-14, version 1.1. Economics theory working paper on claim architecture under transformative AI. The manuscript develops a CES real-claim phase condition, a general power-law claim-closure theorem, and an abundance-exclusion divergence result. It is a structural stress test rather than an unemployment forecast or a prescription of one political-economic system. Substantial AI assistance under human direction is disclosed. Not peer reviewed. The targeted prior-art search does not certify global priority. Version 1.1 is the first public DOI edition.</p>',
                'publication_date':DATE,'version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'eng',
                'keywords':['transformative AI','automation','general equilibrium','income distribution','claim architecture','post-labor economics','AI ownership','basic needs','public finance']}
            dep=z.request('/deposit/depositions','POST',{'metadata':md})
    rid,doi=check_deposit(dep)
    receipt={'record_id':rid,'doi':doi,'title':TITLE,'report_number':REPORT,'version':VERSION,'submitted':bool(dep.get('submitted')),
             'state':'ALREADY_SUBMITTED_REQUIRES_READBACK' if dep.get('submitted') else 'RESERVED_NOT_PUBLICATION',
             'prior_records_modified':False,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')}
    save('deposit.json',receipt); save('preparation-attempt.json',{'state':receipt['state'],'record_id':rid,'phase':'completed','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
if __name__=='__main__':
    try: run()
    except Exception as e:
        save('preparation-attempt.json',{'state':'INCOMPLETE_REQUIRES_SAME_RECORD_RECONCILIATION','phase':PHASE,'error_type':type(e).__name__,'error':str(e),'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
        print(f'{type(e).__name__}: {e}',file=sys.stderr); sys.exit(1)
