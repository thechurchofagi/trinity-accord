#!/usr/bin/env python3
"""Reserve one separate TA13 Zenodo draft; never publish in this step."""
from __future__ import annotations
import json, os, sys, urllib.parse
from publication_common import DATE,REPORT,ROOT,TITLE,VERSION,check_deposit,client,load,persist_states,read,save,select_existing,validate_identity
PHASE='initialization'
def run():
    global PHASE
    z=client(); checkpoint=ROOT/'deposit.json'
    PHASE='recover_existing_reservation'
    if checkpoint.exists():
        identity=load('deposit.json'); rid=validate_identity(identity)
        deposit=read(z,f'/deposit/depositions/{rid}'); check_deposit(deposit,identity)
    else:
        rows=read(z,'/deposit/depositions?'+urllib.parse.urlencode({'q':'"Civilizational Intellectual Production Satellite Accounts"','size':100}))
        deposit=select_existing(rows)
        if deposit is None:
            if (ROOT/'create-intent.json').exists(): raise RuntimeError('Unresolved creation intent; reconcile before creating another record')
            PHASE='checkpoint_creation_intent'
            save('create-intent.json',{'title':TITLE,'report_number':REPORT,'version':VERSION,'state':'CREATE_ONCE_INTENT','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
            persist_states({'create-intent.json'})
            PHASE='create_one_new_draft'
            metadata={
              'upload_type':'publication','publication_type':'preprint','title':TITLE,
              'creators':[{'name':'Liu, Hongju'}],
              'description':'<p>TA-TR-2026-13. A theory-method preprint proposing Civilizational Intellectual Production Satellite Accounts (CIPSA): a flow-based, domain-first, partial-identification framework for measuring Human/AI/interaction contributions to new intellectual production and epistemic governance. Complete Chinese text with English title and abstract. Three deterministic simulations validate the accounting logic only; they are not estimates of real-world Human/AI intellectual shares. The paper explicitly treats earlier knowledge-economy satellite accounts, innovation accounting, AI-economy measurement, AI-in-science measurement, contribution-disclosure frameworks, and partial-identification methods as prior art. Substantial AI assistance under human direction is disclosed. Not peer reviewed. Version 1.0 is the first public edition. No prior DOI or Bitcoin Original is amended.</p>',
              'publication_date':DATE,'version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'zho',
              'keywords':['civilizational intellectual production','human-AI contribution','epistemic governance','partial identification','satellite accounts','AI measurement','AGI measurement']
            }
            deposit=z.request('/deposit/depositions','POST',{'metadata':metadata})
    rid,doi=check_deposit(deposit)
    receipt={'record_id':rid,'doi':doi,'title':TITLE,'report_number':REPORT,'version':VERSION,
             'submitted':bool(deposit.get('submitted')),
             'state':'ALREADY_SUBMITTED_REQUIRES_READBACK' if deposit.get('submitted') else 'RESERVED_NOT_PUBLICATION',
             'prior_records_modified':False,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')}
    save('deposit.json',receipt)
    save('preparation-attempt.json',{'state':receipt['state'],'record_id':rid,'phase':'completed','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    persist_states({'deposit.json','preparation-attempt.json'})
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
if __name__=='__main__':
    try: run()
    except Exception as error:
        save('preparation-attempt.json',{'state':'INCOMPLETE_REQUIRES_SAME_RECORD_RECONCILIATION','phase':PHASE,'error_type':type(error).__name__,'error':str(error),'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
        print(f'{type(error).__name__}: {error}',file=sys.stderr); sys.exit(1)
