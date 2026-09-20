#!/usr/bin/env python3
import json, os, re, sys, urllib.parse
from publication_common import *
PHASE='initialization'
def previous_ok(dep):
    md=dep.get('metadata',{})
    if (dep.get('id'),md.get('title'),md.get('version'))!=(PREVIOUS_RECORD,PREVIOUS_TITLE,'1.0') or not dep.get('submitted'):
        raise RuntimeError('published predecessor identity mismatch')
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']: raise RuntimeError('predecessor creator mismatch')
    concept=str(dep.get('conceptrecid',''))
    if not concept.isdigit(): raise RuntimeError('conceptrecid unavailable')
    return concept
def draft_id(url):
    p=urllib.parse.urlsplit(url); m=re.fullmatch(r'/api/deposit/depositions/([0-9]+)',p.path)
    if p.scheme!='https' or p.hostname!='zenodo.org' or p.query or p.fragment or not m: raise RuntimeError('unexpected latest_draft URL')
    return int(m.group(1))
def descendant_ok(dep,concept):
    rid=validate_record_id(dep.get('id')); md=dep.get('metadata',{}); submitted=bool(dep.get('submitted'))
    if str(dep.get('conceptrecid'))!=concept: raise RuntimeError('not same concept lineage')
    allowed_titles={TITLE} if submitted else {PREVIOUS_TITLE,TITLE}
    if md.get('title') not in allowed_titles or md.get('version') not in (None,'1.0',VERSION):
        raise RuntimeError('unexpected descendant metadata: '+json.dumps({'id':rid,'title':md.get('title'),'version':md.get('version')},ensure_ascii=False))
    if [c.get('name') for c in md.get('creators',[])]!=['Liu, Hongju']: raise RuntimeError('descendant creator mismatch')
    return rid
def run():
    global PHASE
    z=client(); PHASE='read_predecessor'; prev=read(z,f'/deposit/depositions/{PREVIOUS_RECORD}'); concept=previous_ok(prev)
    if (ROOT/'deposit.json').exists():
        ident=load('deposit.json'); rid=validate_record_id(ident['record_id'])
        if str(ident.get('conceptrecid'))!=concept or ident.get('previous_record_id')!=PREVIOUS_RECORD: raise RuntimeError('local lineage mismatch')
        dep=read(z,f'/deposit/depositions/{rid}')
    else:
        latest=prev.get('links',{}).get('latest_draft'); existing=draft_id(latest) if latest else PREVIOUS_RECORD
        if existing==PREVIOUS_RECORD:
            PHASE='checkpoint_newversion_intent'
            save('create-intent.json',{'state':'CREATE_ONE_LINKED_VERSION_INTENT','previous_record_id':PREVIOUS_RECORD,'conceptrecid':concept,'version':VERSION,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
            persist_states({'create-intent.json'})
            PHASE='create_linked_version'; resp=z.request(f'/deposit/depositions/{PREVIOUS_RECORD}/actions/newversion','POST')
            existing=draft_id(resp['links']['latest_draft']) if resp.get('id')==PREVIOUS_RECORD else descendant_ok(resp,concept)
        dep=read(z,f'/deposit/depositions/{validate_record_id(existing)}')
    rid=descendant_ok(dep,concept)
    if dep.get('submitted'): raise RuntimeError('v1.1 descendant already submitted before package review')
    PHASE='set_metadata'
    metadata={'upload_type':'publication','publication_type':'preprint','title':TITLE,
      'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
      'description':'<p>TA-TR-2026-10, revision 1.1 of the published v1.0 preprint. This revision sharpens ERF as a slow shared-modulation hypothesis with discriminating tests and adds a small reproducible numerical training experiment. The experiment is reported as graded organizational profiles rather than a binary consciousness test; finite numerical residuals are not rounded into ontological thresholds. Complete Chinese paper with English title and abstract. Code and raw results are included. Not peer reviewed.</p>',
      'publication_date':DATE,'version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'zho',
      'keywords':['consciousness','endogenous reference field','contextual modulation','timescale separation','artificial intelligence','state space models','discriminating tests']}
    dep=z.request(f'/deposit/depositions/{rid}','PUT',{'metadata':metadata})
    md=dep.get('metadata',{}); doi=dep.get('doi') or md.get('prereserve_doi',{}).get('doi') or md.get('doi')
    if (md.get('title'),md.get('version'),doi)!=(TITLE,VERSION,f'10.5281/zenodo.{rid}'): raise RuntimeError('new version metadata/DOI mismatch')
    rec={'record_id':rid,'doi':doi,'conceptrecid':concept,'conceptdoi':f'10.5281/zenodo.{concept}',
      'previous_record_id':PREVIOUS_RECORD,'previous_doi':f'10.5281/zenodo.{PREVIOUS_RECORD}',
      'title':TITLE,'report_number':REPORT,'version':VERSION,'submitted':False,'state':'RESERVED_NOT_PUBLICATION',
      'prior_version_files_modified':False,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')}
    save('deposit.json',rec); save('preparation-attempt.json',{'state':rec['state'],'record_id':rid,'phase':'completed','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    persist_states({'deposit.json','preparation-attempt.json'}); print(json.dumps(rec,indent=2))
if __name__=='__main__':
    try:run()
    except Exception as e:
        save('preparation-attempt.json',{'state':'INCOMPLETE_REQUIRES_SAME_VERSION_RECONCILIATION','phase':PHASE,'error_type':type(e).__name__,'error':str(e),'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
        print(type(e).__name__+': '+str(e),file=sys.stderr); sys.exit(1)
