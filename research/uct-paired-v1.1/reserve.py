#!/usr/bin/env python3
"""Reserve successors of exactly two published UCT editions; never publish here.
Uses the established repository Zenodo client and intended Actions credential.
No credentials are logged. Checkpoints precede non-idempotent operations.
"""
from __future__ import annotations
import hashlib, importlib.util, json, os, pathlib, subprocess, urllib.parse
ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parents[1]
BRANCH='research/uct-ab-v1-1-20260929'
CLIENT_BLOB='a0cbc84cc5fd826c06d16456c4adbaa40dabc788'
PAPERS={
 'a': {'old_id':23005588,'report':'TA-TR-2026-20','title':'Unified Consciousness Theory I: Ontic Structure, Physical Views, and the Structural Continuity from Physical Process to Conceptual Self'},
 'b': {'old_id':23008262,'report':'TA-TR-2026-21','title':'Unified Consciousness Theory II: Consciousness Theories as Effective Organization Theories'}
}
def save(name,data):
    p=ROOT/name; p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def load(name):return json.loads((ROOT/name).read_text())
def persist():
    subprocess.run(['git','config','user.name','trinity-research-release-bot'],cwd=REPO,check=True)
    subprocess.run(['git','config','user.email','actions@github.com'],cwd=REPO,check=True)
    subprocess.run(['git','add','--',str(ROOT.relative_to(REPO))],cwd=REPO,check=True)
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=REPO).returncode==0:return
    subprocess.run(['git','commit','-m','research: checkpoint UCT v1.1 reservation [skip ci]'],cwd=REPO,check=True)
    for _ in range(3):
        if subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO).returncode==0:return
        subprocess.run(['git','fetch','origin',BRANCH,'--prune'],cwd=REPO,check=True)
        subprocess.run(['git','rebase','origin/'+BRANCH],cwd=REPO,check=True)
    raise RuntimeError('Unable to persist reservation checkpoint')
