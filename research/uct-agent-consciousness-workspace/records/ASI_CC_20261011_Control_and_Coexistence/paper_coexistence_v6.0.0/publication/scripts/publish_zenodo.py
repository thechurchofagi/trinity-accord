#!/usr/bin/env python3
"""One-shot, pinned-asset Zenodo publication for PR-v6.0.0.

Follows existing Trinity Accord publication style: exact frozen checksums, an
explicit owner authorization, protected GitHub Actions credentials, an
idempotency search, then authenticated publish and anonymous exact-byte readback.
The publication code deliberately never prints a token. The script only touches
one exact titled version; after uncertain remote success it must reconcile,
not create a second record. No Arweave charge, and no OTS submission here.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time, zipfile, subprocess
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / 'EXPECTED-PUBLICATION.json'
AUTH = ROOT / 'PUBLISH-AUTHORIZATION.json'
ASSETS = ROOT / 'release'
ATTEMPT = ROOT / 'PUBLICATION-ATTEMPT.json'
RECEIPT = ROOT / 'PUBLICATION-RECEIPT.json'
BASE = 'https://zenodo.org/api'


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def write(path: Path, obj: dict):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)+'\n', encoding='utf-8')


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def utc():
    return datetime.now(timezone.utc).isoformat()


def preflight():
    j=load(FREEZE)
    a=load(AUTH)
    assert j['schema']=='asi-cc-pr6-publication-freeze-v1'
    assert j['paper_id']=='PR-v6.0.0'
    assert a['schema']=='asi-cc-pr6-publish-authorization/1'
    assert a['status']=='AUTHORIZED_FOR_ONE_PUBLIC_ZENODO_PREPRINT'
    assert a['paper_id']==j['paper_id']
    assert a['expected_sha256']==sha256(FREEZE.read_bytes())
    assert a['owner_instruction']=='Publish PR-v6.0.0 DOI, following the repository established workflow'
    m=j['metadata']
    assert m['title']=='Safe Revocation Without Complete Diagnosis: Exact Resource Frontiers under Coupled Faults for Subjecthood-Agnostic AI Coexistence'
    assert m['version']=='6.0.0'
    assert m['license']=='cc-by-4.0'
    assert m['upload_type']=='publication' and m['publication_type']=='preprint'
    assert m['creators']==[{'name':'Liu, Hongju','affiliation':'Independent Researcher, Shenzhen, China'}]
    found=[]
    for spec in j['files']:
        p=ASSETS/spec['name']
        assert p.is_file(),f'Missing frozen asset {p}'
        assert p.stat().st_size==spec['bytes'],f'Wrong bytes: {p}'
        assert sha256(p.read_bytes())==spec['sha256'],f'Wrong SHA: {p}'
        found.append(spec['name'])
    assert len(found)==j['file_count']==len(set(found))
    assert set(x.name for x in ASSETS.iterdir() if x.is_file())==set(found)
    pdf=ASSETS/'safe-revocation-without-complete-diagnosis-pr-v6.0.0.pdf'
    assert sha256(pdf.read_bytes())==j['source_pdf_sha256']
    with zipfile.ZipFile(ASSETS/'reproducibility-pr-v6.0.0.zip') as z:
        assert z.testzip() is None
        assert 'PR-v6.0.0/INDEX.json' in z.namelist()
    check=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,check=True)
    assert 'Pages:           14' in check.stdout
    return j


def api(session, method, path, **kwargs):
    import requests
    url=BASE+path
    kwargs.setdefault('timeout',75)
    r=session.request(method,url,**kwargs)
    if r.status_code >=400:
        # Never print headers (contain bearer token). Body may contain errors.
        raise RuntimeError(f'Zenodo {method} {path} status={r.status_code}; error={r.text[:500]!r}')
    return r.json() if r.content else {}


def own_depositions(session,title,version):
    from urllib.parse import urlencode
    params={'q':'"'+title+'"','size':100}
    # The authenticated depositions endpoint includes unfinished drafts.
    rows=api(session,'GET','/deposit/depositions?'+urlencode(params))
    if not isinstance(rows,list):
        raise RuntimeError('Authenticated deposit list was not an array; cannot rule out duplicates')
    matches=[x for x in rows if x.get('metadata',{}).get('title')==title
             and str(x.get('metadata',{}).get('version',''))==version]
    if len(matches)>1:raise RuntimeError('Ambiguous duplicate exact title/version in owner account')
    return matches


def verify_metadata(dep,freeze):
    m=dep.get('metadata') or {}
    f=freeze['metadata']
    for k in ('title','version','upload_type','publication_type'):
        if m.get(k)!=f[k]:raise RuntimeError(f'Deposit metadata mismatch: {k} ({m.get(k)!r})')
    expected=f['creators'][0]
    rows=m.get('creators') or []
    if len(rows)!=1 or rows[0].get('name')!=expected['name']:
        raise RuntimeError('Deposit creator mismatch')


def upload_exact(session,dep,freeze,attempt):
    # Traditional Zenodo deposition API returns a bucket URL.
    import requests
    bucket=(dep.get('links') or {}).get('bucket')
    if not bucket or not bucket.startswith('https://zenodo.org/api/'):
        raise RuntimeError('No trusted Zenodo bucket link in deposition')
    existing=api(session,'GET',f"/deposit/depositions/{dep['id']}/files")
    by_name={x.get('filename'):x for x in existing}
    if len(by_name)!=len(existing):raise RuntimeError('Duplicate filename in remote draft')
    expected_names={f['name'] for f in freeze['files']}
    if any(x not in expected_names for x in by_name):raise RuntimeError('Unexpected file in matching remote draft')
    for f in freeze['files']:
        name=f['name']
        b=(ASSETS/name).read_bytes()
        md5=hashlib.md5(b).hexdigest() # Zenodo legacy draft checksum is MD5.
        if name in by_name:
            row=by_name[name]
            s=row.get('filesize') or row.get('size')
            chk=(row.get('checksum') or '').replace('md5:','')
            if s is not None and int(s)!=f['bytes']:raise RuntimeError(f'Existing draft file wrong size: {name}')
            if chk and chk!=md5:raise RuntimeError(f'Existing draft file wrong checksum: {name}')
            attempt.setdefault('files_confirmed',[]).append(name)
            continue
        # Use legacy API's multipart upload for portability across draft endpoints.
        with (ASSETS/name).open('rb') as source:
            resp=session.post(f"{BASE}/deposit/depositions/{dep['id']}/files",
                              data={'name':name},files={'file':(name,source)},timeout=160)
        if resp.status_code>=400:
            raise RuntimeError(f'Zenodo upload {name} status={resp.status_code} body={resp.text[:400]!r}')
        answer=resp.json()
        chk=(answer.get('checksum') or '').replace('md5:','')
        if chk and chk!=md5:raise RuntimeError(f'Upload returned wrong checksum {name}')
        attempt.setdefault('files_uploaded',[]).append(name)
        write(ATTEMPT,attempt)
    files=api(session,'GET',f"/deposit/depositions/{dep['id']}/files")
    got={f.get('filename'):f for f in files}
    if set(got)!=expected_names:raise RuntimeError(f'Remote file inventory incomplete: {sorted(got)}')
    for spec in freeze['files']:
        row=got[spec['name']]
        md5=hashlib.md5((ASSETS/spec['name']).read_bytes()).hexdigest()
        remote=(row.get('checksum') or '').replace('md5:','')
        if remote and remote!=md5:raise RuntimeError('Draft file content mismatch for '+spec['name'])
        n=row.get('filesize') or row.get('size')
        if n is not None and int(n)!=spec['bytes']:raise RuntimeError('Draft file length mismatch for '+spec['name'])


def anonymous_readback(record_id,freeze):
    import requests
    request=requests.Session()
    record=None
    for i in range(8):
        try:
            result=request.get(f'{BASE}/records/{record_id}',timeout=40)
            if result.status_code==200:
                record=result.json()
                break
        except requests.RequestException:
            pass
        time.sleep(min(i+1,8))
    if not record:raise RuntimeError('Published record not available for anonymous public readback')
    if record.get('id')!=record_id:raise RuntimeError('Public record id mismatched')
    doi=record.get('doi') or record.get('metadata',{}).get('doi')
    if not doi or doi!=f'10.5281/zenodo.{record_id}':raise RuntimeError('Public DOI mismatch or unassigned')
    if record.get('metadata',{}).get('title')!=freeze['metadata']['title']:
        raise RuntimeError('Public title differs from frozen title')
    entries=record.get('files') or []
    by_name={x.get('key'):x for x in entries}
    if set(by_name)!={f['name'] for f in freeze['files']}:
        raise RuntimeError('Public file inventory mismatch')
    verified=[]
    for spec in freeze['files']:
        name=spec['name'];f=by_name[name]
        link=(f.get('links') or {}).get('self')
        if not link or not link.startswith('https://zenodo.org/'):
            link=f'{BASE}/records/{record_id}/files/{quote(name,safe="")}/content'
        if not link.startswith('https://zenodo.org/'):
            raise RuntimeError('Untrusted download host for '+name)
        r=request.get(link,timeout=110)
        if r.status_code!=200:raise RuntimeError(f'Public {name} readback HTTP {r.status_code}')
        if len(r.content)!=spec['bytes'] or sha256(r.content)!=spec['sha256']:
            raise RuntimeError(f'Public {name} not identical to frozen bytes')
        verified.append({'name':name,'bytes':len(r.content),'sha256':sha256(r.content),'url':link})
    return {'record_id':record_id,'doi':doi,'record_url':f'https://zenodo.org/records/{record_id}',
      'public_title':record['metadata']['title'],'verified_files':verified,'record_metadata':record['metadata']}


def publish():
    import requests
    freeze=preflight()
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:raise RuntimeError('ZENODO_ACCESS_TOKEN unavailable in protected workflow; no Zenodo write')
    session=requests.Session();session.headers.update({'Authorization':'Bearer '+token})
    # Public search is just a first safety gate. The authenticated account list is decisive.
    title=freeze['metadata']['title'];version=freeze['metadata']['version']
    attempt={'schema':'asi-cc-pr6-publication-attempt/1','phase':'STARTED','paper_id':freeze['paper_id'],
      'expected_manifest_sha256':sha256(FREEZE.read_bytes()),'started_at_utc':utc(),
      'trigger_commit':os.environ.get('GITHUB_SHA'),'runtime_run_id':os.environ.get('GITHUB_RUN_ID')}
    write(ATTEMPT,attempt)
    try:
        match=own_depositions(session,title,version)
        if match:
            dep=match[0];verify_metadata(dep,freeze)
            attempt.update({'phase':'RECOVER_EXISTING_DEPOSIT','record_id':dep['id'],'state':dep.get('state')})
        else:
            # A second public title match (perhaps on another account) requires inspection.
            from urllib.parse import urlencode
            public=api(requests.Session(),'GET','/records?'+urlencode({'q':'title:"'+title+'"','size':25}))
            hits=((public.get('hits') or {}).get('hits') or [])
            same=[x for x in hits if x.get('metadata',{}).get('title')==title and
                  str(x.get('metadata',{}).get('version',''))==version]
            if same:
                raise RuntimeError('Identical already-public title/version exists; abort automatic duplicate publication')
            dep=api(session,'POST','/deposit/depositions',json={'metadata':freeze['metadata']})
            attempt.update({'phase':'DRAFT_CREATED','record_id':dep['id'],'state':dep.get('state')})
        write(ATTEMPT,attempt)
        record_id=dep['id']
        if dep.get('state')!='done':
            upload_exact(session,dep,freeze,attempt)
            attempt.update({'phase':'FILES_STAGED_AND_CHECKED','state':dep.get('state')})
            write(ATTEMPT,attempt)
            # No automatic retry of publication POST. If ambiguous, recover by reading.
            try:
                dep=api(session,'POST',f'/deposit/depositions/{record_id}/actions/publish')
            except Exception as ex:
                attempt.update({'phase':'PUBLISH_RESPONSE_UNCERTAIN','error':str(ex)[:700]})
                write(ATTEMPT,attempt)
                # Always attempt public readback before deciding whether publish succeeded.
                try:
                    public=anonymous_readback(record_id,freeze)
                    attempt['phase']='PUBLISHED_RECOVERED_BY_PUBLIC_READBACK'
                except Exception:
                    raise RuntimeError('Publish POST uncertain; deposit id recorded for manual recovery; DO NOT CREATE ANOTHER DRAFT') from ex
            else:
                attempt.update({'phase':'PUBLISHED_POST_RETURNED','state':dep.get('state'),'doi':dep.get('doi')})
                write(ATTEMPT,attempt)
                public=anonymous_readback(record_id,freeze)
        else:
            public=anonymous_readback(record_id,freeze)
        receipt={'schema':'asi-cc-pr6-published-and-readback/1','status':'PUBLISHED_PUBLIC_BYTE_READBACK_PASS',
          'paper_id':freeze['paper_id'],'published_at_utc':utc(),
          'doi':public['doi'],'record_id':record_id,'record_url':public['record_url'],
          'expected_manifest_sha256':sha256(FREEZE.read_bytes()),
          'publication_workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
          'source_commit':os.environ.get('GITHUB_SHA'),
          'files':public['verified_files'],'authenticated_readback':False,
          'peer_reviewed':False,'no_new_AI_experiment':True,
          'ots':'NOT_EXECUTED_IN_THIS_WORKFLOW','arweave':'NOT_EXECUTED_IN_THIS_WORKFLOW'}
        write(RECEIPT,receipt)
        attempt.update({'phase':'PUBLISHED_PUBLIC_BYTE_READBACK_PASS','doi':public['doi'],
                        'verified_count':len(public['verified_files'])})
        write(ATTEMPT,attempt)
        print(json.dumps({'status':receipt['status'],'doi':receipt['doi'],
                          'record_url':receipt['record_url'],'file_count':len(receipt['files'])},indent=2))
    except Exception as e:
        attempt['failed_at_utc']=utc();attempt['exception_type']=type(e).__name__
        attempt['error']=str(e)[:700]
        write(ATTEMPT,attempt)
        raise


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('verify','publish'))
    args=parser.parse_args()
    if args.action=='verify':
        f=preflight();print('FROZEN PRE-FLIGHT PASS:',f['paper_id'],f['file_count'],'files')
    else:publish()

if __name__=='__main__':main()
