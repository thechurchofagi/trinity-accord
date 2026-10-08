#!/usr/bin/env python3
"""Prepare ONE linked Zenodo v1.0.1 draft without publishing or uploading.

Old Zenodo v1.0.0 DOI remains untouched. External POST is never replayed on
unknown outcome. Publication requires a separately frozen v1.0.1 PDF/ZIP.
"""
from __future__ import annotations
import json, os, pathlib, subprocess, sys, time, urllib.parse, urllib.request, urllib.error
P=pathlib.Path(__file__).resolve().parent
REPO=P.parents[1]
BRANCH='research/mgtd-method-v1-0-1-20261008'
OLD_ID=23241205
OLD_DOI='10.5281/zenodo.23241205'
TITLE='Map-Guided Theory Development: A Versioned Protocol for Thought Experiments, Semantic Audits, and Human-AI Research'
SOURCE='manuscript-template.md'
FILES=('version-intent.json','new-version-deposit.json','preparation-status.json')

def save(n,x):
    p=P/n;t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');t.replace(p)
def load(n):return json.loads((P/n).read_text())
def persist():
    if os.environ.get('GITHUB_ACTIONS')!='true':return
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()
    if branch!=BRANCH: raise RuntimeError('Refuse wrong branch')
    paths=[str((P/n).relative_to(REPO)) for n in FILES if (P/n).exists()]
    if not paths:return
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
    subprocess.run(['git','add','--',*paths],cwd=REPO,check=True)
    if subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip():
        subprocess.run(['git','commit','-m','[skip ci] Checkpoint v1.0.1 linked Zenodo draft state'],cwd=REPO,check=True)
        subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*_):raise RuntimeError('Zenodo auth redirect refused')
def api(endpoint,method='GET',payload=None):
    if os.environ.get('GITHUB_ACTIONS')!='true' or not os.environ.get('ZENODO_ACCESS_TOKEN'):
        raise RuntimeError('Existing Zenodo secret in GitHub Actions is required')
    url=endpoint if endpoint.startswith('https://') else ('https://zenodo.org'+endpoint if endpoint.startswith('/api/') else 'https://zenodo.org/api'+endpoint)
    u=urllib.parse.urlsplit(url)
    if u.scheme!='https' or u.netloc!='zenodo.org':raise RuntimeError('Untrusted DOI backend')
    h={'Authorization':'Bearer '+os.environ['ZENODO_ACCESS_TOKEN'],'User-Agent':'MGTD-Version-Preparation/1.0'}
    data=None
    if payload is not None:
        data=json.dumps(payload).encode('utf8');h['Content-Type']='application/json'
    req=urllib.request.Request(url,headers=h,method=method,data=data)
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=100) as response:
        raw=response.read(8_000_001)
    if len(raw)>8_000_000:raise RuntimeError('Response too large')
    return json.loads(raw) if raw else None

def locate_unpublished():
    rows=[]
    for page in range(1,9):
        a=api(f'/deposit/depositions?page={page}&size=100')
        if not isinstance(a,list):raise RuntimeError('Draft listing changed')
        for x in a:
            if x.get('submitted'):continue
            if x.get('id')==OLD_ID:continue
            if x.get('conceptrecid')==OLD_ID:continue
            if str(x.get('conceptrecid') or '') == str(load('version-intent.json').get('conceptrecid','__unknown__')):
                rows.append(x)
        if len(a)<100:break
    return rows

def prepare():
    md=(P/SOURCE).read_text(encoding='utf8')
    if md.count('__MGTD_V101_DOI__')!=2 or 'MGTD-PAPER-v1.0.1' not in md:
        raise RuntimeError('Template is not the expected version / placeholders')
    if (P/'new-version-deposit.json').exists():
        d=load('new-version-deposit.json');rid=d['record_id']
        actual=api('/deposit/depositions/'+str(rid))
        if actual.get('id')!=rid or actual.get('submitted') or actual.get('metadata',{}).get('title')!=TITLE:
            # In a future run after publication, published status must be handled by publisher.
            if actual.get('submitted') and (P/'publication-record-v101.json').exists():return
            raise RuntimeError('Existing draft not in expected state')
        print('EXISTING_V101_DRAFT',rid,d['doi']);return
    old=api('/deposit/depositions/'+str(OLD_ID))
    if not old.get('submitted') or old.get('doi')!=OLD_DOI or old.get('metadata',{}).get('title')!=TITLE:
        raise RuntimeError('Old record not immutable published MGTD original')
    concept=old.get('conceptrecid')
    if not concept:raise RuntimeError('Old record concept ID missing')
    pending='version-intent.json'
    if (P/pending).exists():
        intent=load(pending)
        if intent.get('old_record_id')!=OLD_ID or intent.get('conceptrecid')!=concept:
            raise RuntimeError('Existing intent mismatch')
        candidates=locate_unpublished()
        if len(candidates)!=1:
            raise RuntimeError('Uncertain newversion POST; cannot uniquely recover draft. Human reconciliation needed.')
        d=candidates[0]
    else:
        intent={'state':'CREATE_NEW_VERSION_ONCE','old_record_id':OLD_ID,'conceptrecid':concept,'old_doi':OLD_DOI,'requested_version':'1.0.1'}
        save(pending,intent);persist()
        try:
            response=api('/deposit/depositions/'+str(OLD_ID)+'/actions/newversion',method='POST')
        except Exception as exc:
            save('preparation-status.json',{'state':'CREATE_NEWVERSION_RESPONSE_UNCERTAIN','reason':type(exc).__name__})
            persist();raise
        link=response.get('links',{}).get('latest_draft','') if response else ''
        if not link:
            save('preparation-status.json',{'state':'CREATED_BUT_DRAFT_LINK_MISSING','reason':'Check unpublished drafts; do not POST again'})
            persist();raise RuntimeError('Newversion link missing; no replay')
        d=api(link)
        if d.get('id')==OLD_ID or d.get('submitted'):
            # Documented stale latest_draft behaviour; try unique matching draft.
            candidates=locate_unpublished()
            if len(candidates)!=1:raise RuntimeError('Cannot unambiguously discover new draft')
            d=candidates[0]
    rid=d.get('id')
    if not isinstance(rid,int) or rid==OLD_ID or d.get('submitted') or str(d.get('conceptrecid'))!=str(concept):
        raise RuntimeError('New version does not share original concept / draft')
    DOI=d.get('doi') or d.get('metadata',{}).get('prereserve_doi',{}).get('doi') or f'10.5281/zenodo.{rid}'
    if DOI!=f'10.5281/zenodo.{rid}':raise RuntimeError('Unexpected version DOI')
    save('new-version-deposit.json',{'state':'LINKED_DRAFT_CREATED','record_id':rid,'doi':DOI,'prior_record_id':OLD_ID,'prior_doi':OLD_DOI,'conceptrecid':concept,'version':'1.0.1','source':'Zenodo newversion action'})
    save('preparation-status.json',{'state':'RESERVED_NEW_VERSION', 'record_id':rid, 'doi':DOI, 'prior_record_id':OLD_ID, 'conceptrecid':concept})
    persist()
    print('MGTD_NEW_VERSION_RESERVED',rid,DOI)

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('verify','prepare','persist'):raise SystemExit('usage: prepare_version.py verify|prepare|persist')
    if sys.argv[1]=='verify':
        raw=(P/SOURCE).read_text();assert raw.count('__MGTD_V101_DOI__')==2; print('SOURCE_TEMPLATE_PASS')
    elif sys.argv[1]=='prepare':prepare()
    else:persist()
