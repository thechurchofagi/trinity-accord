#!/usr/bin/env python3
"""Publish exactly one frozen EAC-v3.0.0 DOI under the repository's Zenodo credentials.

No bearer credential printed, no preexisting third-party record overwritten, and no
second deposit on ambiguous remote response. Success requires public readback of
all six exact original files. OTS and paid Arweave are intentionally separate.
"""
from __future__ import annotations
import argparse,hashlib,json,os,sys,time,subprocess,zipfile
from pathlib import Path
from urllib.parse import urlencode,quote
from datetime import datetime,timezone

BASE='https://zenodo.org/api'
ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/'EXPECTED-PUBLICATION.json'
AUTH=ROOT/'PUBLISH-AUTHORIZATION.json'
ASSETS=ROOT/'release'
ATTEMPT=ROOT/'PUBLICATION-ATTEMPT.json'
RECEIPT=ROOT/'PUBLICATION-RECEIPT.json'

def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')

def freeze_check():
    x=read(FREEZE);a=read(AUTH)
    assert x['schema']=='eac-v3-zenodo-frozen-release/1' and x['paper_id']=='EAC-v3.0.0'
    assert a['schema']=='eac-v3-zenodo-authorized/1' and a['paper_id']==x['paper_id']
    assert a['status']=='AUTHORIZED_FOR_ONE_PUBLIC_ZENODO_PREPRINT' and a['deposition_once']
    assert a['owner_instruction']=='Publish EAC-v3.0.0 according to existing repository DOI then OTS then Arweave publication process'
    assert a['expected_manifest_sha256']==sha(FREEZE.read_bytes())
    m=x['metadata']
    assert m['title']=='When the Guardians Can Be Acquired: Joint Protection Across Concurrent and Renewable Authorizations'
    assert m['version']=='3.0.0' and m['publication_date']=='2026-10-12'
    assert m['upload_type']=='publication' and m['publication_type']=='preprint'
    assert m['license']=='cc-by-4.0' and m['access_right']=='open'
    assert m['creators']==[{'name':'Liu, Hongju','affiliation':'Independent Researcher, Shenzhen, China'}]
    listed=[]
    for f in x['files']:
        p=ASSETS/f['name'];assert p.exists() and p.is_file()
        assert p.stat().st_size==f['bytes'] and sha(p.read_bytes())==f['sha256']
        listed.append(f['name'])
    assert len(listed)==6 and len(set(listed))==6
    assert set(p.name for p in ASSETS.iterdir() if p.is_file())==set(listed)
    pdf=ASSETS/x['primary_pdf']
    assert pdf.name=='when-the-guardians-can-be-acquired-eac-v3.0.0.pdf' and sha(pdf.read_bytes())==x['source_pdf_sha256']
    with zipfile.ZipFile(ASSETS/'reproducibility-eac-v3.0.0.zip') as z:
        assert z.testzip() is None and 'EAC-v3.0.0/INDEX.json' in z.namelist()
    info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,check=True)
    assert 'Pages:           12' in info.stdout and 'Encrypted:       no' in info.stdout
    return x

def api(session,method,path,**kw):
    kw.setdefault('timeout',75)
    response=session.request(method,BASE+path,**kw)
    if response.status_code>=400:
        raise RuntimeError(f'Zenodo {method} {path} HTTP {response.status_code}: {response.text[:500]}')
    return response.json() if response.content else {}

def find_existing(session,freeze):
    title=freeze['metadata']['title'];version=freeze['metadata']['version']
    # Personal account depositions include private drafts, not just public records.
    search=api(session,'GET','/deposit/depositions?'+urlencode({'q':'"'+title+'"','size':25}))
    if not isinstance(search,list):raise RuntimeError('Cannot establish exact deposited record uniqueness')
    matches=[x for x in search if x.get('metadata',{}).get('title')==title and
             str(x.get('metadata',{}).get('version'))==version]
    if len(matches)>1:raise RuntimeError('Multiple existing account depositions with identical title and version; human reconciliation required')
    if matches:return matches[0]
    # Search the publicly visible family as well, not only exact subtitle; this
    # protects against earlier versions created outside this repo/account.
    import requests
    stem='When the Guardians Can Be Acquired'
    public=api(requests.Session(),'GET','/records?'+urlencode({'q':'title:"'+stem+'"','size':25}))
    hits=(public.get('hits') or {}).get('hits') or []
    possible=[{'id':r.get('id'),'title':r.get('metadata',{}).get('title'),'version':r.get('metadata',{}).get('version')}
              for r in hits if stem.lower() in (r.get('metadata',{}).get('title') or '').lower()]
    if possible:
        raise RuntimeError('Related Guardians publication already exists; do not create a second first-version DOI automatically: '+json.dumps(possible)[:600])
    return None

