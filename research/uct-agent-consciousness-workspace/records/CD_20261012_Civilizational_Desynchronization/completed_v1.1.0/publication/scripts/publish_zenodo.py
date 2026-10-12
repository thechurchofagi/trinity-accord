#!/usr/bin/env python3
"""One authorized, frozen CD-v1.1.0 Zenodo preprint publication.

No credential material is printed. All 6 original assets are verified before and
independently after publishing. An ambiguous remote POST is NEVER blindly retried;
reconcile the exact title/version/deposition id before another operation.
OTS and paid Arweave are separate publication-preservation steps.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time,zipfile
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlencode,quote

ROOT=Path(__file__).resolve().parents[1]
FREEZE=ROOT/'EXPECTED-PUBLICATION.json';AUTH=ROOT/'PUBLISH-AUTHORIZATION.json'
ASSETS=ROOT/'release';ATTEMPT=ROOT/'PUBLICATION-ATTEMPT.json';RECEIPT=ROOT/'PUBLICATION-RECEIPT.json'
BASE='https://zenodo.org/api'


def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def md5(b:bytes)->str:return hashlib.md5(b).hexdigest()
def load(p:Path):return json.loads(p.read_text(encoding='utf-8'))
def save(p:Path,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def utc():return datetime.now(timezone.utc).isoformat()


def preflight():
    freeze=load(FREEZE);auth=load(AUTH)
    assert freeze['schema']=='cd-v110-zenodo-publication-freeze/1'
    assert freeze['paper_id']=='CD-v1.1.0' and freeze['file_count']==6
    assert auth['schema']=='cd-v110-zenodo-authorization/1'
    assert auth['paper_id']==freeze['paper_id'] and auth['status']=='AUTHORIZED_FOR_ONE_PUBLIC_ZENODO_PREPRINT'
    assert auth['once'] is True and auth['expected_manifest_sha256']==sha(FREEZE.read_bytes())
    assert auth['owner_instruction']=='Publish CD-v1.1.0 according to Trinity Accord repository workflow'
    assert auth['no_OTS_or_Arweave_in_this_step'] is True
    m=freeze['metadata']
    assert m['title']=='Awareness Can Catch Up After Choice Has Closed: Uneven Readiness, Effective Reconsideration, and Civilizational Desynchronization in AI Transitions'
    assert m['version']=='1.1.0' and m['upload_type']=='publication' and m['publication_type']=='preprint'
    assert m['license']=='cc-by-4.0' and m['publication_date']=='2026-10-12'
    assert m['creators']==[{'name':'Liu, Hongju','affiliation':'Independent Researcher, Shenzhen, China'}]
    names=[x['name'] for x in freeze['files']]
    assert len(names)==len(set(names))==6
    assert set(names)=={x.name for x in ASSETS.iterdir() if x.is_file()}
    for x in freeze['files']:
        d=(ASSETS/x['name']).read_bytes()
        assert len(d)==x['bytes'] and sha(d)==x['sha256'],f'Frozen asset mismatch {x["name"]}'
    pdf=ASSETS/freeze['primary_pdf'];assert pdf.read_bytes().startswith(b'%PDF-')
    assert sha(pdf.read_bytes())==freeze['source_pdf_sha256']
    zpath=ASSETS/'reproducibility-cd-v1.1.0.zip'
    assert sha(zpath.read_bytes())==freeze['research_package_sha256']
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        assert z.read('CD-v1.1.0/paper/manuscript.pdf')==pdf.read_bytes()
        assert z.read('CD-v1.1.0/paper/manuscript.tex')==(ASSETS/'awareness-can-catch-up-after-choice-has-closed-cd-v1.1.0.tex').read_bytes()
        assert len(z.namelist())==27
    inf=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,check=True)
    assert 'Pages:           12' in inf.stdout
    return freeze


def api(session,method,path,**kwargs):
    url=BASE+path
    response=session.request(method,url,timeout=kwargs.pop('timeout',80),**kwargs)
    if response.status_code>=400:
        raise RuntimeError(f'Zenodo {method} {path} HTTP {response.status_code}; response {response.text[:550]!r}')
    return response.json() if response.content else {}


def exact_owner_record(session,freeze):
    title=freeze['metadata']['title'];version=freeze['metadata']['version']
    q=urlencode({'q':'"'+title+'"','size':100})
    matches=api(session,'GET','/deposit/depositions?'+q)
    if not isinstance(matches,list):raise RuntimeError('Cannot assess owner record duplicates')
    same=[m for m in matches if (m.get('metadata') or {}).get('title')==title and str((m.get('metadata') or {}).get('version',''))==version]
    if len(same)>1:raise RuntimeError('Multiple owner deposits with exact title and version; manual recovery required')
    return same[0] if same else None


def public_exact_title_match(freeze):
    import requests
    title=freeze['metadata']['title'];version=freeze['metadata']['version']
    # Public Zenodo searches cap unauthenticated page size at 25.
    q=urlencode({'q':'title:"'+title+'"','size':25})
    body=api(requests.Session(),'GET','/records?'+q)
    block=body.get('hits') or {}
    rows=(block.get('hits') or [])
    total=block.get('total',len(rows))
    if isinstance(total,dict):total=total.get('value',len(rows))
    if int(total)>len(rows):
        raise RuntimeError('Unexamined public search pages; inspect before publication, do not create a duplicate')
    return [x for x in rows if (x.get('metadata') or {}).get('title')==title and str((x.get('metadata') or {}).get('version',''))==version]


def validate_remote_metadata(dep,freeze):
    m=dep.get('metadata') or {};f=freeze['metadata']
    for k in ('title','version','upload_type','publication_type'):
        if m.get(k)!=f[k]:raise RuntimeError('Zenodo existing record metadata mismatch: '+k)
    c=m.get('creators') or []
    if len(c)!=1 or c[0].get('name')!=f['creators'][0]['name']:
        raise RuntimeError('Zenodo creator mismatch; stop before upload')


def stage_files(session,dep,freeze,attempt):
    bucket=(dep.get('links') or {}).get('bucket')
    if not bucket or not bucket.startswith(BASE+'/'):
        raise RuntimeError('Missing trusted Zenodo bucket URL')
    rows=api(session,'GET',f"/deposit/depositions/{dep['id']}/files")
    if not isinstance(rows,list):raise RuntimeError('Cannot retrieve remote draft files')
    by={x.get('filename'):x for x in rows}
    if len(rows)!=len(by):raise RuntimeError('Ambiguous duplicate filenames in existing draft')
    expected={x['name'] for x in freeze['files']}
    if set(by)-expected:raise RuntimeError('Unknown preexisting files in matching Zenodo draft')
    for spec in freeze['files']:
        name=spec['name'];content=(ASSETS/name).read_bytes()
        if name in by:
            row=by[name];got=(row.get('checksum') or '').replace('md5:','');size=row.get('filesize',row.get('size'))
            if got and got!=md5(content):raise RuntimeError('Existing draft file checksum mismatch '+name)
            if size is not None and int(size)!=spec['bytes']:raise RuntimeError('Existing draft file size mismatch '+name)
            continue
        with (ASSETS/name).open('rb') as f:
            r=session.post(BASE+f"/deposit/depositions/{dep['id']}/files",data={'name':name},files={'file':(name,f)},timeout=180)
        if r.status_code>=400:raise RuntimeError(f'Upload {name} status={r.status_code} {r.text[:500]!r}')
        answer=r.json();sum_=(answer.get('checksum') or '').replace('md5:','')
        if sum_ and sum_!=md5(content):raise RuntimeError('Zenodo immediate upload checksum mismatch '+name)
        attempt.setdefault('files_uploaded',[]).append(name);save(ATTEMPT,attempt)
    rows=api(session,'GET',f"/deposit/depositions/{dep['id']}/files")
    got={x.get('filename'):x for x in rows}
    if set(got)!=expected:raise RuntimeError('Remote inventory differs from exact frozen file set')
    for spec in freeze['files']:
        name=spec['name'];row=got[name];b=(ASSETS/name).read_bytes()
        chk=(row.get('checksum') or '').replace('md5:','');size=row.get('filesize',row.get('size'))
        if chk and chk!=md5(b):raise RuntimeError('Remote draft MD5 mismatch '+name)
        if size is not None and int(size)!=spec['bytes']:raise RuntimeError('Remote draft size mismatch '+name)


def anonymous_readback(record_id,freeze):
    import requests
    session=requests.Session();record=None
    for i in range(9):
        try:
            r=session.get(BASE+f'/records/{record_id}',timeout=40)
            if r.status_code==200:record=r.json();break
        except requests.RequestException:pass
        time.sleep(min(i+1,8))
    if not record:raise RuntimeError('Published record not publicly readable yet')
    doi=record.get('doi') or (record.get('metadata') or {}).get('doi')
    if record.get('id')!=record_id or doi!=f'10.5281/zenodo.{record_id}':raise RuntimeError('DOI and record ID differ from expected new record')
    if (record.get('metadata') or {}).get('title')!=freeze['metadata']['title']:
        raise RuntimeError('Public Zenodo title mismatch')
    rows=record.get('files') or []
    by={x.get('key'):x for x in rows};expected={x['name'] for x in freeze['files']}
    if set(by)!=expected or len(rows)!=len(expected):raise RuntimeError('Public file inventory mismatch')
    verified=[]
    for spec in freeze['files']:
        name=spec['name'];item=by[name]
        link=(item.get('links') or {}).get('self')
        if not link or not link.startswith('https://zenodo.org/'):
            link=BASE+f'/records/{record_id}/files/{quote(name,safe="")}/content'
        if not link.startswith('https://zenodo.org/'):
            raise RuntimeError('Unexpected remote file host')
        r=session.get(link,timeout=130)
        if r.status_code!=200 or len(r.content)!=spec['bytes'] or sha(r.content)!=spec['sha256']:
            raise RuntimeError('Anonymous public file readback failed '+name)
        verified.append({'name':name,'bytes':spec['bytes'],'sha256':spec['sha256'],'url':link})
    return {'record_id':record_id,'doi':doi,'record_url':f'https://zenodo.org/records/{record_id}', 'verified':verified}


def publish():
    import requests
    freeze=preflight()
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:raise RuntimeError('Protected ZENODO_ACCESS_TOKEN unavailable; NO remote publication attempted')
    s=requests.Session();s.headers.update({'Authorization':'Bearer '+token})
    attempt={'schema':'cd-v110-zenodo-publication-attempt/1','paper_id':'CD-v1.1.0',
      'phase':'STARTED','started_at_utc':utc(),'frozen_manifest_sha256':sha(FREEZE.read_bytes()),
      'github_sha':os.environ.get('GITHUB_SHA'),'github_run_id':os.environ.get('GITHUB_RUN_ID')}
    save(ATTEMPT,attempt)
    try:
        dep=exact_owner_record(s,freeze)
        if dep:
            validate_remote_metadata(dep,freeze)
            attempt.update(phase='FOUND_EXACT_OWNER_DEPOSIT',record_id=dep['id'],state=dep.get('state'))
        else:
            if public_exact_title_match(freeze):
                raise RuntimeError('Exact public record already exists; stop to avoid duplicate DOI')
            dep=api(s,'POST','/deposit/depositions',json={'metadata':freeze['metadata']})
            attempt.update(phase='DRAFT_CREATED',record_id=dep['id'],state=dep.get('state'))
        save(ATTEMPT,attempt)
        record_id=dep['id']
        if dep.get('state')!='done':
            stage_files(s,dep,freeze,attempt)
            attempt.update(phase='STAGED_ALL_FROZEN_BYTES');save(ATTEMPT,attempt)
            try:dep=api(s,'POST',f'/deposit/depositions/{record_id}/actions/publish')
            except Exception as ex:
                attempt.update(phase='PUBLISH_POST_AMBIGUOUS',error_type=type(ex).__name__,error=str(ex)[:600]);save(ATTEMPT,attempt)
                try:public=anonymous_readback(record_id,freeze)
                except Exception:
                    raise RuntimeError('Zenodo publish response uncertain: DO NOT CREATE ANOTHER DEPOSIT. Reconcile existing record id '+str(record_id)) from ex
                attempt['phase']='PUBLISHED_RECOVERED_BY_PUBLIC_READBACK'
            else:
                attempt.update(phase='PUBLISH_POST_RETURNED',state=dep.get('state'));save(ATTEMPT,attempt)
                public=anonymous_readback(record_id,freeze)
        else:
            public=anonymous_readback(record_id,freeze)
        receipt={'schema':'cd-v110-zenodo-public-byte-readback/1','status':'PUBLISHED_PUBLIC_BYTE_READBACK_PASS',
          'paper_id':'CD-v1.1.0','record_id':public['record_id'],'doi':public['doi'],'record_url':public['record_url'],
          'published_checked_at_utc':utc(),'public_files':public['verified'],
          'source_commit':os.environ.get('GITHUB_SHA'),'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
          'manifest_sha256':sha(FREEZE.read_bytes()),'peer_reviewed':False,'prior_publications_unchanged':True,
          'ots':'NOT_PERFORMED_IN_THIS_JOB','arweave':'NOT_PERFORMED_IN_THIS_JOB'}
        save(RECEIPT,receipt)
        attempt.update(phase='PUBLISHED_PUBLIC_BYTE_READBACK_PASS',doi=public['doi'],record_id=public['record_id'],verified_files=len(public['verified']))
        save(ATTEMPT,attempt)
        print(json.dumps({'state':receipt['status'],'doi':receipt['doi'],'record':receipt['record_url'],'file_count':len(receipt['public_files'])},indent=2))
    except Exception as exc:
        attempt['error_type']=type(exc).__name__;attempt['error']=str(exc)[:700];attempt['failed_at_utc']=utc()
        save(ATTEMPT,attempt)
        raise


def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['verify','publish']);a=p.parse_args()
    if a.operation=='verify':
        f=preflight();print('FROZEN_PREFLIGHT_PASS',f['paper_id'],f['file_count'])
    else:publish()

if __name__=='__main__':main()