def client():
    p=REPO/'research/reading-trinity-accord/publish_zenodo.py';b=p.read_bytes()
    if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=CLIENT_BLOB:
        raise RuntimeError('Established Zenodo client changed')
    spec=importlib.util.spec_from_file_location('uct_zenodo_client',p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:raise RuntimeError('Publication credential unavailable')
    return mod.Zenodo(token)
def draft_link(dep):
    link=dep.get('links',{}).get('latest_draft')
    if not link:return None
    url=urllib.parse.urlsplit(link)
    if url.scheme!='https' or url.hostname!='zenodo.org' or not url.path.startswith('/api/deposit/depositions/'):
        raise RuntimeError('Unexpected successor draft link')
    # Published deposits can expose a latest_draft link pointing to themselves.
    # It is not evidence that a new unpublished successor already exists.
    if url.path.rstrip('/').split('/')[-1]==str(dep.get('id')):return None
    return link

def reserve():
    z=client()
    for key,cfg in PAPERS.items():
        checkpoint=f'deposit-{key}.json'; intent=f'newversion-intent-{key}.json'
        oldid=cfg['old_id'];old=z.request(f'/deposit/depositions/{oldid}')
        if old.get('id')!=oldid or not old.get('submitted') or str(old.get('metadata',{}).get('version'))!='1.0':
            raise RuntimeError('Prior UCT edition identity/status differs')
        if not any(c.get('name')=='Liu, Hongju' for c in old['metadata'].get('creators',[])):
            raise RuntimeError('Prior author mismatch')
        before=z.request(f'/records/{oldid}',authenticated=False)
        if before.get('doi')!=f'10.5281/zenodo.{oldid}':raise RuntimeError('Prior DOI mismatch')
        baseline_name=f'prior-public-{key}.json'
        if not (ROOT/baseline_name).exists():save(baseline_name,before);persist()
        if (ROOT/checkpoint).exists():
            identity=load(checkpoint);newid=int(identity['record_id'])
            if newid in [p['old_id'] for p in PAPERS.values()]:raise RuntimeError('Refusing a prior ID')
            draft=z.request(f'/deposit/depositions/{newid}')
        else:
            link=draft_link(old)
            if link:
                draft=z.request(link)
                if draft.get('id')==oldid or draft.get('submitted'):raise RuntimeError('Invalid existing successor')
                ver=str(draft.get('metadata',{}).get('version',''))
                if ver not in ('1.0','1.1'):raise RuntimeError('An unrelated successor draft already exists')
                if not (ROOT/intent).exists():
                    raise RuntimeError('Existing successor without this release intent; reconcile before adopting')
            else:
                latest=before.get('links',{}).get('latest')
                if latest:
                    parsed=urllib.parse.urlsplit(latest)
                    if parsed.hostname!='zenodo.org':raise RuntimeError('Unexpected latest-record host')
                    latestid=parsed.path.rstrip('/').split('/')[-1]
                    if latestid.isdigit() and int(latestid)!=oldid:raise RuntimeError('A newer published edition exists')
                if (ROOT/intent).exists():raise RuntimeError('Unresolved new-version request: inspect before retrying')
                save(intent,{'state':'NEWVERSION_ONCE_INTENT','old_record_id':oldid,'version':'1.1',
                             'run_id':os.environ.get('GITHUB_RUN_ID'),'authorization':'User explicitly requested completing revisions through DOI publication on 2026-09-29.'})
                persist()
                response=z.request(f'/deposit/depositions/{oldid}/actions/newversion','POST')
                link=draft_link(response)
                if not link:raise RuntimeError('No latest_draft returned by newversion')
                draft=z.request(link)
            newid=int(draft['id'])
        if newid in [p['old_id'] for p in PAPERS.values()] or draft.get('submitted'):
            raise RuntimeError('Reservation may write only a new unpublished draft')
        oldconcept=str(old.get('conceptrecid',before.get('conceptrecid','')))
        newconcept=str(draft.get('conceptrecid',''))
        if not oldconcept or newconcept!=oldconcept:raise RuntimeError('Version-family identity mismatch')
        md={'upload_type':'publication','publication_type':'preprint','title':cfg['title'],
            'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
            'description':'<p>'+cfg['report']+' v1.1. Revised theoretical preprint in the Unified Consciousness Theory series. Preserves the prior v1.0 edition; not peer reviewed. Explicitly separates adopted ontological commitments, conditional mathematical results, scientific views, and finite empirical bridges. Model calculations do not establish experience or validate the foundational axioms.</p><p>Human author of record and responsible depositor: Hongju Liu. Substantial ChatGPT assistance, including GPT-6 Astra Pro in this revision, is disclosed. Adjacent non-amending research; not an amendment or independent corroboration of the Trinity Accord or its Bitcoin Originals.</p>',
            'publication_date':'2026-09-29','version':'1.1','access_right':'open','license':'cc-by-4.0','language':'eng',
            'keywords':['consciousness','structural identity','process ontology','causal organization','theory unification'],
            'related_identifiers':[{'identifier':f'10.5281/zenodo.{oldid}','relation':'isNewVersionOf','scheme':'doi'}],
            'prereserve_doi':True}
        draft=z.request(f'/deposit/depositions/{newid}','PUT',{'metadata':md})
        doi=draft.get('metadata',{}).get('prereserve_doi',{}).get('doi') or draft.get('doi')
        if doi!=f'10.5281/zenodo.{newid}':raise RuntimeError('Successor DOI reservation mismatch')
        save(checkpoint,{'state':'RESERVED_NOT_PUBLISHED','record_id':newid,'doi':doi,
                         'conceptrecid':newconcept,'prior_record_id':oldid,'report_number':cfg['report'],
                         'title':cfg['title'],'version':'1.1','submitted':False,
                         'old_published_files_modified':False,'run_id':os.environ.get('GITHUB_RUN_ID')})
        persist()
        print(key,doi,'RESERVED_NOT_PUBLISHED',flush=True)
if __name__=='__main__':
    try:reserve()
    finally:persist()