def validate_deposit(d,freeze):
    m=d.get('metadata') or {};target=freeze['metadata']
    for key in ('title','version','upload_type','publication_type'):
        if str(m.get(key))!=str(target.get(key)):raise RuntimeError('Existing draft metadata differs: '+key)
    if [x.get('name') for x in (m.get('creators') or [])]!=['Liu, Hongju']:
        raise RuntimeError('Existing draft creator mismatch')

def upload_files(session,dep,freeze,attempt):
    depid=dep['id']
    if not (dep.get('links') or {}).get('bucket','').startswith('https://zenodo.org/api/'):
        raise RuntimeError('Draft has no trusted Zenodo bucket URL')
    result=api(session,'GET',f'/deposit/depositions/{depid}/files')
    entries={x.get('filename'):x for x in result}
    if len(entries)!=len(result) or set(entries)-{x['name'] for x in freeze['files']}:
        raise RuntimeError('Unexpected or duplicate name in retained draft')
    for meta in freeze['files']:
        name=meta['name'];p=ASSETS/name
        digest=hashlib.md5(p.read_bytes()).hexdigest() # Zenodo legacy API checksum
        if name in entries:
            old=entries[name];c=(old.get('checksum') or '').replace('md5:','')
            n=old.get('filesize') or old.get('size')
            if (c and c!=digest) or (n is not None and int(n)!=meta['bytes']):
                raise RuntimeError('Existing draft name has wrong bytes: '+name)
            continue
        with p.open('rb') as f:
            r=session.post(f'{BASE}/deposit/depositions/{depid}/files',data={'name':name},files={'file':(name,f)},timeout=160)
        if r.status_code>=400:raise RuntimeError(f'Upload {name} HTTP {r.status_code}: {r.text[:500]}')
        got=r.json();checked=(got.get('checksum') or '').replace('md5:','')
        if checked and checked!=digest:raise RuntimeError('Draft upload checksum response mismatch: '+name)
        attempt.setdefault('files_uploaded',[]).append(name);save(ATTEMPT,attempt)
    actual=api(session,'GET',f'/deposit/depositions/{depid}/files')
    got={x.get('filename'):x for x in actual};expected={x['name'] for x in freeze['files']}
    if set(got)!=expected or len(got)!=len(actual):raise RuntimeError('Zenodo draft file inventory differs')
    for meta in freeze['files']:
        x=got[meta['name']];n=x.get('filesize') or x.get('size')
        c=(x.get('checksum') or '').replace('md5:','')
        if (n is not None and int(n)!=meta['bytes']) or (c and c!=hashlib.md5((ASSETS/meta['name']).read_bytes()).hexdigest()):
            raise RuntimeError('Zenodo draft byte count/checksum mismatch '+meta['name'])

def public_readback(depid,freeze):
    import requests
    s=requests.Session();record=None
    for attempt in range(9):
        try:
            r=s.get(f'{BASE}/records/{depid}',timeout=40)
            if r.status_code==200:record=r.json();break
        except requests.RequestException:pass
        time.sleep(min(2+attempt,8))
    if record is None:raise RuntimeError('Record not anonymously readable after public publish')
    if int(record.get('id',-1))!=int(depid):raise RuntimeError('Published record id differs')
    doi=record.get('doi') or (record.get('metadata') or {}).get('doi')
    if doi!=f'10.5281/zenodo.{depid}':raise RuntimeError('Published DOI not equal to expected record DOI')
    if (record.get('metadata') or {}).get('title')!=freeze['metadata']['title']:
        raise RuntimeError('Public record title differs')
    publicfiles=record.get('files') or []
    by_name={x.get('key'):x for x in publicfiles}
    if len(by_name)!=len(publicfiles) or set(by_name)!={x['name'] for x in freeze['files']}:
        raise RuntimeError('Public file inventory differs')
    verified=[]
    for f in freeze['files']:
        key=f['name'];remote=by_name[key]
        download=(remote.get('links') or {}).get('self')
        if not download or not download.startswith('https://zenodo.org/'):
            download=f'{BASE}/records/{depid}/files/{quote(key,safe="")}/content'
        if not download.startswith('https://zenodo.org/'):raise RuntimeError('Untrusted asset download domain')
        r=s.get(download,timeout=120)
        if r.status_code!=200 or len(r.content)!=f['bytes'] or sha(r.content)!=f['sha256']:
            raise RuntimeError('Public file readback failed byte SHA-256 '+key)
        verified.append({'name':key,'bytes':len(r.content),'sha256':sha(r.content),'url':download})
    return {'record_id':int(depid),'doi':doi,'record_url':f'https://zenodo.org/records/{depid}','verified_files':verified}

def publish():
    import requests
    frozen=freeze_check()
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:raise RuntimeError('Protected GitHub Actions ZENODO_ACCESS_TOKEN is unavailable; no external write')
    s=requests.Session();s.headers.update({'Authorization':'Bearer '+token})
    state={'schema':'eac-v3-zenodo-attempt/1','status':'STARTED','paper_id':frozen['paper_id'],'manifest_sha256':sha(FREEZE.read_bytes()),'started_utc':now(),'github_run_id':os.environ.get('GITHUB_RUN_ID'),'github_source_commit':os.environ.get('GITHUB_SHA')}
    save(ATTEMPT,state)
    try:
        dep=find_existing(s,frozen)
        if dep:
            validate_deposit(dep,frozen)
            state.update(status='RECOVER_IDENTICAL_DEPOSIT',record_id=dep['id'],deposition_state=dep.get('state'))
        else:
            try:dep=api(s,'POST','/deposit/depositions',json={'metadata':frozen['metadata']})
            except Exception as exc:
                raise RuntimeError('Deposit create response failed/uncertain. Do not rerun until owner deposition list reconciled.') from exc
            state.update(status='DRAFT_CREATED',record_id=dep['id'],deposition_state=dep.get('state'))
        save(ATTEMPT,state)
        depid=dep['id']
        if dep.get('state')!='done':
            upload_files(s,dep,frozen,state)
            state['status']='DRAFT_FILES_MATCH';save(ATTEMPT,state)
            try:
                result=api(s,'POST',f'/deposit/depositions/{depid}/actions/publish')
            except Exception as exc:
                state['status']='PUBLISH_POST_UNCERTAIN';save(ATTEMPT,state)
                try:public=public_readback(depid,frozen)
                except Exception:raise RuntimeError(f'Publish response uncertain for record {depid}; do NOT create another deposit; check existing remote status') from exc
            else:
                state['publish_action_state']=result.get('state')
                public=public_readback(depid,frozen)
        else:public=public_readback(depid,frozen)
        receipt={'schema':'eac-v3-published-and-verified/1','status':'PUBLISHED_PUBLIC_BYTE_READBACK_PASS',
          'paper_id':frozen['paper_id'],'doi':public['doi'],'record_id':depid,'record_url':public['record_url'],
          'published_checked_at_utc':now(),'publication_workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
          'source_commit':os.environ.get('GITHUB_SHA'),
          'manifest_sha256':sha(FREEZE.read_bytes()),'public_files':public['verified_files'],
          'peer_reviewed':False,'ots':'NOT_PERFORMED_IN_THIS_JOB','arweave':'NOT_PERFORMED_IN_THIS_JOB',
          'previous_published_research_papers_modified':False}
        save(RECEIPT,receipt)
        state.update(status=receipt['status'],doi=public['doi'],record_id=depid,file_count=len(public['verified_files']))
        save(ATTEMPT,state)
        print(json.dumps({'status':receipt['status'],'doi':public['doi'],'record_url':public['record_url'],'files_verified':len(public['verified_files'])},indent=2))
    except Exception as e:
        state.update(status='BLOCKED_OR_UNCERTAIN',failed_at_utc=now(),error_type=type(e).__name__,error=str(e)[:850]);save(ATTEMPT,state)
        raise

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','publish'));a=p.parse_args()
    if a.command=='verify':
        x=freeze_check();print('FROZEN ASSETS PRE-FLIGHT PASS:',x['paper_id'],len(x['files']))
    else:publish()
if __name__=='__main__':main()
